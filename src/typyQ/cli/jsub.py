"""Submit typyQ jobs to the configured queue."""
from itertools import cycle
import argparse
import pickle
import time
from typing import Optional


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("pkl", type=str)
    parser.add_argument("-n", "--num-repeats", type=int, default=1)
    parser.add_argument("-p", "--ppri", type=int, default=None)
    parser.add_argument("-q", "--queue", type=str)
    parser.add_argument("-r", "--reset", action="store_true")
    parser.add_argument("-o", "--output", type=str, default="OUTPUTS")
    parser.add_argument("--qs_init", type=str)
    parser.add_argument("--qs", nargs="+")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    with open(args.pkl, "rb") as handle:
        job = pickle.load(handle)

    if args.queue:
        job.set_queue_name(args.queue)

    if args.reset:
        job.run_number = 0
        job.dependent_on = None

    if args.qs:
        qs_cycle = cycle(args.qs)
    elif job.queue_file:
        qs_cycle = cycle([job.queue_file])
    else:
        raise ValueError("Queue script must be specified via --qs or in job pkl!")

    for _ in range(args.num_repeats):
        if job.run_number == 0 and args.qs_init:
            job.set_queue_file(args.qs_init)
        else:
            job.set_queue_file(next(qs_cycle))

        job.submit()
        time.sleep(1)

    with open(args.pkl, "wb") as handle:
        pickle.dump(job, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
