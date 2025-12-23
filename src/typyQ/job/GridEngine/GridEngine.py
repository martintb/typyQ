from ..Job import Job
import re

class GridEngineJob(Job):
  def __init__(self):
    super(GridEngineJob,self).__init__()
    self.pe=None
    self.reserve=False
  def parse_submission_id(self,qsub_out):
    return int(qsub_out.split('.')[0]) #split for handling array jobs correctly

  def submission_cmd(self):
    argList = []
    argList.append('qsub -terse')
    argList.append('-j yes')
    argList.append('-cwd')
    if isinstance(self.walltime,int):
      argList.append('-l h_rt={:02d}:00:00'.format(self.walltime))
    elif isinstance(self.walltime,float):
      walltime = 3600*self.walltime
      argList.append('-l h_rt={:f}'.format(walltime))

    if self.reserve:
      argList.append('-R y'.format(self.reserve))

    if self.node:
      argList.append('-l h={}'.format(self.node))

    if self.export_env:
      argList.append('-V')

    if self.queue_name:
      argList.append('-q {}'.format(self.queue_name))

    if self.memory:
      argList.append('-l m_mem_free={:d}G'.format(self.memory))

    if self.virtual_memory:
      argList.append('-l h_vmem={:d}G'.format(self.virtual_memory))

    # if self.num_procs>1 and self.pe:
    if self.pe:
      argList.append('-pe {:s} {:d}'.format(self.pe,self.num_procs))

    if self.name:
      argList.append('-N {:s}_{:d}'.format(self.name,self.run_number))

    if self.email:
      argList.append('-m eas')
      argList.append('-M {}'.format(self.email))

    if self.exclusive:
      argList.append('-l exclusive=1')

    return argList

