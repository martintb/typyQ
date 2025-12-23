from .JobData import JobData
import shlex,subprocess
import re

def read_queue(user_group=None):
  job_details = subprocess.check_output(shlex.split('scontrol show jobid'), text=True).split('\n\n')

  job_list = []
  for i,jd in enumerate(job_details):
    if not jd:
      continue

    user    = re.findall('UserId=([0-9a-zA-z]*)\([0-9]*\)',jd,flags=re.MULTILINE)[0]
    if user_group:
      if user not in user_group:
        continue
      
    job_num = int(re.findall('JobId=([0-9a-zA-z]*) ',jd,flags=re.MULTILINE)[0])
    name    = re.findall('JobName=(.*)$',jd,flags=re.MULTILINE)[0]
    state   = re.findall('JobState=([0-9a-zA-z]*) ',jd,flags=re.MULTILINE)[0]


    queue   = re.findall('Partition=([a-zA-z]*) ',jd,flags=re.MULTILINE)[0]
    if queue == 'preemptible':
      standby = True
    else:
      standby = False

    predecessor = re.search('Dependency=([a-zA-z0-9:()]*)',jd,flags=re.MULTILINE)
    # import ipdb; ipdb.set_trace()
    if predecessor:
      predecessor = predecessor.groups()[0]
      if predecessor  == '(null)':
        predecessor = None
      else:
        predecessor = int(predecessor.split(':')[1])

    num_cores = re.search('NumCPUs=([0-9]*)',jd,flags=re.MULTILINE)
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
                            ppri=0,
                            held=None,
                            predecessor=predecessor
                           )
                    )
  return job_list
