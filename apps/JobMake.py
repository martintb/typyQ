#!/usr/bin/env python
from typyQ import job
import argparse
import cPickle


parser = argparse.ArgumentParser()
parser.add_argument('name', type=str)
parser.add_argument('--ruth',  action='store_true')
parser.add_argument('--farber',  action='store_true')
args = parser.parse_args()

if args.farber:
  job = job.FarberJob()
elif args.ruth:
  job = job.RuthJob()
else:
  raise ValueError('Must provide job type as flag!')

print '>>> Making empty job file: {}'.format(args.name)
with open(args.name,'wb') as f:
  cPickle.dump(job,f,-1)
