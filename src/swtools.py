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
# /opt/apps/swsuite/src/swtools.py
# version 1.0
#

from functools import partial
from datetime import datetime
import os
import argparse
import math

import swconfig as swc

# Using collections for testing
from collections import namedtuple
# Switch to using dataclasses if you have support for python 3.7.x
# from dataclasses import dataclass

BADWARNING = '\033[43;30m'
OKGREEN = '\033[42m'
FAIL = '\033[41m'
ENDC = '\033[0m'
WHITE = '\033[97m'
BLACK_TEXT = '\033[30m'
TEST_PASSED = OKGREEN + WHITE + "Test Passed!" + ENDC + ENDC
TEST_FAILED = FAIL + WHITE + "Test Failed!" + ENDC + ENDC
TEST_DIVIDER = '-'*28

# Class to build scripts and commands

class Builder:

    # Value Checking Fns

    # Following check functions return in the form of
    # return a flag, error message, error code , new value to assign in case of warnings
    # They are wrapped as callable objects and stored in a list of rules

    # Takes in a partition and checks if it is in the list of allowed partitions
    # If not, return VALUE_ERROR to raise an ERROR and stop code exec
    def check_partitions(self, p):
        if p not in swc.SWS_CONF['ALLOWED_PARTITIONS']:
            return False, "{} Partition {} does not exist. {}".format(FAIL, p, ENDC), swc.SWS_CONF['VALUE_ERROR'], ""
        if "cpu" in p:
            return False, "Note: {} CPU partition used. Ignoring all user-specified node config {}".format(BADWARNING, ENDC), swc.SWS_CONF['WARNING'], p
        return True, "" , 0, ""

    def check_node_type(self, p):
        if p not in swc.SWS_CONF['ALLOWED_NODE_TYPE']:
            return False, "{} Node Type {} does not exist. {}".format(FAIL, p, ENDC), swc.SWS_CONF['VALUE_ERROR'], ""
        return True, "" , 0, ""

    # Takes in a time as hours and checks it against a range
    # If not, cuts it off at limit and raises a WARNING
    def check_time(self, t):
        tret = swc.SWS_CONF['HOURS_DEFAULT']
        flag = True
        err_msg = ""
        err_code = 0

        if t < 1:
            tret = swc.SWS_CONF['HOURS_DEFAULT']
            flag = False
            err_msg = "Warning: {} Time below 1 hour, using default of {} hours.{}".format(BADWARNING, swc.SWS_CONF['HOURS_DEFAULT'], ENDC)
            err_code = swc.SWS_CONF['WARNING']
        elif t > swc.SWS_CONF['HOURS_UL']:
            tret = swc.SWS_CONF['HOURS_UL']
            flag = False
            err_msg = "Warning: {} Time above {} hours, capping at {}. {}".format(BADWARNING, swc.SWS_CONF['HOURS_UL'], swc.SWS_CONF['HOURS_UL'], ENDC)
            err_code = swc.SWS_CONF['WARNING']
        else:
            tret = t

        return flag, err_msg, err_code, tret

    # Takes in a cpu_per_gpu and checks it against a range
    # If not, RAISES an ERROR by return error code to parameter check
    def check_cpu_per_gpu(self, cpg):
        cpgret = swc.SWS_CONF['CPU_PER_GPU_DEFAULT']
        flag = True
        err_msg = ""
        err_code = 0

        if cpg < swc.SWS_CONF['CPU_PER_GPU_LL'] or cpg > swc.SWS_CONF['CPU_PER_GPU_UL']:
            flag = False
            err_msg = "{}Invalid value of {} CPU per GPU, please input an integer in the range between {} and {}.{}".format(FAIL, cpg, swc.SWS_CONF['CPU_PER_GPU_LL'], swc.SWS_CONF['CPU_PER_GPU_UL'], ENDC)
            err_code = swc.SWS_CONF['VALUE_ERROR']

        return flag, err_msg, err_code, 0

    # search for container image
    def check_container(self, container_noext):
        toret = ""
        flag = True
        err_msg = ""
        err_code = 0

        ftree = {}
        depth = 0
        for dirpath, dirnames, filenames, dirfd in os.fwalk(swc.SWS_CONF['HAL_CONTAINER_REGISTRY']):
            ftree[depth] = {'directory':dirpath, 'files':filenames}
            depth += 1

        final_img = ""
        found = False
        for k, v in ftree.items():
            if k <= swc.SWS_CONF['CONTAINER_SEARCH_DEPTH_LIMIT']:
                for ext in swc.SWS_CONF['ALLOWED_CONTAINER_IMAGE_EXTENSIONS']:
                    container = container_noext + ext
                    if container in v['files']:
                        final_img = "{}/{}".format(v['directory'], container)
                        found = True
                    if found == True:
                        break
            if found == True:
                break

        if final_img == "":
            flag = False
            err_msg = "{}Container image not found!{}\n{} Started topdown search of depth {} from {} for {} {}".format(FAIL, ENDC, " "*len("ValueError:"), swc.SWS_CONF['CONTAINER_SEARCH_DEPTH_LIMIT'], swc.SWS_CONF['HAL_CONTAINER_REGISTRY'], container_noext, swc.SWS_CONF['ALLOWED_CONTAINER_IMAGE_EXTENSIONS'])
            err_code = swc.SWS_CONF['VALUE_ERROR']
        else:
            flag = False
            err_msg = "{}Container image found!{} Using {}".format(OKGREEN + BLACK_TEXT , ENDC, final_img)
            err_code = swc.SWS_CONF['WARNING']
            toret = final_img

        return flag, err_msg, err_code, toret

    # Checks User Parameters in terms of limits
    # Based on flag return from rules, it checks error code
    # Based on error code it outputs an error message which it ALSO got from rules
    def parameter_checks(self, dict_params, params_to_clean):
        for p in params_to_clean:
            # first check is parameter to clean is actually present
            if p in dict_params:
                x = dict_params[p]
                if x == "" or x == None:
                    continue
                else:
                    # then try to find the related function to check the value
                    if p in self._rules:
                        flag, err_msg, err_code, corrected_value = self._rules[p](x)
                        if flag == False:
                            if err_code == swc.SWS_CONF['VALUE_ERROR']:
                                raise ValueError(err_msg)
                            elif err_code == swc.SWS_CONF['TYPE_ERROR']:
                                raise TypeError(err_msg)
                            elif err_code == swc.SWS_CONF['WARNING']:
                                print(err_msg)
                                dict_params[p] = corrected_value

        return


    ###################################### Creations Fns ###########################################

    # creates a job parameters dictionary from uparams i.e user parameters dictionary
    def job_parameters_init(self, uparams, mode):
        job_parameters = {}
        # User supplied k=key, v=value
        for k,v in uparams.items():
            job_parameters[k] = v
        # Generated
        job_parameters["nodes"] = 1
        job_parameters["ntasks-per-node"] = swc.SWS_CONF['NTASKS_PER_NODE']
        job_parameters["sockets-per-node"] = swc.SWS_CONF['SOCKETS_PER_NODE']
        job_parameters["cores-per-socket"] = swc.SWS_CONF['CORES_PER_SOCKET']
        job_parameters["threads-per-core"] = swc.SWS_CONF['THREADS_PER_CORE']
        job_parameters["gpus"] = swc.SWS_CONF['GPUS']
        if uparams["node_type"] == "ppc64le":
            job_parameters["mem-per-cpu"] = swc.SWS_CONF['NODE_DEFINE'][0]['mem_cpu']
        if uparams["node_type"] == "arm":
            job_parameters["mem-per-cpu"] = swc.SWS_CONF['NODE_DEFINE'][1]['mem_cpu']
        if uparams["node_type"] == "x86":
            job_parameters["mem-per-cpu"] = swc.SWS_CONF['NODE_DEFINE'][2]['mem_cpu']

        if mode == swc.SWS_CONF['INTERACTIVE_MODE']:
            job_parameters["wait"] = 0

        if mode in [swc.SWS_CONF['INTERACTIVE_MODE'], swc.SWS_CONF['SCRIPT_MODE']]:
            job_parameters["export"] = "ALL"

        return job_parameters

    # takes a dictionary and creates the srun command and infers layout of job
    def build_command_internal(self, params):
        job_parameters = params.copy()
        to_del = []
        for k,v in job_parameters.items():
            if v == "" or v == None:
                to_del.append(k)
        for item in to_del:
            del job_parameters[item]

        cpu_flag = 1
        multiplier = swc.SWS_CONF['MULTIPLIER']

        partition = job_parameters["partition"]
        q_num = int(partition.split('x')[1]) if "gpu" in partition else 0

        if q_num >= 1 and q_num<=4:
            multiplier = q_num
            if job_parameters["node_type"] == "ppc64le":
                job_parameters["partition"] = "gpu"
            if job_parameters["node_type"] == "arm":
                job_parameters["partition"] = "arm"
            if job_parameters["node_type"] == "x86":
                job_parameters["partition"] = "x86"                                
        elif q_num >=8 and q_num <= 16:
            multiplier = 4
            job_parameters["nodes"] = q_num // 4
            if job_parameters["node_type"] == "ppc64le":
                job_parameters["partition"] = "gpu"
            if job_parameters["node_type"] == "arm":
                job_parameters["partition"] = "arm"
            if job_parameters["node_type"] == "x86":
                job_parameters["partition"] = "x86"      
        else:
            # cpu job
            cpu_flag = 0
            multiplier = 4
            c_num = int(partition.split('n')[1]) if "cpun" in partition else 0
            if c_num > 0:
                job_parameters["partition"] = "cpu"
            job_parameters["nodes"] = c_num
            if job_parameters["node_type"] == "arm":
                c_num = int(partition.split('n')[1]) if "cpux" in partition else 0
                job_parameters["partition"] = "arm"
                job_parameters["nodes"] = 1
            if job_parameters["node_type"] == "x86":
                c_num = int(partition.split('n')[1]) if "cpux" in partition else 0
                job_parameters["partition"] = "x86"
                job_parameters["nodes"] = 1

        if job_parameters["node_type"] == "ppc64le":
            gpu_type = swc.SWS_CONF['NODE_DEFINE'][0]['gpu_type']
        if job_parameters["node_type"] == "arm":
            gpu_type = swc.SWS_CONF['NODE_DEFINE'][1]['gpu_type']
        if job_parameters["node_type"] == "x86":
            gpu_type = swc.SWS_CONF['NODE_DEFINE'][2]['gpu_type']

        job_parameters["gres"] = "gpu:{}:{}".format(gpu_type,job_parameters.pop("gpus")*multiplier*cpu_flag)

        job_parameters["sockets-per-node"] = 2 if multiplier > 2 else 1

        cpg = job_parameters.pop("cpu_per_gpu")

        if cpu_flag == 1:
            job_parameters["cores-per-socket"] = math.ceil(cpg / job_parameters["threads-per-core"] * multiplier / job_parameters["sockets-per-node"])
            job_parameters["ntasks-per-node"] = job_parameters["cores-per-socket"]*job_parameters["sockets-per-node"]*job_parameters["threads-per-core"]
        elif cpu_flag == 0:
            job_parameters["cores-per-socket"] = 1
            job_parameters["ntasks-per-node"] = 1

        hrs = job_parameters["time"]

        # disabled for no debug queue
        # if hrs <= swc.SWS_CONF['HOURS_DEBUG'] and q_num>=1 and q_num<=4:
        #     job_parameters["partition"] = swc.SWS_CONF['DEBUG_PARTITION']
        job_parameters["time"] = "{}:00:00".format(hrs)

        job_parameters.pop("node_type")

        return job_parameters

    # takes a command dicitonary and makes it into an executable command
    def command_dict_to_command(self, command_dict, mode):
        if mode == swc.SWS_CONF['INTERACTIVE_MODE']:
            command = swc.SWS_CONF['SLURM_RUN']
        elif mode == swc.SWS_CONF['ALLOCATION_MODE']:
            command = swc.SWS_CONF['SLURM_ALLOC']
        else:
            # logic in build command makes sure you never come here
            # but if you do change it, let default be
            command = swc.SWS_CONF['SLURM_RUN']

        for k,v in command_dict.items():
            command += " --{}={}".format(k,v)

        # Add a shell to for interactive session
        if mode == swc.SWS_CONF['INTERACTIVE_MODE']:
            command += " {} {}".format("--pty", swc.SWS_CONF['SHELL'])

        return command

    # takes a command dicitonary and makes it into a runnable script
    # from misc it takes any non scheduler commands and comments and adds them to the script buffer
    def command_dict_to_script(self, command_dict, misc):
        script_buffer = ""

        script_buffer = swc.SWS_CONF['SHEBANG'] + "\n"
        for k,v in command_dict.items():
            t = k
            if t == "job_name":
                t = "job-name"
            script_buffer += "{} --{}={}\n".format(swc.SWS_CONF['SLURM_BATCH'], t, v)

        script_buffer += "\n"
        for (idx, comm) in misc:
            if idx == swc.SWS_CONF['NON_BATCH_COMMAND'] or idx == swc.SWS_CONF['COMMENT']:
                script_buffer += "{}\n".format(comm)

        return script_buffer

    # create the exec command for the container
    def get_container_exec_command(self, command_dict, mode):
        command = ""
        img = ""
        gpu_flag = ""

        if "singularity" in command_dict:
            img = command_dict.pop("singularity")
            if command_dict['nodes'] == 1:
                gpu_flag = " --nv" if 'gpu' in command_dict['partition'] else ""
            else:
                raise TypeError("{}Running a container interactively only works on one node now!{}".format(FAIL, ENDC))
            command = "\nmodule load singularity"
            command += "\n{} {}{} {}".format("singularity", mode, gpu_flag, img)

        return command

    # Takes a dictionary and resolves certain values if they are environment variables
    def resolve_env_vars(self, conf):
        for k, v in conf.items():
            if type(v) == str:
                if v[0] == "$":
                    conf[k] = os.environ[v[1:]]

        return

    def __init__(self):
        self._job_parameters = {}
        self._rules = {"partition": partial(self.check_partitions),
                        "time": partial(self.check_time),
                        "node_type": partial(self.check_node_type),
                        "cpu_per_gpu": partial(self.check_cpu_per_gpu),
                        "singularity": partial(self.check_container)}
        self._conf = swc.SWS_CONF

        self.resolve_env_vars(self._conf)
        globals().update(self._conf)

        return

    ################################# Some Build Fn Wrappers #######################################

    # to build srun command
    def build_command(self, args, u_args, mode):
        cur_mode = swc.SWS_CONF['INTERACTIVE_MODE']
        if mode == 'interactive':
            cur_mode = swc.SWS_CONF['INTERACTIVE_MODE']
        elif mode == 'allocation':
            cur_mode = swc.SWS_CONF['ALLOCATION_MODE']
        else:
            raise ValueError("Invalid mode specified for building command!")

        uparams = {}
        uparams["partition"] = args.partition[0]
        uparams["cpu_per_gpu"] = swc.SWS_CONF['CPU_PER_GPU_DEFAULT'] if type(args.cpu_per_gpu) == int else args.cpu_per_gpu[0]

        uparams["node_type"] = swc.SWS_CONF['NODE_TYPE_DEFAULT']
        # print(swc.SWS_CONF['NODE_DEFINE'][0]['gpu_type'])

        wtf = args.time[0]
        try:
            hh, mm, ss = wtf.split(':')
            hrs = int(hh)
            if int(mm) > 0:
                hrs = hrs + 1
        except ValueError:
            hrs = int(wtf)
        uparams["time"] = int(hrs)           

        if "node_type" in args:
            uparams["node_type"] = args.node_type[0]

        if "singularity" in args:
            if args.singularity == "84r":
                uparams["singularity"] = ""
            else:
                uparams["singularity"] = args.singularity[0]

        if "reservation" in args:
            if args.reservation == "84r":
                uparams["reservation"] = ""
            else:
                uparams["reservation"] = args.reservation[0]

        self._job_parameters = self.job_parameters_init(uparams, mode=cur_mode)
        self.parameter_checks(self._job_parameters, u_args)
        command_dict = self.build_command_internal(self._job_parameters)
        
        # Inserts a singularity exec command after the srun command above
        singularity_command = self.get_container_exec_command(command_dict, "shell")
        command_buffer = self.command_dict_to_command(command_dict, mode=cur_mode)
        command_buffer += "{}".format(singularity_command)

        return command_buffer

    # to build sbatch script
    def build_run_script(self, run_script, u_args):
        print(".........Run Script received {}.........\n".format(run_script))
        read_data = None
        with open(run_script) as f:
            read_data = f.read()
        print(read_data)
        script_data = read_data.split("\n")

        script_data = [x.strip() for x in script_data if x != ""]

        # following takes the lines of the script and tags them with an integer for identification
        scommands = []
        for x in script_data:
            if x[:len(swc.SWS_CONF['SLURM_BATCH'])] == swc.SWS_CONF['SLURM_BATCH']:
                scommands.append((swc.SWS_CONF['BATCH_COMMAND'],x))
            elif (x[0] == "#" and x[1:1+len(swc.SWS_CONF['SHELL'])] == swc.SWS_CONF['SHELL']) or (x[0:2] == "#!" and x[2:2+len(swc.SWS_CONF['SHELL'])] == swc.SWS_CONF['SHELL']):
                scommands.append((3,x))
            elif x[0] == '#':
                scommands.append((swc.SWS_CONF['COMMENT'],x))
            else:
                scommands.append((swc.SWS_CONF['NON_BATCH_COMMAND'],x))

        uparams = {}
        for sc in scommands:
            # if it is a BATCH command
            if sc[0] == swc.SWS_CONF['BATCH_COMMAND']:
                p = sc[1].split(" ")[1].split("=")
                key = p[0].split("--")[1]
                if key == "time":
                    try:
                        hh, mm, ss = p[1].split(':')
                        hrs = int(hh)
                        if int(mm) > 0:
                            hrs = hrs + 1
                    except ValueError:
                        hrs = int(p[1])
                    uparams[key] = int(hrs)

                uparams[key] = int(p[1]) if p[1].isdigit() else p[1]

        if "partition" not in uparams:
            raise ValueError("Need Partition!")
        if "cpu_per_gpu" not in uparams:
            uparams["cpu_per_gpu"] = swc.SWS_CONF['CPU_PER_GPU_DEFAULT']
        if "time" not in uparams:
            uparams["time"] = swc.SWS_CONF['HOURS_DEFAULT']

        # params created
        self._job_parameters = self.job_parameters_init(uparams, mode=swc.SWS_CONF['SCRIPT_MODE'])
        self.parameter_checks(self._job_parameters, u_args)
        command_dict = self.build_command_internal(self._job_parameters)

        # Inserting container execution command at the start of script, after SBATCH commands
        singularity_command = self.get_container_exec_command(command_dict, "exec")
        if len(singularity_command) > 0:
            sing_exec_command = singularity_command.split("\n")[2]
            singularity_command = singularity_command.split("\n")[1]
            for i in range(len(scommands)):
                if scommands[i][0] == swc.SWS_CONF['NON_BATCH_COMMAND']:
                    scommands[i] = (scommands[i][0], sing_exec_command + " " + scommands[i][1])

        scommands.insert(0, (swc.SWS_CONF['NON_BATCH_COMMAND'], singularity_command))

        script_buffer = self.command_dict_to_script(command_dict, scommands)

        return script_buffer

    ############################## Some Read-Accessible Variables ##################################
    @property
    def job_parameters(self):
        return self._job_parameters


