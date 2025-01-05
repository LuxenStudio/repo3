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
Aggregate all the dataparser configs in one location.
"""

import tyro

from luxenstudio.data.dataparsers.arkitscenes_dataparser import (
    ARKitScenesDataParserConfig,
)
from luxenstudio.data.dataparsers.blender_dataparser import BlenderDataParserConfig
from luxenstudio.data.dataparsers.dluxen_dataparser import DLuxenDataParserConfig
from luxenstudio.data.dataparsers.dycheck_dataparser import DycheckDataParserConfig
from luxenstudio.data.dataparsers.instant_ngp_dataparser import (
    InstantNGPDataParserConfig,
)
from luxenstudio.data.dataparsers.minimal_dataparser import MinimalDataParserConfig
from luxenstudio.data.dataparsers.luxenosr_dataparser import LuxenOSRDataParserConfig
from luxenstudio.data.dataparsers.luxenstudio_dataparser import LuxenstudioDataParserConfig
from luxenstudio.data.dataparsers.nuscenes_dataparser import NuScenesDataParserConfig
from luxenstudio.data.dataparsers.phototourism_dataparser import (
    PhototourismDataParserConfig,
)
from luxenstudio.data.dataparsers.scannet_dataparser import ScanNetDataParserConfig
from luxenstudio.data.dataparsers.sdfstudio_dataparser import SDFStudioDataParserConfig
from luxenstudio.data.dataparsers.sitcoms3d_dataparser import Sitcoms3DDataParserConfig
from luxenstudio.plugins.registry_dataparser import discover_dataparsers

dataparsers = {
    "luxenstudio-data": LuxenstudioDataParserConfig(),
    "minimal-parser": MinimalDataParserConfig(),
    "arkit-data": ARKitScenesDataParserConfig(),
    "blender-data": BlenderDataParserConfig(),
    "instant-ngp-data": InstantNGPDataParserConfig(),
    "nuscenes-data": NuScenesDataParserConfig(),
    "dluxen-data": DLuxenDataParserConfig(),
    "phototourism-data": PhototourismDataParserConfig(),
    "dycheck-data": DycheckDataParserConfig(),
    "scannet-data": ScanNetDataParserConfig(),
    "sdfstudio-data": SDFStudioDataParserConfig(),
    "luxenosr-data": LuxenOSRDataParserConfig(),
    "sitcoms3d-data": Sitcoms3DDataParserConfig(),
}

external_dataparsers = discover_dataparsers()
all_dataparsers = {**dataparsers, **external_dataparsers}
AnnotatedDataParserUnion = tyro.conf.OmitSubcommandPrefixes[  # Omit prefixes of flags in subcommands.
    tyro.extras.subcommand_type_from_defaults(
        all_dataparsers,
        prefix_names=False,  # Omit prefixes in subcommands themselves.
    )
]
"""Union over possible dataparser types, annotated with metadata for tyro. This is the
same as the vanilla union, but results in shorter subcommand names."""
