#!/usr/bin/env python
from __future__ import print_function

try:
  import ipdb
  ist = ipdb.set_trace
except ImportError:
  ist = None

import argparse
from typyQ import job

parser = argparse.ArgumentParser()
parser.add_argument('job_file', type=str)
parser.add_argument('-s','--set',nargs=3, type=str)
if ist is not None:
  parser.add_argument('-i','--iset',action="store_true")
args = parser.parse_args()


def printJob():
  for (key,val) in vars(job_obj).items():
    print("{:20s}: {:10s}".format(key,str(val)))

print('>>> Reading job file: {}'.format(args.job_file))
model, legacy = job.load_job_model(args.job_file)
job_obj = job.instantiate_job(model)

if args.iset:
  if ist is None:
    print(">>> typyQ wasn't able to import ipdb.")
    print(">>> Interactive job modification not supported without ipdb.")
    exit(1)
  else:
    print("-----------------------------------------------------------------")
    printJob()
    print("-----------------------------------------------------------------")
    print(">>> Run \"printJob()\" to see current contents of job")
    print(">>> Job attributes can be set via \"job_obj.<attribute>=value\"")
    print(">>> Run \"q\" to quit modification without saving")
    print(">>> Run \"c\" to write modifications to the job file.")
    print("-----------------------------------------------------------------")
    ist()
    print(">>> Writing job modifications to disk!")
elif args.set:
  attr = args.set[0]
  val = args.set[1]
  valType = args.set[2]

  if valType=="int":
    val = int(val)
  elif valType=="float":
    val = float(val)
  elif valType=="bool":
    val = val=="True"
  elif valType=="str":
    pass
  elif valType=="None":
    val = None
  else:
    print(">>> `Variable type must be int, float, bool, none, or str, but not {}".format(valType))
    exit(1)

  print(">>> Setting {} to {}".format(attr,val))
  setattr(job_obj,attr,val)
else:
  print(">>> JobClass:",job_obj.__class__.__name__)
  print("-----------------------------------------------------------------")
  printJob()
  print("-----------------------------------------------------------------")

if args.iset or args.set:
  model = job.JobModel.from_job(job_obj)
  written_to = job.save_job_model(model, args.job_file)
  if legacy:
    print('>>> Migrated legacy pickle to {}'.format(written_to))
