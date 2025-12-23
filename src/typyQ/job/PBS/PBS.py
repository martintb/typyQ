import logging
import re
import shlex
import subprocess

from ..Job import Job


logger = logging.getLogger(__name__)

class PBSJob(Job):
  def __init__(self):
    super(PBSJob,self).__init__()
    self.gpu=False
  def update_dependency(self,qsub_out):
    self.dependent_on = int(qsub_out.strip().split('.')[0])
  def check(self):
    pass
  def build_argList(self):
    self.check()
    argList = []
    argList.append('qsub')
    argList.append('-j oe')
    argList.append('-l walltime={:02d}:00:00,nodes=1:ppn=1'.format(self.walltime))

    if self.export_env:
      argList.append('-V')


    if self.queue_name:
      argList.append('-q {}'.format(self.queue_name))

    if self.name:
      argList.append('-N {:s}_{:d}'.format(self.name,self.run_number))

    if self.email:
      argList.append('-m abe')
      argList.append('-M {}'.format(self.email))

    if self.dependent_on:
      check_command = shlex.split('qstat -f {:d}'.format(self.dependent_on))
      try:
        jid_check = subprocess.check_output(check_command, text=True, stderr=subprocess.STDOUT)
      except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        logger.warning(
          'Ignoring hold request: cannot find job %d in queue (%s)',
          self.dependent_on,
          getattr(exc, 'output', str(exc)).strip(),
        )
      else:
        if re.search(self.user,jid_check) and not re.search('job_state = C',jid_check):
          argList.append('-W depend=afterok:{:d}'.format(self.dependent_on))
        else:
          logger.warning(
            'Ignoring hold request: User does not own dependent job or job is not eligible for dependency'
          )

    if self.exclusive:
      argList.append('-l naccesspolicy=singlejob')

    argList.append('{:s}'.format(self.queue_file))
    return argList

