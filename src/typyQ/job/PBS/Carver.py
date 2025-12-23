from .PBS import PBSJob

class CarverJob(PBSJob):
  def __init__(self):
    super(CarverJob,self).__init__()
    self.gpu=False
  def build_argList(self):
    self.check()
    argList = super(PBSJob,self).build_argList()
    if self.gpu:
      argList[-1]+=':fermi'
    return argList
