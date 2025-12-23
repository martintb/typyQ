#!/usr/bin/env python
# from typyQ.job.Monitor import UGEMonitor
from __future__ import print_function

from itertools import cycle
import argparse
import time
from typyQ import job

parser = argparse.ArgumentParser()
parser.add_argument('job_file', type=str)
parser.add_argument('-n','--num-repeats', type=int, default=1)
parser.add_argument('-p','--ppri', type=int, default=None)
parser.add_argument('-q','--queue', type=str)
parser.add_argument('-r','--reset',action='store_true')
parser.add_argument('-o','--output',type=str,default='OUTPUTS')
parser.add_argument('--qs_init',type=str)
parser.add_argument('--qs',nargs='+')
args = parser.parse_args()

model, legacy = job.load_job_model(args.job_file)
job_obj = job.instantiate_job(model)

if args.queue:
  job_obj.set_queue_name(args.queue)

if args.reset:
  job_obj.run_number=0
  job_obj.dependent_on=None

if args.qs:
  qs_cycle = cycle(args.qs)
elif job_obj.queue_file:
  qs_cycle = cycle([job_obj.queue_file])
else:
  raise ValueError('Queue script must be specified via --qs or in job file!')

for i in range(args.num_repeats):
  # if i==0 and isinstance(job_obj,FarberJob):
  #   if args.ppri is not None:
  #     ppri=args.ppri
  #   else:
  #     mon = UGEMonitor()
  #     ppri = mon.calc_priority()
  #   job_obj.set_priority(ppri)

  if job_obj.run_number==0 and args.qs_init:
    job_obj.set_queue_file(args.qs_init)
  else:
    job_obj.set_queue_file(next(qs_cycle))

  job_obj.submit()
  time.sleep(1)

model = job.JobModel.from_job(job_obj)
written_to = job.save_job_model(model, args.job_file)
if legacy:
  print('>>> Migrated legacy pickle to {}'.format(written_to))
