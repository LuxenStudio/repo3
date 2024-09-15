"""
Luxen-W (Luxen in the wild) implementation.
TODO:
"""

from mattport.luxen.graph.vanilla_luxen import LuxenGraph
from mattport.structures.rays import RayBundle


class LuxenWGraph(LuxenGraph):
    """Luxen-W graph"""

    def __init__(self, intrinsics=None, camera_to_world=None, **kwargs) -> None:
        super().__init__(intrinsics=intrinsics, camera_to_world=camera_to_world, **kwargs)

    def get_outputs(self, ray_bundle: RayBundle):
        raise NotImplementedError

    def get_loss_dict(self, outputs, batch):
        raise NotImplementedError
