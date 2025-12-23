"""Create typyQ job configuration files and optional queue scripts."""
import argparse
import pathlib
from typing import Optional

from typyQ import job
from typyQ.job.model import DEFAULT_EXTENSION, normalize_job_path, save_job


QUEUE_SCRIPT = """#!/bin/bash -l
# export OMP_NUM_THREADS=8
set -e

source ~/.typyEnv CLEAN
typyEnv --add python
typyEnv --add typySetup
typyEnv --add typySim
# typyEnv --add typyAnalyze
# typyEnv --add typyCreator
# typyEnv --add lammps

cd ${SGE_O_WORKDIR}

python sim.py >OUTPUTS
# mpirun python sim.py >OUTPUTS
# mpirun lammps -i in.lammps > OUTPUTS

touch DONE
"""


JOB_TYPES = {
    "ruth": job.RuthJob,
    "farber": job.FarberJob,
    "raritan": job.RARITANJob,
}


def write_queue_script(path: pathlib.Path) -> None:
    path.write_text(QUEUE_SCRIPT)
    path.chmod(path.stat().st_mode | 0o111)
    print(f">>> Making generic run script \"{path.name}\"")


def write_job_config(path: pathlib.Path, job_type: Optional[type]) -> None:
    if job_type is None:
        return
    print(f'>>> Making empty job file "{path.name}" of type "{job_type.__name__}"')
    save_job(path, job_type())


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "name",
        type=pathlib.Path,
        help=f"Base name for job configuration (defaults to {DEFAULT_EXTENSION})",
    )
    parser.add_argument("--qs", action="store_true", help="Also write a generic queue script")

    job_type_group = parser.add_mutually_exclusive_group()
    job_type_group.add_argument("--ruth", dest="job_type", action="store_const", const="ruth")
    job_type_group.add_argument("--farber", dest="job_type", action="store_const", const="farber")
    job_type_group.add_argument("--raritan", dest="job_type", action="store_const", const="raritan")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    job_type = JOB_TYPES.get(args.job_type) if args.job_type else None
    target_path = normalize_job_path(args.name)

    if job_type is None and not args.qs:
        print(
            ">>> If you've made it here, there is a good chance you are not using this tool correctly.\n"
            ">> Use the --qs flag to direct this tool to create a generic queue script,\n"
            ">> or specify a jobType to create a generic, empty job configuration file.\n"
            ">> See the help output below for more information."
        )
        parse_args(["-h"])
        return 1

    write_job_config(target_path, job_type)
    if args.qs:
        write_queue_script(pathlib.Path("run.qs"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
