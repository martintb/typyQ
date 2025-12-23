"""Display typyQ job pickle contents."""
import argparse
import pickle
from typing import Any, Optional


def print_job(job: Any) -> None:
    for key, val in vars(job).items():
        print(f"{key:20s}: {val!s}")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("pkl", type=str)
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    print(f">>> Reading job file: {args.pkl}")
    with open(args.pkl, "rb") as handle:
        job = pickle.load(handle)

    print_job(job)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
