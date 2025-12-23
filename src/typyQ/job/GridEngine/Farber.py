import logging
import re
import shlex
import subprocess

from .GridEngine import GridEngineJob
from ..Job import JobConfigurationError


logger = logging.getLogger(__name__)

class FarberJob(GridEngineJob):
  def __init__(self):
    super(FarberJob,self).__init__()
    self.ppri = None
    self.gpu=False
    self.standby=False
  def set_walltime(self,walltime):
    if walltime<=24:
      self.walltime = int(walltime)
      logger.info("Setting a walltime of %d hours", self.walltime)
    else:
      message = (
        "Please use a maximum walltime of 24 hours for our queue. "
        "You requested a {:d} hour walltime.".format(int(walltime))
      )
      logger.error(message)
      raise JobConfigurationError(message)
  def check(self):
    if self.ppri is None:
      message = 'You must call job.set_priority(ppri) before submission'
      logger.error(message)
      raise JobConfigurationError(message)
  def set_priority(self,ppri):
    if isinstance(ppri,dict):
      if ppri['all'].max<ppri[self.user].min:
        self.ppri = ppri['all'].max
      else:
        self.ppri = ppri[self.user].min-1
    else:
      self.ppri = ppri
  def submission_cmd(self):
    argList = super(FarberJob,self).submission_cmd()

    if self.standby:
      argList.append('-l standby=1')

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
        if not self.standby:
          #update ppri to follow this jobs dependency
          self.ppri = int(re.findall(r'priority:\s*(\-?[0-9]*)', jid_check)[0]) - 1

    if not self.standby:
      argList.append('-p {:d}'.format(self.ppri))

    if self.gpu:
      argList.append('-l nvidia_gpu=1')

    argList.append('{:s}'.format(self.queue_file))

    return argList
