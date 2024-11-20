from dataclasses import dataclass, field
from typing import Type

import matplotlib.pyplot as plt
import numpy as np
from torch.cuda.amp.grad_scaler import GradScaler
from typing_extensions import Literal

from luxenstudio.data.datamanagers.dreamfusion_datamanager import (
    DreamFusionDataManagerConfig,
)
from luxenstudio.engine.optimizers import Optimizers
from luxenstudio.generative.stable_diffusion import StableDiffusion
from luxenstudio.pipelines.base_pipeline import VanillaPipeline, VanillaPipelineConfig
from luxenstudio.utils import profiler


@dataclass
class DreamfusionPipelineConfig(VanillaPipelineConfig):
    """Configuration for pipeline instantiation"""

    _target: Type = field(default_factory=lambda: DreamfusionPipeline)
    """target class to instantiate"""
    datamanager: DreamFusionDataManagerConfig = DreamFusionDataManagerConfig()
    """specifies the datamanager config"""
    prompt: str = "A high quality photo of a pineapple"
    """prompt for stable dreamfusion"""

    location_based_prompting: bool = True
    """enables location based prompting"""
    side_prompt: str = ", side view"
    """appended to prompt for side view"""
    front_prompt: str = ", front view"
    """appended to prompt for front view"""
    back_prompt: str = ", back view"
    """appended to prompt for back view"""

    opacity_penalty: bool = True
    """enables penalty to encourage transparent scenes"""
    target_transmittance: float = 0.5
    """target transmittance for opacity penalty"""

    guidance_scale: float = 100
    """guidance scale for sds loss"""


class DreamfusionPipeline(VanillaPipeline):
    def __init__(
        self,
        config: DreamfusionPipelineConfig,
        device: str,
        test_mode: Literal["test", "val", "inference"] = "val",
        world_size: int = 1,
        local_rank: int = 0,
    ):
        super().__init__(config, device, test_mode, world_size, local_rank)
        self.generative = True
        self.sd = StableDiffusion(device)
        if config.location_based_prompting:
            self.front_text_embedding = self.sd.get_text_embeds(f"{config.prompt}{config.front_prompt}", "")
            self.side_text_embedding = self.sd.get_text_embeds(f"{config.prompt}{config.side_prompt}", "")
            self.back_text_embedding = self.sd.get_text_embeds(f"{config.prompt}{config.back_prompt}", "")
        else:
            self.base_text_embedding = self.sd.get_text_embeds(config.prompt, "")

    @profiler.time_function
    def custom_step(self, step: int, grad_scaler: GradScaler, optimizers: Optimizers):
        """This function gets your training loss dict. This will be responsible for
        getting the next batch of data from the DataManager and interfacing with the
        Model class, feeding the data to the model's forward function.

        Args:
            step: current iteration step to update sampler if using DDP (distributed)
        """
        if self.world_size > 1 and step:
            assert self.datamanager.train_sampler is not None
            self.datamanager.train_sampler.set_epoch(step)
        ray_bundle, batch = self.datamanager.next_train(step)
        model_outputs = self.model(ray_bundle)

        train_output = model_outputs["train_output"].view(1, 64, 64, 3).permute(0, 3, 1, 2)

        accumulation = model_outputs["accumulation"].view(64, 64).detach().cpu().numpy()
        accumulation = np.clip(accumulation, 0.0, 1.0)
        plt.imsave("luxen_accumulation.jpg", accumulation)

        # background = model_outputs["background"].view(64, 64, 3).detach().cpu().numpy()
        # background = np.clip(background, 0.0, 1.0)
        # plt.imsave("luxen_background.jpg", background)

        # shaded = model_outputs["shaded"].view(64, 64, 3).detach().cpu().numpy()
        # shaded = np.clip(shaded, 0.0, 1.0)
        # plt.imsave("luxen_textureless.jpg", shaded)

        if self.config.location_based_prompting:
            if batch["central"] > 315 or batch["central"] <= 45:
                text_embedding = self.front_text_embedding
            elif batch["central"] > 45 and batch["central"] <= 135:
                text_embedding = self.side_text_embedding
            elif batch["central"] > 135 and batch["central"] <= 225:
                text_embedding = self.back_text_embedding
            elif batch["central"] > 225 and batch["central"] <= 315:
                text_embedding = self.side_text_embedding
        else:
            text_embedding = self.base_text_embedding

        sds_loss, latents, grad = self.sd.sds_loss(
            text_embedding, train_output, guidance_scale=self.config.guidance_scale
        )
        # TODO: opacity penalty using transmittance, not accumultation
        if self.config.opacity_penalty:
            accum_mean = np.mean(1.0 - accumulation)
            sds_loss *= np.min((0.5, accum_mean))

        grad_scaler.scale(latents).backward(gradient=grad, retain_graph=True)
        # optimizers.scheduler_step_all(step)
        # optimizers.optimizer_scaler_step_all(grad_scaler)
        # grad_scaler.update()

        metrics_dict = self.model.get_metrics_dict(model_outputs, batch)
        loss_dict = self.model.get_loss_dict(model_outputs, batch, metrics_dict)
        loss_dict["sds_loss"] = sds_loss

        normals_loss = loss_dict["orientation_loss"] + loss_dict["pred_normal_loss"]
        grad_scaler.scale(normals_loss).backward()  # type: ignore
        optimizers.optimizer_scaler_step_all(grad_scaler)

        grad_scaler.update()
        optimizers.scheduler_step_all(step)

        return model_outputs, loss_dict, metrics_dict
