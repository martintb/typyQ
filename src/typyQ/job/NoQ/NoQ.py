from ..Job import Job
import re
import shlex,subprocess

class NoQJob(Job):
  def __init__(self):
    super(NoQJob,self).__init__()
  def check(self):
    pass
  def submission_cmd(self):
    argList = []
    argList.append('bash -l {:s} & echo $!'.format(self.queue_file))

    if self.dependent_on:
      raise NotImplementedError('This feature is not yet working for NoQ jobs.')
      # check_command = shlex.split('ps -p {:d}'.format(self.dependent_on))
      # if
      # try:
      #   jid_check = subprocess.check_output(check_command)
      # except subprocess.CalledProcessError:
      #   print 'Ignoring wait request: Cannot find process {:d}'.format(self.dependent_on)
      # else:
      #   argList.insert('wait {:d}; '.format(self.dependent_on))

    return argList

