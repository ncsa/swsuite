# swsuite v1.0

## Introduction
The HAL Slurm Wrapper Suite is designed to help users use the HAL system easily and efficiently. The current version is "swsuite-v1.0", which includes  
* srun → swrun : request resources to run interactive jobs.  
* sbatch → swbatch : request resource to submit a batch script to slurm.  
* squeue → swqueue : check current running jobs and computational resource status.  

## Goals
1) Minimize the required input options.
2) Consistent with the original "slurm" run-script format.
3) Submits job to suitable partition based on the number of CPUs and/or GPUs needed.

## Usage
### Interactive Mode
```
swrun [-h] -p PARTITION [-c CPU_PER_GPU] [-t TIME] [-s SINGULARITY][-r RESERVATION] [-v]
```
* partition (**_required_**) : cpu_mini, cpun1, cpun2, cpun4, cpun8, cpun16. gpux1, gpux2, gpux3, gpux4, gpux8, gpux12, gpux16.
* [cpu_per_gpu] (_optional_) : 16 cpus (default), range from 16 cpus to 40 cpus.
* [time] (_optional_) : 24 hours (default), range from 1 hour to 72 hours (walltime).
* [singularity] (_optional_): specify a singularity container(name-only) to use from the $HAL_CONTAINER_REGISTRY
* [reservation] (_optional_): specify a reservation name, if any.
* [version] (_optional_): Display Slurm wrapper suite and Slurm versions.

##### Example:
To request a full node: 4 gpus, 160 cpus (→ 40*4 = 160 cpus) , 72 hours
```
swrun -p gpux4 -c 40 -t 72
```
or using a container image (dummy.sif) on a cpu only node with default of 24 hours
```
swrun -p cpun1 -s dummy
```
**Note**: In the second case we are using a singularity container image. 
To run a _custom_ container, instead of using the default location of the container registry, you can set it to your own by **_first_** exporting the environment variable

```bash
export HAL_CONTAINER_REGISTRY="/path/to/custom/registry"
```

### Script Mode

```
swbatch [-h] RUN_SCRIPT [-v]
```
Same as original slurm batch.
* RUN_SCRIPT (**_required_**) : Specify a batch script as input.

Within the run_script:
* partition (**_required_**) : cpu_mini, cpun1, cpun2, cpun4, cpun8, cpun16, gpux1, gpux2, gpux3, gpux4, gpux8, gpux12, gpux16.
* job_name (_optional_) : job name.
* output_file (_optional_) : output file name.
* error_file (_optional_) : error file name.
* cpu_per_gpu (_optional_) : 16 cpus (default), range from 16 cpus to 40 cpus.
* time (_optional_) : 24 hours (default), range from 1 hour to 72 hours (walltime).
* singularity (_optional_) : Specify a singularity image to use. The container image is searched for from the container registry directory environment variable in the swconf.yaml configuration.

##### Example:
Consider demo.swb, which is a batch script such as
```python
#!/bin/bash

#SBATCH --partition=gpux1

srun hostname
```

or using a container image with a time of 42 hours

```python
#!/bin/bash

#SBATCH --job_name="demo"
#SBATCH --output="demo.%j.%N.out"
#SBATCH --error="demo.%j.%N.err"
#SBATCH --partition=gpux1
#SBATCH --time=42
#SBATCH --singularity=dummy

srun hostname
```

You can run the script as below but remember to export the container registry variable if you are using some custom singularity images.

```bash
swbatch demo.swb
```

### Monitoring Mode

```
swqueue
```
Same as original slurm `squeue`, which show both running and queueing jobs, the `swqueue` shows running jobs and computational resource status.

