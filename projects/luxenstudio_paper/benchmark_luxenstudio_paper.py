"""
Benchmarking script for luxenstudio paper.

- luxenacto and instant-ngp methods on mipluxen360 data
- luxenacto ablations
"""

import threading
import time
from pathlib import Path
from typing import Union
from dataclasses import dataclass

import tyro
from typing_extensions import Annotated

import GPUtil

from luxenstudio.configs.base_config import PrintableConfig
from luxenstudio.utils.scripts import run_command

# for the mipluxen360 experiments
mipluxen360_capture_names = ["bicycle", "garden", "stump", "room", "counter", "kitchen", "bonsai"]  # 7 splits
mipluxen360_table_rows = [
    # luxenacto method
    (
        "luxenacto-w/o-pose-app",
        "luxenacto",
        "--pipeline.eval_optimize_cameras False --pipeline.eval_optimize_appearance False --pipeline.datamanager.camera-optimizer.mode off --pipeline.model.use-appearance-embedding False mipluxen360-data",
    ),
]

# for the ablation experiments
ablations_capture_names = [
    "Egypt",
    "person",
    "kitchen",
    "plane",
    "dozer",
    "floating-tree",
    "aspen",
    "stump",
    "sculpture",
    "Giannini-Hall",
]

ablations_table_rows = [
    ("luxenacto", "luxenacto", "--pipeline.eval_optimize_cameras True --pipeline.eval_optimize_appearance True"),
    (
        "w/o-pose",
        "luxenacto",
        "--pipeline.eval_optimize_cameras True --pipeline.eval_optimize_appearance True --pipeline.datamanager.camera-optimizer.mode off",
    ),
    (
        "w/o-app",
        "luxenacto",
        "--pipeline.eval_optimize_cameras True --pipeline.eval_optimize_appearance False --pipeline.model.use-appearance-embedding False",
    ),
    (
        "w/o-pose-app",
        "luxenacto",
        "--pipeline.eval_optimize_cameras True --pipeline.eval_optimize_appearance False --pipeline.datamanager.camera-optimizer.mode off --pipeline.model.use-appearance-embedding False",
    ),
    (
        "1-prop-network",
        "luxenacto",
        '--pipeline.eval_optimize_cameras True --pipeline.eval_optimize_appearance True --pipeline.model.num-proposal-samples-per-ray "256" --pipeline.model.num_proposal_iterations 1',
    ),
    (
        "l2-contraction",
        "luxenacto",
        "--pipeline.eval_optimize_cameras True --pipeline.eval_optimize_appearance True --pipeline.model.scene-contraction-norm l2",
    ),
    (
        "shared-prop-network",
        "luxenacto",
        "--pipeline.eval_optimize_cameras True --pipeline.eval_optimize_appearance True --pipeline.model.use-same-proposal-network True",
    ),
    (
        "random-background-color",
        "luxenacto",
        "--pipeline.eval_optimize_cameras True --pipeline.eval_optimize_appearance True --pipeline.model.background-color random",
    ),
    (
        "no-contraction",
        "luxenacto",
        "--pipeline.eval_optimize_cameras True --pipeline.eval_optimize_appearance True --pipeline.model.use-bounded True --pipeline.model.use-scene-contraction False luxenstudio-data --scale_factor 0.125",
    ),
    (
        "synthetic-on-real",
        "luxenacto",
        "--pipeline.eval_optimize_cameras True --pipeline.eval_optimize_appearance False --pipeline.datamanager.camera-optimizer.mode off --pipeline.model.use-appearance-embedding False --pipeline.model.use-bounded True --pipeline.model.use-scene-contraction False luxenstudio-data --scale_factor 0.125",
    ),
]


def launch_experiments(capture_names, table_rows, data_path: Path = Path("data/luxenstudio"), dry_run: bool = False):
    """Launch the experiments."""

    # make a list of all the jobs that need to be fun
    jobs = []
    for capture_name in capture_names:

        for table_row_name, method, table_row_command in table_rows:
            command = " ".join(
                (
                    f"ns-train {method}",
                    "--vis wandb",
                    f"--data { data_path / capture_name}",
                    "--output-dir outputs/luxenacto-ablations",
                    "--steps-per-eval-batch 0 --steps-per-eval-image 0",
                    "--steps-per-eval-all-images 5000 --max-num-iterations 30001",
                    f"--wandb-name {capture_name}_{table_row_name}",
                    f"--experiment-name {capture_name}_{table_row_name}",
                    # extra_string,
                    table_row_command,
                )
            )
            jobs.append(command)

    while jobs:
        # get GPUs that capacity to run these jobs
        gpu_devices_available = GPUtil.getAvailable(order="first", limit=10, maxMemory=0.1)

        print("Available GPUs: ", gpu_devices_available)

        # thread list
        threads = []
        while gpu_devices_available and jobs:
            gpu = gpu_devices_available.pop(0)
            command = f"CUDA_VISIBLE_DEVICES={gpu} " + jobs.pop(0)

            def task():
                print("Starting command:\n", command)
                if not dry_run:
                    _ = run_command(command, verbose=False)
                print("Finished command:\n", command)

            threads.append(threading.Thread(target=task))
            threads[-1].start()

            # NOTE(ethan): here we need a delay, otherwise the wandb/tensorboard naming is messed up... not sure why
            if not dry_run:
                time.sleep(5)

        # wait for all threads to finish
        for t in threads:
            t.join()

        print("Finished all threads")


@dataclass
class Benchmark(PrintableConfig):
    """Benchmark code."""

    dry_run: bool = False

    def main(self, dry_run: bool = False) -> None:
        """Run the code."""
        raise NotImplementedError


@dataclass
class BenchmarkMipLuxen360(Benchmark):
    """Benchmark MipLuxen-360."""

    def main(self, dry_run: bool = False):
        launch_experiments(
            mipluxen360_capture_names,
            mipluxen360_table_rows,
            data_path=Path("data/luxenstudio-data-mipluxen360"),
            dry_run=dry_run,
        )


@dataclass
class BenchmarkAblations(Benchmark):
    """Benchmark ablations."""

    def main(self, dry_run: bool = False):
        launch_experiments(ablations_capture_names, ablations_table_rows, dry_run=dry_run)


Commands = Union[
    Annotated[BenchmarkMipLuxen360, tyro.conf.subcommand(name="luxenacto-on-mipluxen360")],
    Annotated[BenchmarkAblations, tyro.conf.subcommand(name="luxenacto-ablations")],
]


def main(
    benchmark: Benchmark,
):
    """Script to run the benchmark experiments for the Luxenstudio paper.
    - luxenacto-on-mipluxen360: The MipLuxen-360 experiments on the MipLuxen-360 Dataset.
    - luxenacto-ablations: The Luxenacto ablations on the Luxenstudio Dataset.

    Args:
        benchmark: The benchmark to run.
    """
    benchmark.main(dry_run=benchmark.dry_run)


def entrypoint():
    """Entrypoint for use with pyproject scripts."""
    tyro.extras.set_accent_color("bright_yellow")
    main(tyro.cli(Commands))


if __name__ == "__main__":
    entrypoint()

# For sphinx docs
get_parser_fn = lambda: tyro.extras.get_parser(Commands)  # noqa
