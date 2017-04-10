#!/usr/bin/env python
import typyQ.reader
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-q','--qtype', default='SLURM')
parser.add_argument('-l','--list', action='store_true')
parser.add_argument('-u','--user', default='tbm')
parser.add_argument('-a','--all',action='store_true')
args = parser.parse_args()

user = args.user
if args.all:
  user = None

if args.qtype=='SLURM':
  job_list = typyQ.reader.SLURM.read_queue(user)
elif args.qtype=='UGE':
  job_list = typyQ.reader.UGE.read_queue(user)
job_groups = typyQ.reader.util.parse_jobs(job_list)

standby_map = {True:'preempt', False:'OU'}
if args.list:
  for job_group in job_groups:
    user = job_group[0].user
    name = job_group[0].name
    size = job_group[0].num_cores
    queue= standby_map[job_group[0].standby]
    num_jobs = len(job_group)
    print user,name,queue,num_jobs,'x',size
    for job in job_group:
      print job.stateno
else:
  maxUserLen = max([len(group[0].user) for group in job_groups])
  maxNameLen = max([len(group[0].name) for group in job_groups])
  jobString = '{{:{}s}}{{:{}s}}{{:7s}} ({{:03d}}x{{:03d}}){{:13s}}'.format(maxUserLen+2,maxNameLen+2)
  for job_group in job_groups:
    user = job_group[0].user
    name = job_group[0].name
    size = job_group[0].num_cores
    queue= standby_map[job_group[0].standby]
    num_jobs = len(job_group)
    if num_jobs>1:
      job_list = '[{}...{}]'.format(job_group[0].stateno,job_group[-1].stateno)
    else:
      job_list = '[{}]'.format(job_group[0].stateno)
    print jobString.format(user,name,queue,num_jobs,size,job_list)
  
  
