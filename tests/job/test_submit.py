import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.modules.setdefault("tomli_w", types.SimpleNamespace(dump=lambda *_, **__: None))

from typyQ.job.Job import Job, JobSubmissionError


class DummyJob(Job):
    def __init__(self):
        super().__init__()
        self.check_called = False
        self.cmd_called = False

    def check(self):
        self.check_called = True

    def submission_cmd(self):
        self.cmd_called = True
        return ["echo", "101"]

    def parse_submission_id(self, output):
        return int(output.strip())


class SubmitRetryJob(Job):
    def __init__(self):
        super().__init__()

    def submission_cmd(self):
        return ["echo", "55"]

    def parse_submission_id(self, output):
        return int(output.strip())


class SubmissionCmdMissingJob(Job):
    def submission_cmd(self):
        return None


class JobSubmitTests(unittest.TestCase):
    def test_submit_runs_hooks_and_tracks_dependency(self):
        job = DummyJob()
        with tempfile.NamedTemporaryFile() as queue_file:
            job.set_queue_file(queue_file.name)

            with patch("subprocess.check_output", return_value="202\n") as mocked_check:
                job.submit()

        mocked_check.assert_called_with(["echo", "101"], text=True, stderr=subprocess.STDOUT)
        self.assertTrue(job.check_called)
        self.assertTrue(job.cmd_called)
        self.assertEqual(job.dependent_on, 202)
        self.assertEqual(job.run_number, 1)

    def test_submit_retries_failed_command(self):
        job = SubmitRetryJob()
        with tempfile.NamedTemporaryFile() as queue_file, patch("time.sleep") as mocked_sleep:
            job.set_queue_file(queue_file.name)

            failure = subprocess.CalledProcessError(returncode=1, cmd="echo", output="error")
            with patch("subprocess.check_output", side_effect=[failure, "77\n"]) as mocked_check:
                job.submit()

        self.assertEqual(mocked_check.call_count, 2)
        mocked_sleep.assert_called_once()
        self.assertEqual(job.dependent_on, 77)
        self.assertEqual(job.run_number, 1)

    def test_missing_submission_cmd_raises(self):
        job = SubmissionCmdMissingJob()
        with tempfile.NamedTemporaryFile() as queue_file:
            job.set_queue_file(queue_file.name)

            with self.assertRaises(JobSubmissionError):
                job.submit()


if __name__ == "__main__":
    unittest.main()
