"""Display typyQ job configuration contents."""
import argparse
from typing import Any, Optional

from typyQ.job.model import load_job


def print_job(job: Any) -> None:
    for key, val in vars(job).items():
        print(f"{key:20s}: {val!s}")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("job_file", type=str, help="Path to job configuration (.job.toml)")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    job, target_path, migrated = load_job(args.job_file)

    print(f">>> Reading job file: {target_path}")
    if migrated:
        print(f">>> Migrated legacy pickle to {target_path}")

    print_job(job)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
