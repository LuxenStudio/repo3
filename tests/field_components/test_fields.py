"""
Test the fields
"""

import torch

from luxenstudio.cameras.rays import Frustums, RaySamples
from luxenstudio.fields.luxenacto_field import LuxenactoField
from luxenstudio.utils.external import TCNN_EXISTS, tcnn_import_exception


def test_luxenacto_field():
    """Test the Luxenacto field"""
    if not TCNN_EXISTS:
        # tinycudann module doesn't exist
        print(tcnn_import_exception)
        return
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    aabb_scale = 1.0
    aabb = torch.tensor(
        [[-aabb_scale, -aabb_scale, -aabb_scale], [aabb_scale, aabb_scale, aabb_scale]],
        dtype=torch.float32,
        device=device,
    )
    field = LuxenactoField(aabb, num_images=1).to(device)
    num_rays = 1024
    num_samples = 256
    positions = torch.rand((num_rays, num_samples, 3), dtype=torch.float32, device=device)
    directions = torch.rand_like(positions)
    frustums = Frustums(
        origins=positions,
        directions=directions,
        starts=torch.zeros((*directions.shape[:-1], 1), device=device),
        ends=torch.zeros((*directions.shape[:-1], 1), device=device),
        pixel_area=torch.ones((*directions.shape[:-1], 1), device=device),
    )
    ray_samples = RaySamples(
        frustums=frustums,
        camera_indices=torch.zeros(
            (num_rays, 1, 1),
            device=device,
            dtype=torch.int32,
        ),
    )
    field.forward(ray_samples)


if __name__ == "__main__":
    test_luxenacto_field()
