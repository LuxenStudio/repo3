# Copyright 2022 the Regents of the University of California, Luxenstudio Team and contributors. All rights reserved.
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
Luxen implementation that combines many recent advancements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple, Type, Union
import torch
from torch.nn import Parameter
from torchmetrics.functional import structural_similarity_index_measure
from torchmetrics.image import PeakSignalNoiseRatio
from torchmetrics.image.lpip import LearnedPerceptualImagePatchSimilarity

from luxenstudio.cameras.cameras import Cameras
from luxenstudio.engine.callbacks import (TrainingCallback,
                                         TrainingCallbackAttributes,
                                         TrainingCallbackLocation)
from luxenstudio.viewer_beta.viewer_elements import ViewerControl
from luxenstudio.engine.optimizers import Optimizers
from luxenstudio.models.base_model import Model, ModelConfig
import math

from diff_rast.rasterize import RasterizeGaussians
from diff_rast.project_gaussians import ProjectGaussians


def random_quat_tensor(N, **kwargs):
    u = torch.rand(N, **kwargs)
    v = torch.rand(N, **kwargs)
    w = torch.rand(N, **kwargs)
    return torch.stack(
        [
            torch.sqrt(1 - u) * torch.sin(2 * math.pi * v),
            torch.sqrt(1 - u) * torch.cos(2 * math.pi * v),
            torch.sqrt(u) * torch.sin(2 * math.pi * w),
            torch.sqrt(u) * torch.sin(2 * math.pi * w),
        ],
        dim=-1,
    )


def identity_quat(N, **kwargs):
    quat = torch.zeros(N, 4, **kwargs)
    quat[:, 0] = 1
    return quat

def projection_matrix(znear, zfar, fovx, fovy, **kwargs):
    t = znear * math.tan(0.5 * fovy)
    b = -t
    r = znear * math.tan(0.5 * fovx)
    l = -r
    n = znear
    f = zfar
    return torch.tensor(
        [
            [2 * n / (r - l), 0.0, (r + l) / (r - l), 0.0],
            [0.0, 2 * n / (t - b), (t + b) / (t - b), 0.0],
            [0.0, 0.0, (f + n) / (f - n), -1.0 * f * n / (f - n)],
            [0.0, 0.0, 1.0, 0.0],
        ],
        **kwargs
    )


@dataclass
class GaussianSplattingModelConfig(ModelConfig):
    """Gaussian Splatting Model Config"""
    _target: Type = field(default_factory=lambda: GaussianSplattingModel)
    warmup_length:int = 100
    """period of steps where resolution is upscaled iteratively"""
    refine_every:int = 100
    """period of steps where gaussians are culled and densified"""
    cull_alpha_thresh:float = .005
    """threshold of opacity for culling gaussians"""
    cull_scale_thresh:float = .5
    """threshold of scale for culling gaussians"""
    reset_alpha_every:int = 10
    """Every this many refinement steps, reset the alpha"""
    densify_grad_thresh: float = .0002
    """threshold of positional gradient norm for densifying gaussians"""
    densify_size_thresh: float = .01
    """below this size, gaussians are *duplicated*, otherwise split"""
    

