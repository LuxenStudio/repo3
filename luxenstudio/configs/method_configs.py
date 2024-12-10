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
Put all the method implementations in one location.
"""

from __future__ import annotations

from typing import Dict

import tyro
from luxenacc import ContractionType

from luxenstudio.cameras.camera_optimizers import CameraOptimizerConfig
from luxenstudio.configs.base_config import ViewerConfig
from luxenstudio.data.datamanagers.base_datamanager import VanillaDataManagerConfig
from luxenstudio.data.datamanagers.depth_datamanager import DepthDataManagerConfig
from luxenstudio.data.datamanagers.dreamfusion_datamanager import (
    DreamFusionDataManagerConfig,
)
from luxenstudio.data.datamanagers.semantic_datamanager import SemanticDataManagerConfig
from luxenstudio.data.datamanagers.variable_res_datamanager import (
    VariableResDataManagerConfig,
)
from luxenstudio.data.dataparsers.blender_dataparser import BlenderDataParserConfig
from luxenstudio.data.dataparsers.dluxen_dataparser import DLuxenDataParserConfig
from luxenstudio.data.dataparsers.dycheck_dataparser import DycheckDataParserConfig
from luxenstudio.data.dataparsers.friends_dataparser import FriendsDataParserConfig
from luxenstudio.data.dataparsers.instant_ngp_dataparser import (
    InstantNGPDataParserConfig,
)
from luxenstudio.data.dataparsers.luxenstudio_dataparser import LuxenstudioDataParserConfig
from luxenstudio.data.dataparsers.phototourism_dataparser import (
    PhototourismDataParserConfig,
)
from luxenstudio.engine.optimizers import AdamOptimizerConfig, RAdamOptimizerConfig
from luxenstudio.engine.schedulers import SchedulerConfig,WarmupScheduler
from luxenstudio.engine.trainer import TrainerConfig
from luxenstudio.field_components.temporal_distortions import TemporalDistortionKind
from luxenstudio.models.depth_luxenacto import DepthLuxenactoModelConfig
from luxenstudio.models.dreamfusion import DreamFusionModelConfig
from luxenstudio.models.instant_ngp import InstantNGPModelConfig
from luxenstudio.models.mipluxen import MipLuxenModel
from luxenstudio.models.luxenacto import LuxenactoModelConfig
from luxenstudio.models.luxenplayer_luxenacto import LuxenplayerLuxenactoModelConfig
from luxenstudio.models.luxenplayer_ngp import LuxenplayerNGPModelConfig
from luxenstudio.models.semantic_luxenw import SemanticLuxenWModelConfig
from luxenstudio.models.tensorf import TensoRFModelConfig
from luxenstudio.models.vanilla_luxen import LuxenModel, VanillaModelConfig
from luxenstudio.pipelines.base_pipeline import VanillaPipelineConfig
from luxenstudio.pipelines.dreamfusion_pipeline import DreamfusionPipelineConfig
from luxenstudio.pipelines.dynamic_batch import DynamicBatchPipelineConfig
from luxenstudio.plugins.registry import discover_methods

method_configs: Dict[str, TrainerConfig] = {}
descriptions = {
    "luxenacto": "Recommended real-time model tuned for real captures. This model will be continually updated.",
    "depth-luxenacto": "Luxenacto with depth supervision.",
    "instant-ngp": "Implementation of Instant-NGP. Recommended real-time model for unbounded scenes.",
    "instant-ngp-bounded": "Implementation of Instant-NGP. Recommended for bounded real and synthetic scenes",
    "mipluxen": "High quality model for bounded scenes. (slow)",
    "semantic-luxenw": "Predicts semantic segmentations and filters out transient objects.",
    "vanilla-luxen": "Original Luxen model. (slow)",
    "tensorf": "tensorf",
    "dluxen": "Dynamic-Luxen model. (slow)",
    "phototourism": "Uses the Phototourism data.",
    "dreamfusion": "Generative Text to Luxen model",
    "luxenplayer-luxenacto": "LuxenPlayer with luxenacto backbone.",
    "luxenplayer-ngp": "LuxenPlayer with InstantNGP backbone.",
}

method_configs["luxenacto"] = TrainerConfig(
    method_name="luxenacto",
    steps_per_eval_batch=20,
    steps_per_save=2000,
    max_num_iterations=30000,
    mixed_precision=True,
    pipeline=VanillaPipelineConfig(
        datamanager=VanillaDataManagerConfig(
            dataparser=LuxenstudioDataParserConfig(),
            train_num_rays_per_batch=4096,
            eval_num_rays_per_batch=4096,
            camera_optimizer=CameraOptimizerConfig(
                mode="SO3xR3", optimizer=AdamOptimizerConfig(lr=6e-4, eps=1e-8, weight_decay=1e-2)
            ),
        ),
        model=LuxenactoModelConfig(eval_num_rays_per_chunk=1 << 15),
    ),
    optimizers={
        "proposal_networks": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        },
        "fields": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        },
    },
    viewer=ViewerConfig(num_rays_per_chunk=1 << 15),
    vis="viewer",
)

method_configs["depth-luxenacto"] = TrainerConfig(
    method_name="depth-luxenacto",
    steps_per_eval_batch=500,
    steps_per_save=2000,
    max_num_iterations=30000,
    mixed_precision=True,
    pipeline=VanillaPipelineConfig(
        datamanager=DepthDataManagerConfig(
            dataparser=LuxenstudioDataParserConfig(),
            train_num_rays_per_batch=4096,
            eval_num_rays_per_batch=4096,
            camera_optimizer=CameraOptimizerConfig(
                mode="SO3xR3", optimizer=AdamOptimizerConfig(lr=6e-4, eps=1e-8, weight_decay=1e-2)
            ),
        ),
        model=DepthLuxenactoModelConfig(eval_num_rays_per_chunk=1 << 15),
    ),
    optimizers={
        "proposal_networks": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        },
        "fields": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        },
    },
    viewer=ViewerConfig(num_rays_per_chunk=1 << 15),
    vis="viewer",
)

method_configs["instant-ngp"] = TrainerConfig(
    method_name="instant-ngp",
    steps_per_eval_batch=500,
    steps_per_save=2000,
    max_num_iterations=30000,
    mixed_precision=True,
    pipeline=DynamicBatchPipelineConfig(
        datamanager=VanillaDataManagerConfig(dataparser=LuxenstudioDataParserConfig(), train_num_rays_per_batch=8192),
        model=InstantNGPModelConfig(eval_num_rays_per_chunk=8192),
    ),
    optimizers={
        "fields": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        }
    },
    viewer=ViewerConfig(num_rays_per_chunk=64000),
    vis="viewer",
)


method_configs["instant-ngp-bounded"] = TrainerConfig(
    method_name="instant-ngp-bounded",
    steps_per_eval_batch=500,
    steps_per_save=2000,
    max_num_iterations=30000,
    mixed_precision=True,
    pipeline=DynamicBatchPipelineConfig(
        datamanager=VanillaDataManagerConfig(dataparser=InstantNGPDataParserConfig(), train_num_rays_per_batch=8192),
        model=InstantNGPModelConfig(
            eval_num_rays_per_chunk=8192,
            contraction_type=ContractionType.AABB,
            render_step_size=0.001,
            max_num_samples_per_ray=48,
            near_plane=0.01,
            background_color="black",
        ),
    ),
    optimizers={
        "fields": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        }
    },
    viewer=ViewerConfig(num_rays_per_chunk=64000),
    vis="viewer",
)


method_configs["mipluxen"] = TrainerConfig(
    method_name="mipluxen",
    pipeline=VanillaPipelineConfig(
        datamanager=VanillaDataManagerConfig(dataparser=LuxenstudioDataParserConfig(), train_num_rays_per_batch=1024),
        model=VanillaModelConfig(
            _target=MipLuxenModel,
            loss_coefficients={"rgb_loss_coarse": 0.1, "rgb_loss_fine": 1.0},
            num_coarse_samples=128,
            num_importance_samples=128,
            eval_num_rays_per_chunk=1024,
        ),
    ),
    optimizers={
        "fields": {
            "optimizer": RAdamOptimizerConfig(lr=5e-4, eps=1e-08),
            "scheduler": None,
        }
    },
)

method_configs["semantic-luxenw"] = TrainerConfig(
    method_name="semantic-luxenw",
    steps_per_eval_batch=500,
    steps_per_save=2000,
    max_num_iterations=30000,
    mixed_precision=True,
    pipeline=VanillaPipelineConfig(
        datamanager=SemanticDataManagerConfig(
            dataparser=FriendsDataParserConfig(), train_num_rays_per_batch=4096, eval_num_rays_per_batch=8192
        ),
        model=SemanticLuxenWModelConfig(eval_num_rays_per_chunk=1 << 16),
    ),
    optimizers={
        "proposal_networks": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        },
        "fields": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        },
    },
    viewer=ViewerConfig(num_rays_per_chunk=1 << 16),
    vis="viewer",
)

method_configs["vanilla-luxen"] = TrainerConfig(
    method_name="vanilla-luxen",
    pipeline=VanillaPipelineConfig(
        datamanager=VanillaDataManagerConfig(
            dataparser=BlenderDataParserConfig(),
        ),
        model=VanillaModelConfig(_target=LuxenModel),
    ),
    optimizers={
        "fields": {
            "optimizer": RAdamOptimizerConfig(lr=5e-4, eps=1e-08),
            "scheduler": None,
        },
        "temporal_distortion": {
            "optimizer": RAdamOptimizerConfig(lr=5e-4, eps=1e-08),
            "scheduler": None,
        },
    },
)

method_configs["tensorf"] = TrainerConfig(
    method_name="tensorf",
    steps_per_eval_batch=500,
    steps_per_save=2000,
    max_num_iterations=30000,
    mixed_precision=False,
    pipeline=VanillaPipelineConfig(
        datamanager=VanillaDataManagerConfig(
            dataparser=BlenderDataParserConfig(),
        ),
        model=TensoRFModelConfig(),
    ),
    optimizers={
        "fields": {
            "optimizer": AdamOptimizerConfig(lr=0.001),
            "scheduler": SchedulerConfig(lr_final=0.0001, max_steps=30000),
        },
        "encodings": {
            "optimizer": AdamOptimizerConfig(lr=0.02),
            "scheduler": SchedulerConfig(lr_final=0.002, max_steps=30000),
        },
    },
    viewer=ViewerConfig(num_rays_per_chunk=1 << 15),
    vis="viewer",
)

method_configs["dluxen"] = TrainerConfig(
    method_name="dluxen",
    pipeline=VanillaPipelineConfig(
        datamanager=VanillaDataManagerConfig(dataparser=DLuxenDataParserConfig()),
        model=VanillaModelConfig(
            _target=LuxenModel,
            enable_temporal_distortion=True,
            temporal_distortion_params={"kind": TemporalDistortionKind.DNERF},
        ),
    ),
    optimizers={
        "fields": {
            "optimizer": RAdamOptimizerConfig(lr=5e-4, eps=1e-08),
            "scheduler": None,
        },
        "temporal_distortion": {
            "optimizer": RAdamOptimizerConfig(lr=5e-4, eps=1e-08),
            "scheduler": None,
        },
    },
)

method_configs["phototourism"] = TrainerConfig(
    method_name="phototourism",
    steps_per_eval_batch=500,
    steps_per_save=2000,
    max_num_iterations=30000,
    mixed_precision=True,
    pipeline=VanillaPipelineConfig(
        datamanager=VariableResDataManagerConfig(  # NOTE: one of the only differences with luxenacto
            dataparser=PhototourismDataParserConfig(),  # NOTE: one of the only differences with luxenacto
            train_num_rays_per_batch=4096,
            eval_num_rays_per_batch=4096,
            camera_optimizer=CameraOptimizerConfig(
                mode="SO3xR3", optimizer=AdamOptimizerConfig(lr=6e-4, eps=1e-8, weight_decay=1e-2)
            ),
        ),
        model=LuxenactoModelConfig(eval_num_rays_per_chunk=1 << 15),
    ),
    optimizers={
        "proposal_networks": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        },
        "fields": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        },
    },
    viewer=ViewerConfig(num_rays_per_chunk=1 << 15),
    vis="viewer",
)

method_configs["dreamfusion"] = TrainerConfig(
    method_name="dreamfusion",
    steps_per_eval_batch=50,
    steps_per_eval_image=50,
    steps_per_save=200,
    max_num_iterations=30000,
    mixed_precision=True,
    pipeline=DreamfusionPipelineConfig(
        datamanager=DreamFusionDataManagerConfig(
            dataparser=LuxenstudioDataParserConfig(),
            train_num_rays_per_batch=4096,
            eval_num_rays_per_batch=4096,
        ),
        model=DreamFusionModelConfig(
            eval_num_rays_per_chunk=1 << 15,
            distortion_loss_mult=10.0,
            orientation_loss_mult=0.1,
            max_res=256,
            sphere_collider=True,
            initialize_density=False,
            random_background=True,
            interlevel_loss_mult=1.0,
            proposal_warmup=500,
            proposal_update_every=5,
            proposal_weights_anneal_max_num_iters=100,
            start_lambertian_training=1000,
            start_normals_training=500,
            opacity_loss_mult=0.001,
        ),
        interpolated_prompting=False,
        guidance_scale=100,
    ),
    optimizers={
        "proposal_networks": {
            "optimizer": AdamOptimizerConfig(lr=5e-2, eps=1e-15),
            "scheduler": None,
        },
        "fields": {
            "optimizer": AdamOptimizerConfig(lr=5e-3, eps=1e-15),
            "scheduler": WarmupScheduler(lr_init=1e-9,lr_max=1e-4,lr_final=1e-6,warmup_steps=3000,max_steps=10000),
        },
    },
    viewer=ViewerConfig(num_rays_per_chunk=1 << 15),
    vis="viewer",
)

method_configs["luxenplayer-luxenacto"] = TrainerConfig(
    method_name="luxenplayer-luxenacto",
    pipeline=VanillaPipelineConfig(
        datamanager=DepthDataManagerConfig(
            dataparser=DycheckDataParserConfig(),
            train_num_rays_per_batch=4096,
            eval_num_rays_per_batch=4096,
            camera_optimizer=CameraOptimizerConfig(
                mode="SO3xR3", optimizer=AdamOptimizerConfig(lr=6e-4, eps=1e-8, weight_decay=1e-2)
            ),
        ),
        model=LuxenplayerLuxenactoModelConfig(eval_num_rays_per_chunk=1 << 15),
    ),
    optimizers={
        "proposal_networks": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        },
        "fields": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        },
    },
    viewer=ViewerConfig(),
    vis="viewer",
)

method_configs["luxenplayer-ngp"] = TrainerConfig(
    method_name="luxenplayer-ngp",
    steps_per_eval_batch=500,
    steps_per_save=2000,
    max_num_iterations=30000,
    mixed_precision=True,
    pipeline=DynamicBatchPipelineConfig(
        datamanager=DepthDataManagerConfig(dataparser=DycheckDataParserConfig(), train_num_rays_per_batch=8192),
        model=LuxenplayerNGPModelConfig(
            eval_num_rays_per_chunk=8192,
            contraction_type=ContractionType.AABB,
            render_step_size=0.001,
            max_num_samples_per_ray=48,
            near_plane=0.01,
        ),
    ),
    optimizers={
        "fields": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        }
    },
    viewer=ViewerConfig(num_rays_per_chunk=64000),
    vis="viewer",
)

external_methods, external_descriptions = discover_methods()
method_configs.update(external_methods)
descriptions.update(external_descriptions)

AnnotatedBaseConfigUnion = tyro.conf.SuppressFixed[  # Don't show unparseable (fixed) arguments in helptext.
    tyro.conf.FlagConversionOff[
        tyro.extras.subcommand_type_from_defaults(defaults=method_configs, descriptions=descriptions)
    ]
]
"""Union[] type over config types, annotated with default instances for use with
tyro.cli(). Allows the user to pick between one of several base configurations, and
then override values in it."""
