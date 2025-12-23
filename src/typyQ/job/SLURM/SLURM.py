import logging
import re
import shlex
import subprocess

from ..Job import Job


logger = logging.getLogger(__name__)

class SLURMJob(Job):
  def __init__(self):
    super(SLURMJob,self).__init__()
    self.dependency_type='afterok'
    self.notify = None
    self.notify_signal = 'SIGTERM'
  def parse_submission_id(self,qsub_out):
    return int(re.findall('Submitted batch job ([0-9]*)',qsub_out)[0])

  def submission_cmd(self):
    argList = []
    argList.append('sbatch')
    argList.append('-t {:02d}:00:00'.format(self.walltime))

    if self.node:
      argList.append('--nodelist={}'.format(self.node))

    if self.export_env:
      argList.append('--export=ALL') # one task

    if self.num_procs:
      argList.append('-n {:d}'.format(self.num_procs)) # one task

    if self.exclusive:
      argList.append('--exclusive'.format(self.queue_name))

    if self.memory:
      argList.append('--mem-per-cpu={:d}gb'.format(self.memory))

    if self.gpu:
      try:
        gpu_count = int(self.gpu)
      except (TypeError, ValueError):
        gpu_count = 1
      else:
        if gpu_count < 1:
          gpu_count = 1

      argList.append('--gres=gpu:{:d}'.format(gpu_count))

    if self.queue_name:
      argList.append('-p {}'.format(self.queue_name))

    if self.name:
      argList.append('--job-name={:s}_{:d}'.format(self.name,self.run_number))

    if self.email:
      argList.append('--mail-type=ALL')
      argList.append('--mail-user={}'.format(self.email))

    if self.notify is not None:
      argList.append('--signal=B:{}@{}'.format(self.notify_signal,self.notify))

    if self.dependent_on:
      check_command = shlex.split('squeue -j {:d}'.format(self.dependent_on))
      try:
        jid_check = subprocess.check_output(check_command, text=True, stderr=subprocess.STDOUT)
      except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        logger.warning(
          'Ignoring hold request: cannot find job %d in queue (%s)',
          self.dependent_on,
          getattr(exc, 'output', str(exc)).strip(),
        )
      else:
        if re.search(self.user,jid_check):
          argList.append('--dependency={:s}:{:d}'.format(self.dependency_type,self.dependent_on))
        else:
          logger.warning(
            'Ignoring hold request: User does not own dependent job or job is not eligible for dependency'
          )

    argList.append('{:s}'.format(self.queue_file))
    return argList

