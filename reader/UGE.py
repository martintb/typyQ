from .JobData import JobData
import shlex,subprocess
import re

def read_queue(user_group=None):
  if user_group is None:
    qstat_str = subprocess.check_output(shlex.split('qstat -u "tbm" -pri -ext'))
  else:
    qstat_str = subprocess.check_output(shlex.split('qstat -u "{}" -pri -ext'.format(user_group)))
  job_nums=[]
  basic_job_data={}
  for line_num,line_str in enumerate(qstat_str.split('\n')):
    if line_str and line_num>1:
      job_num = int(line_str.strip().split()[0])
      ppri = int(line_str.strip().split()[5])
      state = line_str.strip().split()[10]
      if 'h' in state:
        held=True
      else:
        held=False
      basic_job_data[job_num] = {'ppri':ppri,'state':state,'held':held}
      job_nums.append(job_num)

  job_nums_str = ','.join([str(i) for i in job_nums])
  job_details = subprocess.check_output(shlex.split('qstat -j {}'.format(job_nums_str)))
  job_details = job_details.split('='*62)
  job_details.pop(0)

  job_list = []
  for i,jd in enumerate(job_details):
    job_num = int(re.findall('job_number:\s*([0-9a-zA-z]*)',jd)[0])
    ppri    = basic_job_data[job_num]['ppri']
    state   = basic_job_data[job_num]['state']
    held    = basic_job_data[job_num]['held']
    user = re.findall('owner:\s*([0-9a-zA-z]*)',jd)[0]
    name = re.findall('job_name:\s*(.*)',jd)[0]
    standby = not (re.search('standby=1',jd) == None)
    predecessor = re.search('jid_predecessor_list:\s*([0-9]*)\s*',jd)
    successor = re.search('jid_successor_list:\s*([0-9]*)\s*',jd)
    if successor:
      successor = int(successor.groups()[0])
    if predecessor:
      predecessor = int(predecessor.groups()[0])
    num_cores = re.search('parallel environment:.*\s*range:\s*([0-9]*)\s*',jd)
    if num_cores:
      num_cores = int(num_cores.groups()[0])
    else:
      num_cores = 1


    job_list.append(
                    JobData(
                            user=user,
                            name=name,
                            num=job_num,
                            state=state,
                            standby=standby,
                            num_cores=num_cores,
                            ppri=ppri,
                            held=held,
                            successor=successor,
                            predecessor=predecessor
                           )
                    )
  return job_list
