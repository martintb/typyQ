"""Submit typyQ jobs to the configured queue."""
from itertools import cycle
import argparse
import logging
import time
from typing import Optional

from typyQ.job.Job import JobConfigurationError, JobSubmissionError
from typyQ.job.model import load_job, save_job


logger = logging.getLogger(__name__)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("job_file", type=str, help="Path to job configuration (.job.toml)")
    parser.add_argument("-n", "--num-repeats", type=int, default=1)
    parser.add_argument("-p", "--ppri", type=int, default=None)
    parser.add_argument("-q", "--queue", type=str)
    parser.add_argument("-r", "--reset", action="store_true")
    parser.add_argument("-o", "--output", type=str, default="OUTPUTS")
    parser.add_argument("--qs_init", type=str)
    parser.add_argument("--qs", nargs="+")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args(argv)
    job, target_path, migrated = load_job(args.job_file)
    if migrated:
        logger.info("Migrated legacy pickle to %s", target_path)

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
        raise ValueError("Queue script must be specified via --qs or in the job file!")

    for _ in range(args.num_repeats):
        if job.run_number == 0 and args.qs_init:
            job.set_queue_file(args.qs_init)
        else:
            job.set_queue_file(next(qs_cycle))

        try:
            job.submit()
        except FileNotFoundError as exc:
            logger.error("Required file missing: %s", exc)
            return 1
        except JobConfigurationError as exc:
            logger.error("Invalid job configuration: %s", exc)
            return 2
        except JobSubmissionError as exc:
            logger.error("Job submission failed: %s", exc)
            return 3
        except Exception:
            logger.exception("Unexpected error during job submission")
            return 4

        time.sleep(1)

    save_job(target_path, job)
    logger.info("Updated job state saved to %s", target_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
