#!/usr/bin/env python
from typyQ import job
import argparse
import cPickle


parser = argparse.ArgumentParser()
parser.add_argument('name', type=str)
parser.add_argument('--qs', action='store_true')

jobType = parser.add_mutually_exclusive_group()
jobType.add_argument('--ruth',    dest='jobType', action='store_const', const=job.RuthJob)
jobType.add_argument('--farber',  dest='jobType', action='store_const', const=job.FarberJob)
jobType.add_argument('--raritan',  dest='jobType', action='store_const', const=job.RARITANJob)
args = parser.parse_args()

if args.jobType is not None:
  print '>>> Making empty job file "{}" of type "{}"'.format(args.name,args.jobType.__name__)
  with open(args.name,'wb') as f:
    cPickle.dump(args.jobType(),f,-1)

if args.qs:
  print '>>> Making generic run script "run.qs"'
  with open('run.qs','w') as f:
    f.write('#!/bin/bash -l\n')
    f.write('# export OMP_NUM_THREADS=8\n')
    f.write('set -e\n')
    f.write('\n')
    f.write('source ~/.typyEnv CLEAN\n')
    f.write('typyEnv --add python\n')
    f.write('typyEnv --add typySetup\n')
    f.write('typyEnv --add typySim\n')
    f.write('# typyEnv --add typyAnalyze\n')
    f.write('# typyEnv --add typyCreator\n')
    f.write('# typyEnv --add lammps\n')
    f.write('\n')
    f.write('cd ${SGE_O_WORKDIR}\n')
    f.write('\n')
    f.write('python sim.py >OUTPUTS\n')
    f.write('# mpirun python sim.py >OUTPUTS\n')
    f.write('# mpirun lammps -i in.lammps > OUTPUTS\n')
    f.write('\n')
    f.write('touch DONE\n')

if not args.qs and (args.jobType is None):
  print '>>> If you\'ve made it here, there is a good chance you are not using this tool correctly.'
  print '>> Use the --qs flag to direct this tool to create a generic queue script,'
  print '>> or specify a jobType to create a generic, empty job pkl.'
  print '>> See the help output below for more information.'
  parser.print_help()
