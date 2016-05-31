from GridEngine import GridEngineJob
import re

class FarberJob(GridEngineJob):
  def __init__(self):
    super(FarberJob,self).__init__()
    self.ppri = None
    self.gpu=False
    self.standby=False
  def set_walltime(self,walltime):
    if walltime<=24:
      self.walltime = int(walltime)
      print "Setting a walltime of {:d} hours".format(self.walltime)
    else:
      print "Please use a maximum walltime of 24 hours for our queue."
      print "You requested a {:d} hour walltime.".format(int(walltime))
      exit(1)
  def check(self):
    if self.ppri is None:
      print 'You must call job.set_priority(ppri) before submission'
      print "Exiting..."
      exit(1)
  def set_priority(self,ppri):
    if isinstance(ppri,dict):
      if ppri['all'].max<ppri[self.user].min:
        self.ppri = ppri['all'].max
      else:
        self.ppri = ppri[self.user].min-1
    else:
      self.ppri = ppri
  def build_argList(self):
    self.check()

    argList = super(FarberJob,self).build_argList()

    if self.standby:
      argList.append('-l standby=1')

    if self.dependent_on:
      check_command = shlex.split('qstat -j {:d}'.format(self.dependent_on))
      try:
        jid_check = subprocess.check_output(check_command)
      except subprocess.CalledProcessError:
        print 'Ignoring hold request: Cannot find job {:d} in queue'.format(self.dependent_on)
      else:
        argList.append('-hold_jid {:d}'.format(self.dependent_on))
        if not self.standby:
          #update ppri to follow this jobs dependency
          self.ppri = int(re.findall('priority:\s*(\-?[0-9]*)',jid_check)[0]) - 1

    if not self.standby:
      argList.append('-p {:d}'.format(self.ppri))

    if self.gpu:
      argList.append('-l nvidia_gpu=1')

    argList.append('{:s}'.format(self.queue_file))

    return argList
