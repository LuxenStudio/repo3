"""
Implementation of vanilla luxen.
"""


from typing import Dict, List

import torch
from torch import nn
from torch.nn import Parameter
from torchtyping import TensorType

from mattport.luxen.field_modules.encoding import LuxenEncoding
from mattport.luxen.field_modules.field_heads import (DensityFieldHead,
                                                     FieldHeadNames,
                                                     RGBFieldHead)
from mattport.luxen.field_modules.mlp import MLP
from mattport.luxen.field_modules.ray_generator import RayGenerator
from mattport.luxen.graph.base import Graph
from mattport.luxen.loss import MSELoss
from mattport.luxen.renderers import RGBRenderer
from mattport.luxen.sampler import PDFSampler, UniformSampler
from mattport.structures.rays import RaySamples


class LuxenField(nn.Module):
    """Luxen module"""

    def __init__(self) -> None:
        super().__init__()
        self.encoding_xyz = LuxenEncoding(in_dim=3, num_frequencies=10, min_freq_exp=0.0, max_freq_exp=8.0)
        self.encoding_dir = LuxenEncoding(in_dim=3, num_frequencies=6, min_freq_exp=0.0, max_freq_exp=4.0)
        self.mlp_base = MLP(
            in_dim=self.encoding_xyz.get_out_dim(), out_dim=64, num_layers=8, layer_width=64, activation=nn.ReLU()
        )
        self.mlp_rgb = MLP(
            in_dim=self.mlp_base.get_out_dim() + self.encoding_dir.get_out_dim(),
            out_dim=64,
            num_layers=2,
            layer_width=64,
            activation=nn.ReLU(),
        )
        self.field_output_rgb = RGBFieldHead(in_dim=self.mlp_rgb.get_out_dim())
        self.field_output_density = DensityFieldHead(in_dim=self.mlp_base.get_out_dim())

    def forward(self, ray_samples: RaySamples):
        """Evaluates the field at points along the ray
        Args:
            xyz: ()
        # TODO(ethan): change the input to be something more abstracted
        e.g., a FieldInput structure
        """
        positions = ray_samples.positions
        directions = ray_samples.directions
        encoded_xyz = self.encoding_xyz(positions)
        encoded_dir = self.encoding_dir(directions)
        base_mlp_out = self.mlp_base(encoded_xyz)
        rgb_mlp_out = self.mlp_rgb(torch.cat([encoded_dir, base_mlp_out], dim=-1))

        field_rgb_output = self.field_output_rgb(rgb_mlp_out)
        field_density_out = self.field_output_density(base_mlp_out)

        field_outputs = field_rgb_output | field_density_out
        return field_outputs


class LuxenGraph(Graph):
    """Vanilla Luxen graph"""

    def __init__(self, intrinsics=None, camera_to_world=None) -> None:
        super().__init__(intrinsics=intrinsics, camera_to_world=camera_to_world)

    def populate_modules(self):
        # ray generator
        self.ray_generator = RayGenerator(self.intrinsics, self.camera_to_world)

        # samplers
        self.sampler_uniform = UniformSampler(near_plane=0.1, far_plane=4.0, num_samples=64)
        self.sampler_pdf = PDFSampler(num_samples=64)

        # field
        self.field_coarse = LuxenField()
        self.field_fine = LuxenField()

        # renderers
        self.renderer_rgb = RGBRenderer()

        # losses
        self.rgb_loss = MSELoss()

    def get_param_groups(self) -> Dict[str, List[Parameter]]:
        """Obtain the parameter groups for the optimizers

        Returns:
            Dict[str, List[Parameter]]: Mapping of different parameter groups
        """
        param_groups = {}
        param_groups["cameras"] = list(self.ray_generator.parameters())
        param_groups["fields"] = list(self.field_coarse.parameters()) + list(self.field_fine.parameters())
        return param_groups

    def forward(self, ray_indices: TensorType["num_rays", 3]):
        """Takes in the ray indices and renders out values."""
        # get the rays:
        ray_bundle = self.ray_generator.forward(ray_indices)  # RayBundle
        # coarse network:
        uniform_ray_samples = self.sampler_uniform(ray_bundle)  # RaySamples
        coarse_field_outputs = self.field_coarse(uniform_ray_samples)  # FieldOutputs

        coarse_renderer_outputs = self.renderer_rgb(
            rgb=coarse_field_outputs[FieldHeadNames.RGB],
            density=coarse_field_outputs[FieldHeadNames.DENSITY],
            deltas=uniform_ray_samples.deltas,
        )  # RendererOutputs
        # fine network:
        pdf_ray_samples = self.sampler_pdf(ray_bundle, uniform_ray_samples, coarse_field_outputs)  # RaySamples
        fine_field_outputs = self.field_fine(pdf_ray_samples)  # FieldOutputs

        fine_renderer_outputs = self.renderer_rgb(
            rgb=fine_field_outputs[FieldHeadNames.RGB],
            density=fine_field_outputs[FieldHeadNames.DENSITY],
            deltas=pdf_ray_samples.deltas,
        )  # RendererOutputs
        # outputs:
        outputs = {"rgb_coarse": coarse_renderer_outputs.rgb, "rgb_fine": fine_renderer_outputs.rgb}
        return outputs

    def get_losses(self, batch, graph_outputs):
        # batch.pixels # (num_rays, 3)
        losses = {}
        rgb_loss_coarse = self.rgb_loss(batch.pixels, graph_outputs["rgb_coarse"])
        rgb_loss_fine = self.rgb_loss(batch.pixels, graph_outputs["rgb_fine"])
        losses = {"rgb_loss_coarse": rgb_loss_coarse, "rgb_loss_fine": rgb_loss_fine}
        return losses
