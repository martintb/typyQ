from .MinMax import MinMax
from collections import namedtuple
import shlex,subprocess
import re

class Priority:
  def __init__(self,users=None):
    self.priority_ceiling = -1
    self.priority_floor = -1022
    self.get_users(users)
  def set_priority_ceiling(self,value):
    if value>=-1023 and value<=1023:
      self.priority_ceiling = value
    else:
      print('Priority ceiling must be in range -1023<value<1023. You specified',value)
      exit(1)
    self.update_users()
  def get_users(self,users=None):
    if users is None:
      grp_str = subprocess.check_output(shlex.split('getent group jayaraman_lab'), text=True)
      grp_str = grp_str.split(':')[-1] #remove group names
      self.user_list = grp_str.strip().split(',')
      self.user_list.append('all')
    else:
      self.user_list = users
    self.priority = {user:MinMax() for user in self.user_list}
  def calc_priority(self,job_list):
    for i,job in enumerate(job_list):
      if not job.standby and not job.held and job.ppri!=0:
        #update checks if the job ppri is lower than the user min
        #or higher than the user max and updates the users's data accordingly
        priority[job.user].update(job.ppri)
        priority['all'].update(job.ppri)
    for user in priority.keys():
      if priority[user].max is None or priority[user].max>self.priority_ceiling:
        priority[user].max = self.priority_ceiling

      if priority[user].min is None or priority[user].min<self.priority_floor:
        priority[user].min = self.priority_ceiling
    return self.priority
  def print_priority(self):
    print('{:20s} {:4s} {:4s}'.format('user','min','max'))
    print('{:20s} {:4s} {:4s}'.format('----------','----','----'))
    for key in self.priority.keys():
      print('{:20s} {:4d} {:4d}'.format(key,self.priority[key].min,self.priority[key].max))
