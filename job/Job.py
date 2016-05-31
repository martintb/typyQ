from getpass import getuser
import shlex,subprocess
import os
import re

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
    print 'Creating job for',self.user
  def set_queue_file(self,fname,ignoreCheck=False):
    if ignoreCheck or os.path.exists(fname):
      self.queue_file = fname
      print 'Setting queue file to be',fname
    else:
      print "The queue file you specified doesn't seem to exist:",fname
      print "Exiting..."
      exit(1)
  def default_checks(self):
    if not self.queue_file:
      print 'You must call job.set_queue_file(path_to_queue_file) before submission'
      print "Exiting..."
      exit(1)
  def submit(self):
    self.default_checks()

    argList = self.build_argList()
    command = ' '.join(argList)

    print 'Submitting job using:\n\t',command
    qsub_out = subprocess.check_output(shlex.split(command))
    # print 'Output from Submission:\n\t',qsub_out
    self.update_dependency(qsub_out)
    self.run_number+=1