########################################## Testing fns #############################################

def check_command(command, list_of_checks):
    for item in list_of_checks:
        if item not in command:
            print("Can't find {} in {}".format(item, command))
            return 0
    return 1


def run_command_tests():
    num_tests = 0
    num_tests_passed = 0
    logs = "Command Tests\n"

    argStruct = namedtuple("argStruct", "partition cpu_per_gpu time singularity")
    user_arguments = ["partition", "cpu_per_gpu", "time", "singularity"]
    bldr = Builder()

    #################################### Partition Tests ###########################################
    print("Running Partition Tests...")
    logs += "\nRunning Partition Tests...\n"

    for p in swc.SWS_CONF['ALLOWED_PARTITIONS']:
        args = argStruct(partition=[p], cpu_per_gpu=[16], time=['4'], singularity=[""])
        command = bldr.build_command(args, user_arguments, 'interactive')

        num_tests += 1
        temp = check_command(command, [" --partition={}".format(p)])
        num_tests_passed += temp
        passfail_msg = TEST_PASSED if temp == 1 else TEST_FAILED
        logs += "\nTest num:{}\n{}\n{}\n{}\n".format(num_tests, args, command, passfail_msg)


    ####################################### Time Tests #############################################
    print("Running Time Tests...")
    logs += "\n\nRunning Time Tests...\n"

    test_time = 1
    args = argStruct(partition=["gpux1"], cpu_per_gpu=[16], time=[test_time], singularity=[""])
    command = bldr.build_command(args, user_arguments, 'interactive')

    num_tests += 1
    temp = check_command(command, [" --time={}:00:00".format(test_time),
                                    " --partition={}".format(swc.SWS_CONF['DEBUG_PARTITION'])])
    num_tests_passed += temp
    passfail_msg = TEST_PASSED if temp == 1 else TEST_FAILED
    logs += "\nTest num:{}\n{}\n{}\n{}\n".format(num_tests, args, command, passfail_msg)

    args = argStruct(partition=["gpux16"], cpu_per_gpu=[16], time=[test_time], singularity=[""])
    command = bldr.build_command(args, user_arguments, 'interactive')

    num_tests += 1
    temp = check_command(command, [" --time={}:00:00".format(test_time),
                                    " --partition={}".format("gpux16")])
    num_tests_passed += temp
    passfail_msg = TEST_PASSED if temp == 1 else TEST_FAILED
    logs += "\nTest num:{}\n{}\n{}\n{}\n".format(num_tests, args, command, passfail_msg)

    ####################################### Cpu Tests ############################################
    print("Running Other Tests...")
    logs += "\n\nRunning Other Tests...\n"

    # args = argStruct(partition=["cpu"], cpu_per_gpu=[16], time=[1], singularity=[""])
    # command = bldr.build_command(args, user_arguments, 'interactive')

    num_tests += 1
    temp = check_command(command, [" --ntasks-per-node={}".format(swc.SWS_CONF['NTASKS_PER_NODE_CPU']),
                                    " --cores-per-socket={}".format(swc.SWS_CONF['CORES_PER_SOCKET_CPU']),
                                    " --gres=gpu:v100:{}".format(0)])
    num_tests_passed += temp
    passfail_msg = TEST_PASSED if temp == 1 else TEST_FAILED
    logs += "\nTest num:{}\n{}\n{}\n{}\n".format(num_tests, args, command, passfail_msg)

    return num_tests, num_tests_passed, logs

