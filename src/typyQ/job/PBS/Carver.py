from .PBS import PBSJob

class CarverJob(PBSJob):
  def __init__(self):
    super(CarverJob,self).__init__()
    self.gpu=False
  def submission_cmd(self):
    argList = super(CarverJob,self).submission_cmd()
    if self.gpu:
      argList[-1]+=':fermi'
    return argList
