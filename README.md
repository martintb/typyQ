# typyQ
 
The purpose of these scripts are to solve two main problems:

1. Running on several clusters simultaneously can be confusing as each cluster may use different queueing systems (PBS/SLURM/SGE/UGE) which each require a separate set of commands to run/stop/manage jobs.
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
* Modern Python (>=3.12)
* `ipdb` (optional for interactive job modification)

## Installation ##

You can install typyQ with [uv](https://github.com/astral-sh/uv) (recommended) or any modern
pip-compatible installer.

### Using uv
```bash
uv pip install .
```

### Using pip
```bash
python -m pip install .
```

### Editable installs
For local development you can install typyQ in editable mode:
```bash
uv pip install --editable .
```

## CLI usage ##

After installation the following console scripts are available:

* `jmake` – create a job pickle and optional queue script
* `jmod` – modify a job pickle (supports interactive editing with `ipdb`)
* `jread` – print a job pickle
* `jsub` – submit jobs using the provided queue script(s)
* `jdeps` – inspect queue dependencies

Each command supports `-h`/`--help` for full usage details.