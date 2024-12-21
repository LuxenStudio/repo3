from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
from torch import nn
from torch.nn.parameter import Parameter
from torchtyping import TensorType

from luxenstudio.cameras.rays import RaySamples
from luxenstudio.data.scene_box import SceneBox
from luxenstudio.field_components.activations import trunc_exp
from luxenstudio.field_components.field_heads import FieldHeadNames
from luxenstudio.field_components.spatial_distortions import (
    SceneContraction,
    SpatialDistortion,
)
from luxenstudio.fields.base_field import Field

try:
    import tinycudann as tcnn
except ImportError:
    pass


class LERFField(Field):
    def __init__(self, clip_n_dims: int, spatial_distortion: SpatialDistortion = SceneContraction()):
        super().__init__()

        self.spatial_distortion = spatial_distortion
        self.clip_encs = torch.nn.ModuleList([
            LERFField._get_encoding( 16, 128, 12, indim=3), 
            LERFField._get_encoding(128, 512, 12, indim=3)
            ])
        tot_out_dims = sum([e.n_output_dims for e in self.clip_encs])

        self.clip_net = tcnn.Network(
            n_input_dims=tot_out_dims + 1,
            n_output_dims=clip_n_dims,
            network_config={
                "otype": "CutlassMLP",
                "activation": "ReLU",
                "output_activation": "None",
                "n_neurons": 256,
                "n_hidden_layers": 4,
            },
        )

        self.dino_net = tcnn.Network(
            n_input_dims=tot_out_dims,
            n_output_dims=384,
            network_config={
                "otype": "CutlassMLP",
                "activation": "ReLU",
                "output_activation": "None",
                "n_neurons": 256,
                "n_hidden_layers": 1,
            },
        )

    @staticmethod
    def _get_encoding(start_res, end_res, levels, indim=3):
        growth = np.exp((np.log(end_res) - np.log(start_res)) / (levels - 1))
        enc = tcnn.Encoding(
            n_input_dims=indim,
            encoding_config={
                "otype": "HashGrid",
                "n_levels": levels,
                "n_features_per_level": 8,
                "log2_hashmap_size": 19,
                "base_resolution": start_res,
                "per_level_scale": growth,
            },
        )
        return enc

    def get_outputs(self, ray_samples: RaySamples, clip_scales):
        # random scales, one scale
        outputs = {}

        positions = ray_samples.frustums.get_positions().detach()
        positions = self.spatial_distortion(positions)
        positions = (positions + 2.0) / 4.0

        xs = [e(positions.view(-1, 3)) for e in self.clip_encs]
        x = torch.concat(xs, dim=-1)

        outputs[FieldHeadNames.HASHGRID] = x.view(*ray_samples.frustums.shape, -1)

        clip_pass = self.clip_net(torch.cat([x, clip_scales.view(-1, 1)], dim=-1)).view(*ray_samples.frustums.shape, -1)
        outputs[FieldHeadNames.CLIP] = clip_pass / clip_pass.norm(dim=-1, keepdim=True)

        dino_pass = self.dino_net(x).view(*ray_samples.frustums.shape, -1)
        outputs[FieldHeadNames.DINO] = dino_pass

        return outputs

    def get_output_from_hashgrid(self, ray_samples: RaySamples, hashgrid_field, scale):
        # designated scales, run outputs for each scale
        hashgrid_field = hashgrid_field.view(-1, self.clip_net.n_input_dims - 1)
        clip_pass = self.clip_net(torch.cat([hashgrid_field, scale.view(-1, 1)], dim=-1)).view(
            *ray_samples.frustums.shape, -1
        )
        output = clip_pass / clip_pass.norm(dim=-1, keepdim=True)

        return output
