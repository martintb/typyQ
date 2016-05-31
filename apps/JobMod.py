#!/usr/bin/env python

import ipdb
ist = ipdb.set_trace

# from typy.job import *
import argparse
import cPickle

parser = argparse.ArgumentParser()
parser.add_argument('pkl', type=str)
parser.add_argument('-s','--set',nargs=3, type=str)
parser.add_argument('-i','--iset',action="store_true")
args = parser.parse_args()

def printJob():
  for (key,val) in vars(job).items():
    print "{:20s}: {:10s}".format(key,str(val))

print '>>> Reading job file: {}'.format(args.pkl)
with open(args.pkl,'rb') as f:
  job = cPickle.load(f)


if args.iset:
  print "-----------------------------------------------------------------"
  printJob()
  print "-----------------------------------------------------------------"
  print ">>> Run \"printJob()\" to see current contents of job"
  print ">>> Job attributes can be set via \"job.<attribute>=value\""
  print ">>> Run \"q\" to quit modification without saving"
  print ">>> Run \"c\" to write modifications to the pkl."
  print "-----------------------------------------------------------------"
  ist()
  print ">>> Writing job modifications to disk!"
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
    print ">>> `Variable type must be int, float, bool, none, or str, but not",valType
    exit(1)

  print ">>> Setting {} to {}".format(attr,val)
  setattr(job,attr,val)
else:
  print "-----------------------------------------------------------------"
  printJob()
  print "-----------------------------------------------------------------"

if args.iset or args.set:
  with open(args.pkl,'wb') as f:
    cPickle.dump(job,f,-1)

