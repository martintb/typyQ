import logging
import shlex
import subprocess

from .GridEngine import GridEngineJob


logger = logging.getLogger(__name__)

class RuthJob(GridEngineJob):
  def __init__(self):
    super(RuthJob,self).__init__()
  def check(self):
    pass
  def build_argList(self):
    self.check()

    argList = super(RuthJob,self).build_argList()

    if self.dependent_on:
      check_command = shlex.split('qstat -j {:d}'.format(self.dependent_on))
      try:
        jid_check = subprocess.check_output(check_command, text=True, stderr=subprocess.STDOUT)
      except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        logger.warning(
          'Ignoring hold request: cannot find job %d in queue (%s)',
          self.dependent_on,
          getattr(exc, 'output', str(exc)).strip(),
        )
      else:
        argList.append('-hold_jid {:d}'.format(self.dependent_on))

    argList.append('{:s}'.format(self.queue_file))

    return argList
