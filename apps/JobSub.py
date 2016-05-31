#!/usr/bin/env python
from typy.job.Monitor import UGEMonitor
from itertools import cycle
import argparse
import cPickle
import time

parser = argparse.ArgumentParser()
parser.add_argument('pkl', type=str)
parser.add_argument('-n','--num-repeats', type=int, default=1)
parser.add_argument('-p','--ppri', type=int, default=None)
parser.add_argument('-q','--queue', type=str)
parser.add_argument('-r','--reset',action='store_true')
parser.add_argument('-o','--output',type=str,default='OUTPUTS')
parser.add_argument('--qs_init',nargs='+')
parser.add_argument('--qs',nargs='+')
args = parser.parse_args()

with open(args.pkl,'rb') as f:
  job = cPickle.load(f)

if args.queue:
  job.set_queue_name(args.queue)

if args.reset:
  job.run_number=0
  job.dependent_on=None

qs_cycle = cycle(args.qs)
for i in range(args.num_repeats):
  if i==0 and isinstance(job,FarberJob):
    if args.ppri is not None:
      ppri=args.ppri
    else:
      mon = UGEMonitor()
      ppri = mon.calc_priority()
    job.set_priority(ppri)

  if job.run_number==0:
    job.set_queue_file(initQ)
  else:
    job.set_queue_file(repQ)

  job.submit()
  time.sleep(1)

with open(args.pkl,'wb') as f:
  cPickle.dump(job,f,-1)



  
    
