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
#* Neither the names of <NAME OF DEVELOPMENT GROUP>, <NAME OF INSTITUTION>,
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
# /opt/apps/swsuite/src/swbatch.py
# version 1.0
#

import subprocess
import argparse
from swtools import Builder
import sys
import os
import time

# log the script
def save_script(temp_run_script, final_run_script_buffer):
    home = os.environ["HOME"]
    hidden_dir = "{}/{}".format(home, ".run_scripts")

    if os.path.exists(hidden_dir) == False:
        os.mkdir(hidden_dir)
#        os.chmod(hidden_dir, 0o766)

    new_loc = "{}/{}".format(hidden_dir, temp_run_script)
    with open(new_loc, "w") as f:
        f.write(final_run_script_buffer)

#    os.chmod(new_loc, 0o744)
    return


def main():
    if len(sys.argv)==1:
        print("usage: swbatch [-h] RUN_SCRIPT [-v]\nswbatch.py: error: the following arguments are required: run_script")
        print("------------------------------------------")
        print("Example: hostname_demo")
        print("------------------------------------------")
        print("#!/bin/bash")
        print("#SBATCH --job-name=\"hostname_demo\"")
        print("#SBATCH --output=\"hostname_demo_%j.%N.out\"")
        print("#SBATCH --partition=gpux1")
        print("#SBATCH --time=4")
        print("")
        print("module load wmlce")
        print("srun hostname")
        print("------------------------------------------")
        return
    if len(sys.argv)==2 and sys.argv[1] == '-v':
        print("HAL Slurm Wrapper Suite v0.5")
        subprocess.run(['sbatch', '-V'])
        return

    parser = argparse.ArgumentParser(
        description="HAL Slurm Wrapper Suite v0.5",
        usage="swbatch [-h] RUN_SCRIPT [-v]")

    parser._action_groups.pop()
    required = parser.add_argument_group('Required Argument(s)')
    other = parser.add_argument_group('Other Arguments')

    # Required Arguments
    required.add_argument("run_script",
        help="Specify a batch script as input.",
        nargs=1,
        default="f00")

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
    user_arguments = ["partition", "cpu_per_gpu", "time", "job_name", "output", "error", "singularity"]
    bldr = Builder()
    final_run_script_buffer = bldr.build_run_script(args.run_script[0], user_arguments)
    print("...............Submitting Run Script..............\n\n{}".format(final_run_script_buffer))

    # Open a hidden file and write the run script into it
    temp_run_script = ".temp_run_script.{}.swb".format(int(time.time() * 1000000))
    with open(temp_run_script, "w") as f:
        f.write(final_run_script_buffer)
    save_script(temp_run_script[1:], final_run_script_buffer)

    subprocess.run(["sbatch", temp_run_script])
    subprocess.run(["rm", temp_run_script])
    print("{}...............Run Script Submitted..............{}\n".format("\033[42;30m", "\033[0m"))

if __name__ == "__main__":
    main()