class GaussianSplattingModel(Model):
    """Gaussian Splatting model

    TODO (jake-austin): Figure out how to print out on the training log in terminal the number of splats

    Args:
        config: Gaussian Splatting configuration to instantiate model
    """

    config: GaussianSplattingModelConfig
    def __init__(self,*args,**kwargs):
        self.seed_pts = kwargs['seed_points']
        super().__init__(*args,**kwargs)
        self.vc = ViewerControl()

    def populate_modules(self):
        # TODO (jake-austin): clean this up, this is transplanted code across all the implementation functions
        self.means = torch.nn.Parameter(self.seed_pts[0])
        self.means_grad_norm = None
        init_scale = torch.log(torch.tensor(.01)).item()
        self.scales = torch.nn.Parameter(torch.full((self.num_points,3),init_scale))
        self.quats = torch.nn.Parameter(random_quat_tensor(self.num_points))
        rgbinit = torch.clamp((self.seed_pts[1].float())/255.,0,1)
        self.rgbs = torch.nn.Parameter(torch.logit(rgbinit))
        self.opacities = torch.nn.Parameter(torch.zeros(self.num_points, 1))
        # metrics
        self.psnr = PeakSignalNoiseRatio(data_range=1.0)
        from torchmetrics.image import StructuralSimilarityIndexMeasure
        self.ssim = StructuralSimilarityIndexMeasure()
        self.lpips = LearnedPerceptualImagePatchSimilarity(normalize=True)
        self.step=0
        
    def remove_from_optim(self,optimizer, deleted_mask, new_params):
        """removes the deleted_mask from the optimizer provided"""
        assert len(new_params) == 1
        assert isinstance(optimizer,torch.optim.Adam),"Only works with Adam"
        param = optimizer.param_groups[0]['params'][0]
        param_state = optimizer.state[param]
        param_state['exp_avg'] = param_state['exp_avg'][~deleted_mask.squeeze()]
        param_state['exp_avg_sq'] = param_state['exp_avg_sq'][~deleted_mask.squeeze()]
        del optimizer.state[param]
        optimizer.state[param] = param_state
        optimizer.param_groups[0]['params'] = new_params

    def after_train(self,step):
        with torch.no_grad():
            #keep track of a moving average of grad norms
            if self.means_grad_norm is None:
                self.means_grad_norm = self.means.grad.norm(dim=-1,keepdim=True)
            else:
                self.means_grad_norm = .1 * self.means.grad.norm(dim=-1,keepdim=True) + .9 * self.means_grad_norm
    
    def refinement_before(self, optimizers:Optimizers, step):
        print("Inside refinement before")
        if self.step > self.config.warmup_length:
            # do all the refinement stuff here
            #first we cull gaussians
            deleted_mask = self.cull_gaussians()
            param_groups = self.get_param_groups()
            for group,param in param_groups.items(): 
                self.remove_from_optim(optimizers.optimizers[group],deleted_mask,param)
            

    def refinement_after(self, optimizers:Optimizers, step):
        if self.step > self.config.warmup_length:
            #then we densify
            high_grads = (self.means_grad_norm > self.config.densify_grad_thresh).squeeze()
            splits = (self.scales.exp().max(dim=-1).values > self.config.densify_size_thresh).squeeze()
            splits &= high_grads
            dups = ~splits
            dups &= high_grads
            self.split_gaussians(splits)
            self.dup_gaussians(dups) 
            if self.step // self.config.refine_every % self.config.reset_alpha_every == 0:
                print("Resetting alpha")
                with torch.no_grad():
                    reset_value = .01
                    self.opacities.data = torch.full_like(self.opacities.data,torch.logit(torch.tensor(reset_value)).item())
            self.means_grad_norm = None
            
    def cull_gaussians(self):
        """
        This function deletes gaussians with under a certain opacity threshold
        """
        n_bef = self.num_points
        with torch.no_grad():
            #cull transparent ones
            culls = (torch.sigmoid(self.opacities) < self.config.cull_alpha_thresh).squeeze()
            #cull huge ones
            culls |= (torch.exp(self.scales).max(dim=-1).values > self.config.cull_scale_thresh).squeeze()
            self.means = Parameter(self.means[~culls])
            self.means_grad_norm = self.means_grad_norm[~culls]
            self.scales = Parameter(self.scales[~culls])
            self.quats = Parameter(self.quats[~culls])
            self.rgbs = Parameter(self.rgbs[~culls])
            self.opacities = Parameter(self.opacities[~culls])

        print(f"Culled {n_bef - self.num_points} gaussians")
        return culls

    def split_gaussians(self, split_mask):
        """
        This function splits gaussians that are too large
        """
        print(f"Would split {split_mask.sum().item()} gaussians")

    def dup_gaussians(self,dup_mask):
        """
        This function duplicates gaussians that are too small
        """
        print(f"Would duplicate {dup_mask.sum().item()} gaussians")

    @property
    def num_points(self):
        return self.means.shape[0]
    
    def get_training_callbacks(
        self, training_callback_attributes: TrainingCallbackAttributes
    ) -> List[TrainingCallback]:
        """
        List of things that are important:
        every 300 steps, densify by calculating positional gradients and duplicating/splitting
        every 3000 steps: drop all alpha to low, and continue optimization
        cull gaussians with alpha under a threshold
        upscale image resolution every 300 iterations
        SH coefficients are masked initially and get activated over time
        
        
        """
        cbs = []
        cbs.append(TrainingCallback([TrainingCallbackLocation.BEFORE_TRAIN_ITERATION],self.step_cb))
        cbs.append(TrainingCallback([TrainingCallbackLocation.BEFORE_TRAIN_ITERATION],
                                    self.refinement_before,
                                    update_every_num_iters=self.config.refine_every,
                                    args=[training_callback_attributes.optimizers]
                                    ))
        cbs.append(TrainingCallback([TrainingCallbackLocation.AFTER_TRAIN_ITERATION],
                                    self.refinement_after,
                                    update_every_num_iters=self.config.refine_every,
                                    args=[training_callback_attributes.optimizers]
                                    ))
        cbs.append(TrainingCallback([TrainingCallbackLocation.AFTER_TRAIN_ITERATION],
                                    self.after_train,))
        return cbs
    
    def step_cb(self,step):
        self.step = step

    def get_param_groups(self) -> Dict[str, List[Parameter]]:
        """Obtain the parameter groups for the optimizers

        Returns:
            Mapping of different parameter groups
        """
        return {
            "xyz": [self.means],
            "color": [self.rgbs],
            "opacity": [self.opacities],
            "scaling": [self.scales],
            "rotation": [self.quats],
        }

    def get_outputs(self, camera: Cameras) -> Dict[str, Union[torch.Tensor, List]]:
        """Takes in a Ray Bundle and returns a dictionary of outputs.

        TODO (jake-austin): use the new homebrew luxenstudio gaussian rasterization code instead

        Args:
            ray_bundle: Input bundle of rays. This raybundle should have all the
            needed information to compute the outputs.

        Returns:
            Outputs of model. (ie. rendered colors)
        """
        import viser.transforms as vtf
        import numpy as np
        if not isinstance(camera,Cameras):
            print("Called get_outputs with not a camera")
            return {}
        assert camera.shape[0] ==1, "Only one camera at a time"

        #shift the camera to center of scene looking at center
        R = camera.camera_to_worlds[..., :3, :3] # 1 x 3 x 3
        T = camera.camera_to_worlds[..., :3, 3:4] # 1 x 3 x 1
        R = vtf.SO3.from_matrix(R.cpu().squeeze().numpy())
        R = R @ vtf.SO3.from_x_radians(np.pi)
        R = torch.from_numpy(R.as_matrix()[None,...]).to(self.device,torch.float32)
        #vickie pops off here
        viewmat = torch.cat([R,T],dim=2)
        #add a row of zeros and a 1 to the bottom of the viewmat
        viewmat = torch.cat([viewmat,torch.tensor([[[0,0,0,1]]],device=self.device)],dim=1)
        #invert it
        viewmat = torch.inverse(viewmat)
        #calculate the FOV of the camera given fx and fy, width and height
        cx = camera.cx.item()
        cy = camera.cy.item()
        fovx = 2 * math.atan(camera.width / (2 * camera.fx))
        fovy = 2 * math.atan(camera.height / (2 * camera.fy))
        W, H = camera.width.item(), camera.height.item()
        projmat = projection_matrix(.0001,1000,fovx,fovy).to(self.device)
        BLOCK_X, BLOCK_Y = 16, 16
        tile_bounds = (
            (W + BLOCK_X - 1) // BLOCK_X,
            (H + BLOCK_Y - 1) // BLOCK_Y,
            1,
        )
        background = torch.ones(3, device=self.device)
        xys, depths, radii, conics, num_tiles_hit = ProjectGaussians.apply(
            self.means,
            torch.exp(self.scales),
            1,
            self.quats,
            viewmat.squeeze()[:3,:],
            projmat.squeeze()@viewmat.squeeze(),
            camera.fx.item(),
            camera.fy.item(),
            H,
            W,
            tile_bounds
        )
        cx_delta = cx - W / 2
        cy_delta = cy - H / 2
        xys = xys.view(-1, 2) + torch.tensor([cx_delta, cy_delta], device=self.device)
        rgb = RasterizeGaussians.apply(
            xys,
            depths,
            radii,
            conics,
            num_tiles_hit,
            torch.sigmoid(self.rgbs),
            torch.sigmoid(self.opacities),
            H,
            W,
            background,
        )
        return {"rgb": rgb}


    def get_metrics_dict(self, outputs, batch) -> Dict[str, torch.Tensor]:
        """Compute and returns metrics.

        Args:
            outputs: the output to compute loss dict to
            batch: ground truth batch corresponding to outputs
        """

        return {}

    def get_loss_dict(self, outputs, batch, metrics_dict=None) -> Dict[str, torch.Tensor]:
        """Computes and returns the losses dict.

        Args:
            outputs: the output to compute loss dict to
            batch: ground truth batch corresponding to outputs
            metrics_dict: dictionary of metrics, some of which we can use for loss
        """
        #imshow the rendered vs the gt
        # import matplotlib.pyplot as plt
        # fig,ax = plt.subplots(1,1)
        # ax.imshow(batch['image'].detach().cpu().squeeze())
        # ax.imshow(outputs['rgb'].detach().cpu().squeeze(),alpha=.5)
        # plt.show()
        Ll1 = torch.nn.functional.l1_loss(batch['image'], outputs['rgb'])
        # This simloss makes the results look weird, removing for now
        # simloss = self.ssim(batch['image'].permute(2,0,1)[None,...], outputs['rgb'].permute(2,0,1)[None,...])
        return {"main_loss": Ll1}

    @torch.no_grad()
    def get_outputs_for_camera_ray_bundle(self, camera_ray_bundle: Cameras) -> Dict[str, torch.Tensor]:
        """Takes in camera parameters and computes the output of the model.

        Args:
            camera_ray_bundle: ray bundle to calculate outputs over
        """
        outs = self.get_outputs(camera_ray_bundle.to(self.device))
        outs["rgb"] = torch.clamp(outs["rgb"], 0.0, 1.0)
        return outs

    def get_image_metrics_and_images(
        self, outputs: Dict[str, torch.Tensor], batch: Dict[str, torch.Tensor]
    ) -> Tuple[Dict[str, float], Dict[str, torch.Tensor]]:
        """Writes the test image outputs.

        Args:
            image_idx: Index of the image.
            step: Current step.
            batch: Batch of data.
            outputs: Outputs of the model.

        Returns:
            A dictionary of metrics.
        """
        gt_rgb = batch["image"].to(self.device)
        predicted_rgb = outputs["rgb"]  # Blended with background (black if random background)

        combined_rgb = torch.cat([gt_rgb, predicted_rgb], dim=1)

        # Switch images from [H, W, C] to [1, C, H, W] for metrics computations
        gt_rgb = torch.moveaxis(gt_rgb, -1, 0)[None, ...]
        predicted_rgb = torch.moveaxis(predicted_rgb, -1, 0)[None, ...]

        psnr = self.psnr(gt_rgb, predicted_rgb)
        ssim = self.ssim(gt_rgb, predicted_rgb)
        lpips = self.lpips(gt_rgb, predicted_rgb)

        # all of these metrics will be logged as scalars
        metrics_dict = {"psnr": float(psnr.item()), "ssim": float(ssim)}  # type: ignore
        metrics_dict["lpips"] = float(lpips)

        images_dict = {"img": combined_rgb}

        return metrics_dict, images_dict

