"""Display queue status in a concise table."""
from __future__ import annotations

import argparse
from getpass import getuser
from typing import Iterable, Optional

import typyQ.reader

QUEUE_CHOICES = {"SLURM", "UGE"}


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show queued and running jobs")
    parser.add_argument("-q", "--qtype", choices=sorted(QUEUE_CHOICES), default="SLURM")
    parser.add_argument("-u", "--user", help="Filter by a specific user")
    parser.add_argument("--me", action="store_true", help="Only show jobs for the current user")
    parser.add_argument("-a", "--all", action="store_true", help="Show all jobs")
    return parser.parse_args(argv)


def _resolve_user_filter(args: argparse.Namespace) -> str | None:
    if args.all:
        return None
    if args.me:
        return getuser()
    return args.user


def _read_queue(qtype: str, user_filter: str | None):
    if qtype == "SLURM":
        return typyQ.reader.SLURM.read_queue(user_filter)
    if qtype == "UGE":
        return typyQ.reader.UGE.read_queue(user_filter)
    raise ValueError(f"Unknown queue type: {qtype}")


def _format_table(jobs: Iterable) -> list[str]:
    rows = []
    headers = ["JOBID", "USER", "STATE", "QUEUE", "RUNTIME", "CORES", "GPU", "NAME"]
    job_rows = []
    for job in jobs:
        job_rows.append(
            [
                str(job.num),
                job.user,
                job.state,
                job.queue or ("preempt" if job.standby else "OU"),
                job.runtime or "-",
                str(job.num_cores),
                str(job.gpu) if job.gpu is not None else "-",
                job.name,
            ]
        )

    if not job_rows:
        return ["No jobs found."]

    widths = [len(header) for header in headers]
    for row in job_rows:
        widths = [max(w, len(col)) for w, col in zip(widths, row)]

    fmt = "  ".join(f"{{:{width}}}" for width in widths)
    rows.append(fmt.format(*headers))
    rows.append("  ".join("-" * width for width in widths))
    for row in job_rows:
        rows.append(fmt.format(*row))
    return rows


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    user_filter = _resolve_user_filter(args)
    jobs = sorted(_read_queue(args.qtype, user_filter), key=lambda job: (job.user, job.num))

    for line in _format_table(jobs):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
