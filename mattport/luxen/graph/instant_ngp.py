"""
Implementation of Instant NGP.
"""

from torch import nn

from mattport.luxen.field_modules.encoding import HashEncoding, LuxenEncoding
from mattport.luxen.field_modules.mlp import MLP
from mattport.luxen.graph.vanilla_luxen import LuxenField, LuxenGraph


class NGPField(LuxenField):
    """Luxen module"""

    def __init__(self, num_layers=3, layer_width=64) -> None:
        super().__init__(num_layers=num_layers, layer_width=layer_width)

    def build_encodings(self):
        self.encoding_xyz = HashEncoding()
        self.encoding_dir = LuxenEncoding(
            in_dim=3, num_frequencies=4, min_freq_exp=0.0, max_freq_exp=4.0, include_input=True
        )

    def build_mlp_base(self):
        self.mlp_base = MLP(
            in_dim=self.encoding_xyz.get_out_dim(),
            out_dim=self.layer_width,
            num_layers=self.num_layers,
            layer_width=self.layer_width,
            activation=nn.ReLU(),
        )


class NGPGraph(LuxenGraph):
    """Luxen-W graph"""

    def __init__(self, intrinsics=None, camera_to_world=None, **kwargs) -> None:
        super().__init__(intrinsics=intrinsics, camera_to_world=camera_to_world, **kwargs)

    def populate_fields(self):
        """Set the fields."""
        self.field_coarse = NGPField()
        self.field_fine = NGPField()
