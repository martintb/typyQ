# typyQ
 
The purpose of these scripts are to solve two main problems:
1. Running on several clusters simultaneously can be confusing as each cluster may use different queueing systems (PBS/SLURM/SGE/UGE) which each require a separate set of commands to run/stop/manage simulations.
2. Most clusters impose walltime limits that are many many times shorter than the needed length of the run.

typyQ solves #1 by abstracting away the queue system behind a few thin classes. After creating a queue object of the correct type, the jsub command will read the queue object and take care of submitting the job and requesting the resources with the correct flags. 

typyQ solves #2 by reading the output from the queue after submission and storing the jobID of the last submitted job. Using this strategy long chains of dependent jobs can easily be submitted.

This code is somewhat a WIP and has some other features not described here.

## Examples ##
Create a queue object for the Farber supercomputing cluster:
```
$ jmake --farber job.pkl
Creating job for tbm
>>> Making empty job file: job.pkl
```
Read the contents of the queue object:
```
$ jread job.pkl
>>> Reading job file: job.pkl
-----------------------------------------------------------------
export_env          : False
exclusive           : False
run_number          : 0
node                : None
name                : None
reserve             : False
standby             : False
queue_name          : None
num_procs           : 1
dependent_on        : None
user                : tbm
memory              : None
queue_file          : None
gpu                 : False
virtual_memory      : None
pe                  : None
email               : None
ppri                : None
walltime            : 4
-----------------------------------------------------------------
```
Modify the queue object:
```
$jmod job.pkl --set name MD_mpi str
>>> Reading job file: job.pkl
>>> Setting name to md_mpi

$jmod job.pkl --set num_procs 4 int
>>> Reading job file: job.pkl
>>> Setting num_procs to 4
```
Interactively modify the queue object:
```
$jmod --iset job.pkl
```

## Requirements ##
* modern python version (tested with 2.7+)
* ipdb (optional for interactive job modification)