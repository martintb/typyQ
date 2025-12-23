"""Inspect queue dependencies."""
import argparse
from typing import Iterable, Optional

import typyQ.reader


STANDBY_MAP = {True: "preempt", False: "OU"}


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--qtype", default="SLURM")
    parser.add_argument("-l", "--list", action="store_true")
    parser.add_argument("-u", "--user", default="tbm")
    parser.add_argument("-a", "--all", action="store_true")
    return parser.parse_args(argv)


def _format_jobs(job_group: Iterable) -> str:
    job_list = list(job_group)
    user = job_list[0].user
    name = job_list[0].name
    size = job_list[0].num_cores
    queue = STANDBY_MAP[job_list[0].standby]
    num_jobs = len(job_list)

    job_string = "{user:<{ulen}}  {name:<{nlen}}  {queue:<7s} ({num:03d}x{size:03d}){jobs:13s}"
    job_list_str = (
        f"[{job_list[0].stateno}...{job_list[-1].stateno}]"
        if num_jobs > 1
        else f"[{job_list[0].stateno}]"
    )
    return job_string.format(
        user=user,
        ulen=len(user) + 2,
        name=name,
        nlen=len(name) + 2,
        queue=queue,
        num=num_jobs,
        size=size,
        jobs=job_list_str,
    )


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    user = None if args.all else args.user

    if args.qtype == "SLURM":
        job_list = typyQ.reader.SLURM.read_queue(user)
    elif args.qtype == "UGE":
        job_list = typyQ.reader.UGE.read_queue(user)
    else:
        raise ValueError(f"Unknown queue type: {args.qtype}")

    job_groups = typyQ.reader.util.parse_jobs(job_list)

    if args.list:
        for job_group in job_groups:
            first = job_group[0]
            print(first.user, first.name, STANDBY_MAP[first.standby], len(job_group), "x", first.num_cores)
            for job in job_group:
                print(job.stateno)
    else:
        for job_group in job_groups:
            print(_format_jobs(job_group))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
