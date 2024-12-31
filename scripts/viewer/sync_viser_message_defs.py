"""Generate viser message definitions for TypeScript, by parsing Python dataclasses."""
import json
import pathlib
from datetime import datetime

import tyro
from viser.infra import generate_typescript_interfaces

from luxenstudio.viewer.viser import LuxenstudioMessage


def main() -> None:
    """Generate viser message definitions for TypeScript, by parsing Python dataclasses."""

    # Generate typescript source.
    defs = generate_typescript_interfaces(LuxenstudioMessage)

    # Write to file.
    # Three parents from luxenstudio/scripts/viewer/sync_viser_message_defs.py:
    # - luxenstudio/scripts/viewer/
    # - luxenstudio/scripts/
    # - luxenstudio/
    target_path = pathlib.Path(__file__).absolute().parent.parent.parent / pathlib.Path(
        "luxenstudio/viewer/app/src/modules/WebSocket/ViserMessages.tsx"
    )
    assert target_path.exists()

    old_defs = target_path.read_text(encoding="utf_8")

    if old_defs != defs:
        target_path.write_text(defs, encoding="utf_8")

        with open("luxenstudio/viewer/app/package.json", "r", encoding="utf_8") as f:
            data = json.load(f)

        now = datetime.now()
        data["version"] = now.strftime("%y-%m-%d") + "-0"

        with open("luxenstudio/viewer/app/package.json", "w", encoding="utf_8") as f:
            json.dump(data, f, indent=2)
        print(f"Wrote updates to {target_path}")
        print(f"Current viewer version is now {data['version']}")
    else:
        print("No update to messages.")


def entrypoint() -> None:
    """Entrypoint for use with pyproject scripts."""
    # All entrypoints must currently be tyro CLIs.
    tyro.cli(main)


if __name__ == "__main__":
    entrypoint()
