# Copyright 2022 The Luxenstudio Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
DreamTensor field implementations using tiny-cuda-nn, torch, ....
"""


from typing import Dict, Optional, Tuple

import numpy as np
import torch
from torch.nn.parameter import Parameter
from torchtyping import TensorType

from luxenstudio.cameras.rays import RayBundle, RaySamples
from luxenstudio.data.scene_box import SceneBox
from luxenstudio.field_components.activations import trunc_exp
from luxenstudio.field_components.encodings import Encoding, Identity, SHEncoding
from luxenstudio.field_components.field_heads import FieldHeadNames
from luxenstudio.fields.base_field import Field, shift_directions_for_tcnn
from luxenstudio.fields.tensorf_field import TensoRFField
try:
    import tinycudann as tcnn
except ImportError:
    # tinycudann module doesn't exist
    pass

def get_normalized_directions(directions: TensorType["bs":..., 3]):
    """SH encoding must be in the range [0, 1]

    Args:
        directions: batch of directions
    """
    return (directions + 1.0) / 2.0


class DreamFusionTensorField(TensoRFField):
    """TCNN implementation of the Instant-NGP field.

    Args:
        aabb: parameters of scene aabb bounds
        num_layers: number of hidden layers
        hidden_dim: dimension of hidden layers
        geo_feat_dim: output geo feat dimensions
        num_layers_color: number of hidden layers for color network
        hidden_dim_color: dimension of hidden layers for color network
        use_appearance_embedding: whether to use appearance embedding
        num_images: number of images, required if use_appearance_embedding is True
        appearance_embedding_dim: dimension of appearance embedding
        contraction_type: type of contraction
        num_levels: number of levels of the hashmap for the base mlp
        log2_hashmap_size: size of the hashmap for the base mlp
        max_res: maximum resolution of the hashmap for the base mlp
    """

    def __init__(
        self,
        aabb: TensorType,
        feature_encoding: Encoding = Identity(in_dim=3),
        direction_encoding: Encoding = Identity(in_dim=3),
        density_encoding: Encoding = Identity(in_dim=3),
        color_encoding: Encoding = Identity(in_dim=3),
        appearance_dim: int = 27,
        head_mlp_num_layers: int = 2,
        head_mlp_layer_width: int = 128,
        use_sh: bool = False,
        sh_levels: int = 2,
    ) -> None:
        super().__init__(
            aabb,
            feature_encoding,
            direction_encoding,
            density_encoding,
            color_encoding,
            appearance_dim,
            head_mlp_num_layers,
            head_mlp_layer_width,
            use_sh,
            sh_levels
        )

        self.bg_direction_encoding = tcnn.Encoding(
            n_input_dims=3,
            encoding_config={
                "otype": "SphericalHarmonics",
                "degree": 4,
            },
        )

        self.mlp_background_color = tcnn.Network(
            n_input_dims=self.bg_direction_encoding.n_output_dims,
            n_output_dims=3,
            network_config={
                "otype": "FullyFusedMLP",
                "activation": "ReLU",
                "output_activation": "Sigmoid",
                "n_neurons": 32,
                "n_hidden_layers": 1,
            },
        )

    def get_background_rgb(self, ray_bundle: RayBundle):
        """Predicts background colors at infinity."""
        directions = get_normalized_directions(ray_bundle.directions)

        outputs_shape = ray_bundle.directions.shape[:-1]
        directions_flat = self.bg_direction_encoding(directions.view(-1, 3))
        background_rgb = self.mlp_background_color(directions_flat).view(*outputs_shape, -1).to(directions)

        return background_rgb