def run_script_tests():
    num_tests = 0
    num_tests_passed = 0
    logs = "Script Tests\n"

    # user_arguments = ["partition", "cpu_per_gpu", "time", "job_name", "output", "error", "singularity"]
    # bldr = Builder()
    # final_run_script_buffer = bldr.build_run_script(args.run_script[0], user_arguments)
    return num_tests, num_tests_passed, logs

def run_e2e_tests(log_flag):
    test_fns = {"Command": partial(run_command_tests),
                "Script": partial(run_script_tests)}
    num_tests = len(test_fns)
    total_logs = ""

    total_nt = 0
    total_ntp = 0
    test_num = 1
    for test_name, cur_test in test_fns.items():
        str1 = "Part {}/{}: Running {} Tests...".format(test_num, num_tests, test_name)
        print(str1)

        nt, ntp, logs = cur_test()
        total_nt += nt
        total_ntp += ntp

        str2 = "Part {}/{} passed {} out of {} tests!\n".format(test_num, num_tests, ntp, nt)
        print(str2)

        total_logs += "Part {}/{} {}\n{}\n{}\n\n".format(test_num, num_tests, logs, str2, TEST_DIVIDER)
        test_num += 1


    finalstr = "\nTesting overview: {} out of {} completed and passed".format(total_nt, total_ntp)
    print(finalstr)
    total_logs += finalstr

    if log_flag == True:
        with open("swtools_logs.txt", 'w') as f:
            f.write(total_logs)


# esting is ignored if this python script is imported else where
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="HAL Slurm Wrapper Suite v1.1 Tools Library",
        usage="python3 swtools.py [-h] [-l]")

    parser.add_argument("-l", "--log",
        help="Create a local text file to log all the tests",
        action='store_true')

    args = parser.parse_args()

    print("Running End-to-End Tests...\n")
    run_e2e_tests(args.log)
    print("Run Complete!")
    if args.log == True:
        print("Check local logs for more info.")

# end of script
