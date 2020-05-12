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

#!/bin/python3
#
# /opt/apps/swsuite/src/swrun.py
# version 1.0
#

import subprocess
import argparse
from swtools import Builder
import sys

def main():
    if len(sys.argv)==1:
        print("{}\n{}".format( "usage: swrun [-h] -p PARTITION [-c CPU_PER_GPU] [-t TIME] [-s SINGULARITY] [-r RESERVATION] [-v]",
                               "swrun.py: error: the following arguments are required: -p/--partition") )
        print("------------------------------------------")
        print("Example: interactive 1x GPU job")
        print("------------------------------------------")
        print("swrun -p gpux1")
        print("------------------------------------------")
        return
    if len(sys.argv)==2 and sys.argv[1] == '-v':
        print("HAL Slurm Wrapper Suite v0.5")
        subprocess.run(['srun', '-V'])
        return

    parser = argparse.ArgumentParser(
        description="HAL Slurm Wrapper Suite v0.5",
        usage="swrun [-h] -p PARTITION [-c CPU_PER_GPU] [-t TIME] [-s SINGULARITY][-r RESERVATION] [-v]")
#        usage="swrun [-h] -p PARTITION [-c CPU_PER_GPU] [-t TIME] [-s SINGULARITY][-r RESERVATION] [-l (ENABLE_LOCAL_SSD)] [-v]")

    parser._action_groups.pop()
    required = parser.add_argument_group('Required Arguments')
    optional = parser.add_argument_group('Optional Arguments')
    other = parser.add_argument_group('Other Arguments')

    # Required Arguments
    required.add_argument("-p", "--partition",
        help="CPU: cpun1, cpun2, cpun4, cpun8, cpun16. GPU: gpux1, gpux2, gpux3, gpux4, gpux8, gpux12, gpux16.",
        nargs=1,
        default="84r",
        required=True)

    # Optional Arguments
    optional.add_argument("-c", "--cpu_per_gpu",
        help="16 cpus (default), range from 16 cpus to 40 cpus.",
        type=int,
        nargs=1,
        default=16)
    optional.add_argument("-t", "--time",
        help="4 hours (default), range from 1 hour to 24 hours (walltime).",
        nargs=1,
        default="4")
    optional.add_argument("-s", "--singularity",
        help="Specify a singularity container(name-only) to use from the $HAL_CONTAINER_REGISTRY",
        nargs=1,
        default="84r")
    optional.add_argument("-r", "--reservation",
        help="Specify a reservation id",
        nargs=1,
        default="84r")
#    optional.add_argument("-l", "--local_ssd",
#        help="Include this flag to use ssd",
#        action='store_true')

    # Other Arguments
    other.add_argument("-v", "--version",
        help="Display Slurm wrapper suite and Slurm versions.",
        action='store_true')

    other.add_argument("-d", "--debug",
        help=argparse.SUPPRESS,
        action='store_true')

    args = parser.parse_args()

    # Supress Traceback
    if args.debug == False:
        sys.tracebacklimit = 0

    # Define user suppplied parameters and create a Builder object
#    user_arguments = ["partition", "cpu_per_gpu", "time", "singularity", "local_ssd", "reservation"]
    user_arguments = ["partition", "cpu_per_gpu", "time", "singularity", "reservation"]
    bldr = Builder()
    command = bldr.build_command(args, user_arguments, 'interactive')
    command = command.split("\n")
    print(command[0])

    print("{}srun command submitted!{}".format("\033[42;30m", "\033[0m"))

    if len(command) > 1:
        for c in command[1:]:
            print(c)
        print("{}Please submit the non-srun commands yourself!{}".format("\033[45m", "\033[0m"))
    subprocess.run(command[0].split(" "))

if __name__ == "__main__":
    main()
