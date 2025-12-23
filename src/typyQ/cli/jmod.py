"""Modify typyQ job pickle files."""
import argparse
import pickle
from typing import Any, Optional

try:
    import ipdb
except ImportError:  # pragma: no cover - optional dependency
    ipdb = None


def print_job(job: Any) -> None:
    for key, val in vars(job).items():
        print(f"{key:20s}: {val!s:10s}")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("pkl", type=str)
    parser.add_argument("-s", "--set", nargs=3, type=str)
    if ipdb is not None:
        parser.add_argument("-i", "--iset", action="store_true")
    return parser.parse_args(argv)


def interactive_edit(job: Any) -> None:
    if ipdb is None:
        raise RuntimeError("Interactive editing requires the optional 'ipdb' dependency.")

    print("-----------------------------------------------------------------")
    print_job(job)
    print("-----------------------------------------------------------------")
    print(
        ">>> Run \"print_job(job)\" to see current contents of job\n"
        ">>> Job attributes can be set via \"job.<attribute>=value\"\n"
        ">>> Run \"q\" to quit modification without saving\n"
        ">>> Run \"c\" to write modifications to the pkl.\n"
        "-----------------------------------------------------------------"
    )
    ipdb.set_trace()
    print(">>> Writing job modifications to disk!")


def apply_set(job: Any, attr: str, val: str, val_type: str) -> None:
    converters = {
        "int": int,
        "float": float,
        "bool": lambda x: x == "True",
        "str": str,
        "None": lambda _: None,
    }
    try:
        val = converters[val_type](val)
    except KeyError:
        raise ValueError(f"Variable type must be one of {sorted(converters)}, not {val_type}")

    print(f">>> Setting {attr} to {val}")
    setattr(job, attr, val)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    print(f">>> Reading job file: {args.pkl}")
    with open(args.pkl, "rb") as handle:
        job = pickle.load(handle)

    wrote_changes = False
    if getattr(args, "iset", False):
        interactive_edit(job)
        wrote_changes = True
    elif args.set:
        apply_set(job, *args.set)
        wrote_changes = True
    else:
        print(f">>> JobClass: {job.__class__.__name__}")
        print("-----------------------------------------------------------------")
        print_job(job)
        print("-----------------------------------------------------------------")

    if wrote_changes:
        with open(args.pkl, "wb") as handle:
            pickle.dump(job, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
