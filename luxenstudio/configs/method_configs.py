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

import dcargs

from luxenstudio.configs.base_config import Config, TrainerConfig, ViewerConfig
from luxenstudio.data.datamanagers import VanillaDataManagerConfig
from luxenstudio.data.dataparsers.blender_dataparser import BlenderDataParserConfig
from luxenstudio.data.dataparsers.friends_dataparser import FriendsDataParserConfig
from luxenstudio.data.dataparsers.luxenstudio_dataparser import LuxenstudioDataParserConfig
from luxenstudio.engine.optimizers import AdamOptimizerConfig, RAdamOptimizerConfig
from luxenstudio.models.base_model import VanillaModelConfig
from luxenstudio.models.instant_ngp import InstantNGPModelConfig
from luxenstudio.models.mipluxen import MipLuxenModel
from luxenstudio.models.luxenacto import LuxenactoModelConfig
from luxenstudio.models.semantic_luxenw import SemanticLuxenWModelConfig
from luxenstudio.models.vanilla_luxen import LuxenModel
from luxenstudio.pipelines.base_pipeline import VanillaPipelineConfig
from luxenstudio.pipelines.dynamic_batch import DynamicBatchPipelineConfig

method_configs: Dict[str, Config] = {}
descriptions = {
    "luxenacto": "[bold green]Recommended[/bold green] Real-time model tuned for real captures. "
    + "This model will be continually updated.",
    "instant-ngp": "Implementation of Instant-NGP. Recommended real-time model for bounded synthetic data.",
    "mipluxen": "High quality model for bounded scenes. [red]*slow*",
    "semantic-luxenw": "Predicts semantic segmentations and filters out transient objects.",
    "vanilla-luxen": "Original Luxen model. [red]*slow*",
}

method_configs["luxenacto"] = Config(
    method_name="luxenacto",
    trainer=TrainerConfig(steps_per_eval_batch=500, steps_per_save=2000, mixed_precision=True),
    pipeline=VanillaPipelineConfig(
        datamanager=VanillaDataManagerConfig(
            dataparser=LuxenstudioDataParserConfig(), train_num_rays_per_batch=4096, eval_num_rays_per_batch=8192
        ),
        model=LuxenactoModelConfig(eval_num_rays_per_chunk=1 << 14),
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
    viewer=ViewerConfig(num_rays_per_chunk=1 << 14),
    vis="viewer",
)

method_configs["instant-ngp"] = Config(
    method_name="instant-ngp",
    trainer=TrainerConfig(steps_per_eval_batch=500, steps_per_save=2000, mixed_precision=True),
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

method_configs["mipluxen"] = Config(
    method_name="mipluxen",
    pipeline=VanillaPipelineConfig(
        datamanager=VanillaDataManagerConfig(dataparser=BlenderDataParserConfig(), train_num_rays_per_batch=8192),
        model=VanillaModelConfig(
            _target=MipLuxenModel,
            loss_coefficients={"rgb_loss_coarse": 0.1, "rgb_loss_fine": 1.0},
            num_coarse_samples=128,
            num_importance_samples=128,
            eval_num_rays_per_chunk=8192,
        ),
    ),
    optimizers={
        "fields": {
            "optimizer": RAdamOptimizerConfig(lr=5e-4, eps=1e-08),
            "scheduler": None,
        }
    },
)

method_configs["semantic-luxenw"] = Config(
    method_name="semantic-luxenw",
    trainer=TrainerConfig(steps_per_eval_batch=500, steps_per_save=2000, mixed_precision=True),
    pipeline=VanillaPipelineConfig(
        datamanager=VanillaDataManagerConfig(
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

method_configs["vanilla-luxen"] = Config(
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
        }
    },
)


AnnotatedBaseConfigUnion = dcargs.extras.subcommand_type_from_defaults(
    defaults=method_configs, descriptions=descriptions
)
"""Union[] type over config types, annotated with default instances for use with
dcargs.cli(). Allows the user to pick between one of several base configurations, and
then override values in it."""
