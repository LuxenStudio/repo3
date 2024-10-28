# Copyright 2022 The Plenoptix Team. All rights reserved.
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

from luxenactory.configs.base import (
    AdamOptimizerConfig,
    Config,
    RAdamOptimizerConfig,
    SchedulerConfig,
    TrainerConfig,
    ViewerConfig,
)
from luxenactory.datamanagers.base import VanillaDataManagerConfig
from luxenactory.datamanagers.dataparsers.blender_parser import BlenderDataParserConfig
from luxenactory.datamanagers.dataparsers.friends_parser import FriendsDataParserConfig
from luxenactory.datamanagers.dataparsers.mipluxen_parser import (
    MipLuxen360DataParserConfig,
)
from luxenactory.models.base import VanillaModelConfig
from luxenactory.models.compound import CompoundModelConfig
from luxenactory.models.instant_ngp import InstantNGPModelConfig
from luxenactory.models.mipluxen import MipLuxenModel
from luxenactory.models.mipluxen_360 import MipLuxen360Model
from luxenactory.models.luxenw import LuxenWModelConfig
from luxenactory.models.proposal import ProposalModelConfig
from luxenactory.models.semantic_luxen import SemanticLuxenModel
from luxenactory.models.tensorf import TensoRFModelConfig
from luxenactory.models.vanilla_luxen import LuxenModel
from luxenactory.pipelines.base import VanillaPipelineConfig
from luxenactory.pipelines.dynamic_batch import DynamicBatchPipelineConfig

base_configs: Dict[str, Config] = {}
base_configs["compound"] = Config(
    method_name="compound",
    trainer=TrainerConfig(mixed_precision=True),
    pipeline=DynamicBatchPipelineConfig(
        datamanager=VanillaDataManagerConfig(dataparser=BlenderDataParserConfig(), train_num_rays_per_batch=8192),
        model=CompoundModelConfig(eval_num_rays_per_chunk=8192),
    ),
    optimizers={
        "fields": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        }
    },
    vis=["viewer"],
)

base_configs["instant-ngp"] = Config(
    method_name="instant-ngp",
    trainer=TrainerConfig(steps_per_eval_batch=500, steps_per_save=2000, mixed_precision=True),
    pipeline=DynamicBatchPipelineConfig(
        datamanager=VanillaDataManagerConfig(dataparser=BlenderDataParserConfig(), train_num_rays_per_batch=8192),
        model=InstantNGPModelConfig(eval_num_rays_per_chunk=8192),
    ),
    optimizers={
        "fields": {
            "optimizer": AdamOptimizerConfig(lr=1e-2, eps=1e-15),
            "scheduler": None,
        }
    },
    vis=["viewer"],
)

base_configs["proposal"] = Config(
    method_name="proposal",
    trainer=TrainerConfig(steps_per_eval_batch=500, steps_per_save=2000, mixed_precision=True),
    pipeline=VanillaPipelineConfig(
        datamanager=VanillaDataManagerConfig(
            dataparser=BlenderDataParserConfig(), train_num_rays_per_batch=4096, eval_num_rays_per_batch=8192
        ),
        model=ProposalModelConfig(eval_num_rays_per_chunk=8192),
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
    viewer=ViewerConfig(num_rays_per_chunk=2 << 15),
    vis=["viewer"],
)

base_configs["mipluxen-360"] = Config(
    method_name="mipluxen-360",
    trainer=TrainerConfig(steps_per_eval_batch=200),
    pipeline=VanillaPipelineConfig(
        datamanager=VanillaDataManagerConfig(dataparser=MipLuxen360DataParserConfig(), train_num_rays_per_batch=8192),
        model=VanillaModelConfig(
            _target=MipLuxen360Model,
            collider_params={"near_plane": 0.5, "far_plane": 20.0},
            loss_coefficients={"ray_loss_coarse": 1.0, "ray_loss_fine": 1.0},
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

base_configs["mipluxen"] = Config(
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

base_configs["luxenw"] = Config(
    method_name="luxenw",
    pipeline=VanillaPipelineConfig(
        datamanager=VanillaDataManagerConfig(
            dataparser=FriendsDataParserConfig(),
        ),
        model=LuxenWModelConfig(),
    ),
    optimizers={
        "fields": {
            "optimizer": RAdamOptimizerConfig(lr=5e-4, eps=1e-08),
            "scheduler": None,
        }
    },
)


base_configs["semantic-luxen"] = Config(
    method_name="semantic-luxen",
    pipeline=VanillaPipelineConfig(
        datamanager=VanillaDataManagerConfig(
            dataparser=FriendsDataParserConfig(),
        ),
        model=VanillaModelConfig(
            _target=SemanticLuxenModel,
            loss_coefficients={"rgb_loss_coarse": 1.0, "rgb_loss_fine": 1.0, "semantic_loss_fine": 0.05},
            num_coarse_samples=64,
            num_importance_samples=64,
        ),
    ),
    optimizers={
        "fields": {
            "optimizer": RAdamOptimizerConfig(lr=5e-4, eps=1e-08),
            "scheduler": None,
        }
    },
)

base_configs["vanilla-luxen"] = Config(
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

base_configs["tensorf"] = Config(
    method_name="tensorf",
    trainer=TrainerConfig(mixed_precision=True),
    pipeline=VanillaPipelineConfig(
        datamanager=VanillaDataManagerConfig(
            dataparser=BlenderDataParserConfig(),
        ),
        model=TensoRFModelConfig(),
    ),
    optimizers={
        "fields": {
            "optimizer": RAdamOptimizerConfig(lr=0.001),
            "scheduler": SchedulerConfig(lr_final=0.00005, max_steps=15000),
        },
        "position_encoding": {
            "optimizer": RAdamOptimizerConfig(lr=0.02),
            "scheduler": SchedulerConfig(lr_final=0.005, max_steps=15000),
        },
        "direction_encoding": {
            "optimizer": RAdamOptimizerConfig(lr=0.02),
            "scheduler": SchedulerConfig(lr_final=0.005, max_steps=15000),
        },
    },
)


AnnotatedBaseConfigUnion = dcargs.extras.subcommand_type_from_defaults(base_configs)
"""Union[] type over config types, annotated with default instances for use with
dcargs.cli(). Allows the user to pick between one of several base configurations, and
then override values in it."""
