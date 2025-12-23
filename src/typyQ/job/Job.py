from getpass import getuser
import logging
import os
import re
import shlex
import subprocess
import time


logger = logging.getLogger(__name__)


class JobConfigurationError(Exception):
  """Raised when job configuration is invalid."""


class JobSubmissionError(Exception):
  """Raised when job submission fails."""

class Job(object):
  def __init__(self):
    self.run_number = 0
    self.walltime = 4
    self.exclusive = False
    self.memory = None
    self.virtual_memory = None
    self.dependent_on = None
    self.num_procs=1
    self.queue_file = None
    self.queue_name= None
    self.name = None
    self.email= None
    self.user = getuser()
    self.export_env=False
    self.node=None
    self.gpu=False
    # print 'Creating job for',self.user
  def set_queue_file(self,fname,ignoreCheck=False):
    if ignoreCheck or os.path.exists(fname):
      self.queue_file = fname
      logger.info('Setting queue file to %s', fname)
    else:
      message = "The queue file you specified doesn't seem to exist: {:s}".format(fname)
      logger.error(message)
      raise FileNotFoundError(message)
  def default_checks(self):
    if not self.queue_file:
      message = 'You must call job.set_queue_file(path_to_queue_file) before submission'
      logger.error(message)
      raise JobConfigurationError(message)
  def submit(self):
    self.default_checks()

    argList = self.build_argList()
    command = ' '.join(argList)

    logger.info('Submitting job using: %s', command)
    submission_attempts = 0
    while True:
      try:
        qsub_out = subprocess.check_output(
          shlex.split(command), text=True, stderr=subprocess.STDOUT
        )
      except FileNotFoundError as exc:
        message = f'Submission command not found: {command}'
        logger.exception(message)
        raise JobSubmissionError(message) from exc
      except subprocess.CalledProcessError as exc:
        submission_attempts += 1
        logger.warning(
          'Job submission failed (attempt %d): %s',
          submission_attempts,
          exc.output.strip(),
        )
        if submission_attempts >= 3:
          raise JobSubmissionError(
            f'Submission failed after {submission_attempts} attempts: {exc.output.strip()}'
          ) from exc
        time.sleep(submission_attempts)
        continue
      else:
        logger.info('Submission output: %s', qsub_out.strip())
        break

    try:
      self.update_dependency(qsub_out)
    except Exception as exc:
      logger.exception('Failed to parse submission output: %s', qsub_out)
      raise JobSubmissionError('Unable to parse submission output for dependency tracking') from exc

    self.run_number+=1

