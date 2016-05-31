class MinMax(object):
  def __init__(self,min=None,max=None):
    self.min =  min
    self.max =  max

  def __str__(self):
    return "Min: {:d} Max: {:d}".format(self.min,self.max)

  def __repr__(self):
    return "<Min: {:d} Max: {:d}>".format(self.min,self.max)

  def update(self,val):
    if self.min is None:
      self.min = val
    else:
      self.min = min(self.min,val)

    if self.max is None:
      self.max = val
    else:
      self.max = max(self.max,val)
