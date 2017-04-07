from ..Job import Job
import re

class SLURMJob(Job):
  def __init__(self):
    super(SLURMJob,self).__init__()
  def update_dependency(self,qsub_out):
    self.dependent_on = int(re.findall('Submitted batch job ([0-9]*)',qsub_out)[0])
  def check(self):
    pass
  def build_argList(self):
    self.check()
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

    if self.queue_name:
      argList.append('-p {}'.format(self.queue_name))

    if self.name:
      argList.append('--job-name={:s}_{:d}'.format(self.name,self.run_number))

    if self.email:
      argList.append('--mail-type=ALL')
      argList.append('--mail-user={}'.format(self.email))

    if self.dependent_on:
      check_command = shlex.split('squeue -j {:d}'.format(self.dependent_on))
      try:
        jid_check = subprocess.check_output(check_command)
      except subprocess.CalledProcessError:
        print 'Ignoring hold request: Cannot find job {:d} in queue'.format(self.dependent_on)
      else:
        if re.search(self.user,jid_check):
          argList.append('--dependency=afterok:{:d}'.format(self.dependent_on))
        else:
          print 'Ignoring hold request: User does not own dependent job or job is not eligible for dependency'

    argList.append('{:s}'.format(self.queue_file))
    return argList

