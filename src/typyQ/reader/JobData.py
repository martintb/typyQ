class JobData(object):
  def __init__(self,**kwargs):
    user        = None
    num         = None
    standby     = None
    ppri        = None
    held        = None
    successor   = None
    predecessor = None
    state       = None
    name        = None
    num_cores   = None
    gpu         = None
    self.__dict__.update(kwargs)
