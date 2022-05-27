#Copyright (c) 2020 University of Illinois.  All rights reserved.
#
#Developed by: Innovative Systems Lab
#              National Center for Supercomputing Applications
#              http://www.ncsa.uiuc.edu/AboutUs/Directorates/ISL.html
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal with
#the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to
#do so, subject to the following conditions:
#* Redistributions of source code must retain the above copyright notice,
#  this list of conditions and the following disclaimers.
#* Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimers in the documentation
#  and/or other materials provided with the distribution.
#* Neither the names of Innovative Systems Lab, National Center for Supercomputing Applications,
#  nor the names of its contributors may be used to endorse or promote products
#  derived from this Software without specific prior written permission.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
#CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH THE
#SOFTWARE.

#################################### Defaults and Limits ###########################################

SWS_CONF = {
    "NODE_TYPE_NUM" : 2,
    "NODE_DEFINE" : [{'node_type': "ppc64le",'tot_cpu':160,'num_skt':2,'cpu_skt':20,'thd_cpu':4,'mem_cpu':1200,'tot_gpu':4,'gpu_type':"v100"}, \
                     {'node_type': "arm",'tot_cpu':80,'num_skt':1,'cpu_skt':80,'thd_cpu':1,'mem_cpu':4000,'tot_gpu':2,'gpu_type':"a100"}, \
                     {'node_type': "x86",'tot_cpu':256,'num_skt':8,'cpu_skt':16,'thd_cpu':2,'mem_cpu':3200,'tot_gpu':8,'gpu_type':"a100"}],
    "NODE_TYPE_DEFAULT" : "x86",
    "ALLOWED_PARTITIONS" : ["gpux1", "gpux2", "gpux3", "gpux4", "gpux8", "gpux16", "cpux1", "cpux4"],
    "PARTITION_DEFAULT" : "gpux1",
    "ALLOWED_NODE_TYPE" : ["ppc64le", "arm", "x86"],
    "NODES" : 1,
    "NTASKS_PER_NODE" : 16,
    "NTASKS_PER_NODE_CPU" : 1,
    "SOCKETS_PER_NODE" : 1,
    "CORES_PER_SOCKET" : 4,
    "CORES_PER_SOCKET_CPU" : 16,
    "THREADS_PER_CORE" : 1,
    "GPUS" : 1,
    "HOURS_UL" : 24,
    "HOURS_DEBUG" : 4,
    "HOURS_DEFAULT" : 4,
    "HOURS" : 24,
    "TIME" : "24:00:00",
    "MULTIPLIER" : 1,
    "CPU_PER_GPU_LL" : 16,
    "CPU_PER_GPU_UL" : 40,
    "CPU_PER_GPU" : 16,
    "CPU_PER_GPU_DEFAULT" : 16,
    "SLURM_RUN" : "srun",
    "SLURM_BATCH" : "#SBATCH",
    "SLURM_ALLOC" : "salloc",
    "SHELL" : "/bin/bash",
    "SHEBANG" : "#!/bin/bash",
    "COMMENT" : 2,
    "BATCH_COMMAND" : 1,
    "NON_BATCH_COMMAND" : 0,
    "INTERACTIVE_MODE" : 0,
    "SCRIPT_MODE" : 1,
    "ALLOCATION_MODE" : 2,
    "DEBUG_PARTITION" : "debug",
    "VALUE_ERROR" : -1,
    "TYPE_ERROR" : -2,
    "WARNING" : -3
}
