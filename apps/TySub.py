#!/usr/bin/env python
from typy.job import *
from typy.job.Monitor import UGEMonitor
import argparse
import os

parser = argparse.ArgumentParser(description= 
  ("tysub replaces qsub and acts as a rudimentary scheduler " 
   "that should make the queue more 'fair'. Firstly, it assigns "
   "a priority to each job so that the queue will cycle through "
   "users rather than running the jobs in order of submission. "
   "Secondly, tysub imposes a default walltime (which can be "
   "overriden) so that no user can dominate the queue."))

parser.add_argument('queue_file',
                    type=str,
                    nargs='?',
                    default=None,
                    help="Path to 'queue' file that you wish to submit to UGE")

parser.add_argument('-p','--ppri',
                    type=int,
                    help="Override tysubs internal priority calculation")

parser.add_argument('-w','--walltime',
                    type=int,
                    default=4,
                    help="Override default walltime")

parser.add_argument('-n','--node',
                    type=str,
                    default=None,
                    help="Request a specific node to run on")

parser.add_argument('-c','--ceiling',
                    type=int,
                    default=0,
                    help="Set maximum priority to use in submission")

parser.add_argument('-g','--gpu',
                    action='store_true',
                    help="Request GPU coprocessor for job")

parser.add_argument('-s','--status',
                    action='store_true',
                    help="display tysub\'s priority readins from UGE")

parser.add_argument('-S','--standby',
                    action='store_true',
                    help="Submit to standby queue rather than jayarman queue")

parser.add_argument('-H','--hold_jid',
                     default=None,
                     type=int,
                     help = 'Make this job dependent on a previous job')

args = parser.parse_args()

if args.status:
  print '.:: TYSUB PRIORITY STATUS ::.'
  mon = UGEMonitor()
  ppri = mon.calc_priority()
  mon.print_priority()

  print ""
  print ""
  print '.:: qstat -u @jayaraman_lab -pri ::.'
  subprocess.call(shlex.split("qstat -u @jayaraman_lab -pri"))

elif args.queue_file:
  if args.standby:
    command = "qsub -l standby=1 {:s}".format(args.queue_file)
    subprocess.call(shlex.split(command))
  else:
    job = FarberJob()
    job.set_queue_file(args.queue_file)

    if args.ppri:
      job.set_priority(args.ppri)
    else:
      mon = UGEMonitor()
      mon.set_priority_ceiling(args.ceiling)
      ppri = mon.calc_priority()
      job.set_priority(ppri)

    job.walltime = args.walltime

    if args.gpu:
      job.gpu=True

    if args.hold_jid is not None:
      job.dependent_on = args.hold_jid

    if args.node is not None:
      job.node=args.node

    job.submit()

    print '.:: Submitted job with JID: {0} (this number is repeated below for easy parsing)'.format(job.dependent_on)
    print '{0}'.format(job.dependent_on)
else:
  parser.print_help()
