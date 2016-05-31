from GridEngine import GridEngineJob

class VenusJob(GridEngineJob):
  def __init__(self):
    super(VenusJob,self).__init__()
  def check(self):
    pass
  def build_argList(self):
    self.check()

    argList = super(VenusJob,self).build_argList()

    if self.dependent_on:
      check_command = shlex.split('qstat -j {:d}'.format(self.dependent_on))
      try:
        jid_check = subprocess.check_output(check_command)
      except subprocess.CalledProcessError:
        print 'Ignoring hold request: Cannot find job {:d} in queue'.format(self.dependent_on)
      else:
        argList.append('-hold_jid {:d}'.format(self.dependent_on))

    argList.append('{:s}'.format(self.queue_file))

    return argList
