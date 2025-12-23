# typyQ

The purpose of these scripts are to solve two main problems:

1. Running on several clusters simultaneously can be confusing as each cluster may use different queueing systems (PBS/SLURM/SGE/UGE) which each require a separate set of commands to run/stop/manage jobs.
2. Most clusters impose walltime limits that are many many times shorter than the needed length of the run.

typyQ solves #1 by abstracting away the queue system behind a few thin classes. After creating a queue object of the correct type, the `jsub` command will read the queue object and take care of submitting the job and requesting the resources with the correct flags.

typyQ solves #2 by reading the output from the queue after submission and storing the jobID of the last submitted job. Using this strategy long chains of dependent jobs can easily be submitted.

This code is somewhat a WIP and has some other features not described here.

## Supported Python versions

typyQ requires **Python 3.12 or newer** and is developed and tested on current CPython releases (3.12/3.13). Python 2.7 and older Python 3 series are not supported.

## Installation

typyQ ships with a modern `pyproject.toml` and can be installed with the next-generation [uv](https://github.com/astral-sh/uv) package manager (recommended) or any pip-compatible installer.

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

## Getting started

1. **Install typyQ** using `uv pip install .` (or `python -m pip install .`).
2. **Create a job file** with the scheduler template you need. For example, to scaffold a Slurm job: `jmake --slurm job.toml` (other supported templates include PBS and SGE/UGE).
3. **Submit the job** after editing values as needed (walltime, processors, etc.): `jsub job.toml`.
4. **Inspect or tweak the configuration** with `jread job.toml` or modify values interactively: `jmod --iset job.toml`.

Existing `.pkl` job files are automatically migrated to the TOML format the first time they are read by `jread`, `jmod`, or `jsub`.

## CLI usage

After installation the following console scripts are available:

* `jmake` – create a job configuration and queue script for supported schedulers (Slurm, PBS, and SGE/UGE)
* `jmod` – modify a job configuration (supports interactive editing with `ipdb`)
* `jread` – print a job configuration
* `jsub` – submit jobs using the provided queue script(s) for the selected scheduler
* `jdeps` – inspect queue dependencies

Each command supports `-h`/`--help` for full usage details.

## Examples
Create a queue object for the Farber (Slurm) supercomputing cluster:
```
$ jmake --farber job.toml
Creating job for tbm
>>> Making empty job file: job.toml
```
Read the contents of the queue object:
```
$ jread job.toml
>>> Reading job file: job.toml
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
$ jmod job.toml --set name MD_mpi str
>>> Reading job file: job.toml
>>> Setting name to md_mpi

$ jmod job.toml --set num_procs 4 int
>>> Reading job file: job.toml
>>> Setting num_procs to 4
```
Interactively modify the queue object:
```
$ jmod --iset job.toml
```
