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


"""This file contains the configuration for external methods which are not included in this repository."""
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, cast

from rich.prompt import Confirm

from luxenstudio.engine.trainer import TrainerConfig
from luxenstudio.utils.rich_utils import CONSOLE


@dataclass
class ExternalMethod:
    """External method class. Represents a link to a luxenstudio-compatible method not included in this repository."""

    instructions: str
    """Instructions for installing the method. This will be printed to
    the console when the user tries to use the method."""
    configurations: List[Tuple[str, str]]
    """List of configurations for the method. Each configuration is a tuple of (registered slug, description)
    as it will be printed in --help."""
    pip_package: Optional[str] = None
    """Specifies a pip package if the method can be installed by running `pip install <pip_package>`."""


external_methods = []

# Instruct-Luxen2Luxen
external_methods.append(
    ExternalMethod(
        """[bold yellow]Instruct-Luxen2Luxen[/bold yellow]
For more information visit: https://docs.luxen.studio/en/latest/luxenology/methods/in2n.html

To enable Instruct-Luxen2Luxen, you must install it first by running:
  [grey]pip install git+https://github.com/ayaanzhaque/instruct-luxen2luxen[/grey]""",
        configurations=[
            ("in2n", "Instruct-Luxen2Luxen. Full model, used in paper"),
            ("in2n-small", "Instruct-Luxen2Luxen. Half precision model"),
            ("in2n-tiny", "Instruct-Luxen2Luxen. Half prevision with no LPIPS"),
        ],
        pip_package="git+https://github.com/ayaanzhaque/instruct-luxen2luxen",
    )
)


# LERF
external_methods.append(
    ExternalMethod(
        """[bold yellow]LERF[/bold yellow]
For more information visit: https://docs.luxen.studio/en/latest/luxenology/methods/lerf.html

To enable LERF, you must install it first by running:
  [grey]pip install git+https://github.com/kerrj/lerf[/grey]""",
        configurations=[
            ("lerf-big", "LERF with OpenCLIP ViT-L/14"),
            ("lerf", "LERF with OpenCLIP ViT-B/16, used in paper"),
            ("lerf-lite", "LERF with smaller network and less LERF samples"),
        ],
        pip_package="git+https://github.com/kerrj/lerf",
    )
)

# Tetra-Luxen
external_methods.append(
    ExternalMethod(
        """[bold yellow]Tetra-Luxen[/bold yellow]
For more information visit: https://docs.luxen.studio/en/latest/luxenology/methods/tetraluxen.html

To enable Tetra-Luxen, you must install it first. Please follow the instructions here:
  https://github.com/jkulhanek/tetra-luxen/blob/master/README.md#installation""",
        configurations=[
            ("tetra-luxen-original", "Tetra-Luxen. Official implementation from the paper"),
            ("tetra-luxen", "Tetra-Luxen. Different sampler - faster and better"),
        ],
    )
)


@dataclass
class ExternalMethodTrainerConfig(TrainerConfig):
    """
    Trainer config for external methods which does not have an implementation in this repository.
    """

    _method: ExternalMethod = field(default=cast(ExternalMethod, None))

    def handle_print_information(self, *_args, **_kwargs):
        """Prints the method information and exits."""
        CONSOLE.print(self._method.instructions)
        if self._method.pip_package and Confirm.ask(
            "\nWould you like to run the install it now?", default=False, console=CONSOLE
        ):
            # Install the method
            install_command = f"{sys.executable} -m pip install {self._method.pip_package}"
            CONSOLE.print(f"Running: [cyan]{install_command}[/cyan]")
            result = subprocess.run(install_command, shell=True, check=False)
            if result.returncode != 0:
                CONSOLE.print("[bold red]Error installing method.[/bold red]")
                sys.exit(1)

        sys.exit(0)

    def __getattribute__(self, __name: str) -> Any:
        out = object.__getattribute__(self, __name)
        if callable(out) and __name not in {"handle_print_information"} and not __name.startswith("__"):
            # We exit early, displaying the message
            return self.handle_print_information
        return out


def get_external_methods() -> Tuple[Dict[str, TrainerConfig], Dict[str, str]]:
    """Returns the external methods trainer configs and the descriptions."""
    method_configs = {}
    descriptions = {}
    for external_method in external_methods:
        for config_slug, config_description in external_method.configurations:
            method_configs[config_slug] = ExternalMethodTrainerConfig(method_name=config_slug, _method=external_method)
            descriptions[config_slug] = f"""[External] {config_description}"""
    return method_configs, descriptions
