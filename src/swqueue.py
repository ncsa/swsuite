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
# /opt/apps/swsuite/src/swqueue.py
# version 1.0
#

import subprocess
import re
import random
import argparse

NUM_COMPUTE_NODES = 16
COMPUTE_NODES = ['hal{}{}'.format("0" if i < 10 else "", i) for i in range(1, 1+NUM_COMPUTE_NODES)]

def display(hide_names, jobid_info, node_info, allowed_users, display_select_users):
    MAX_PROC = 160
    BIN_SIZE = 16
    MAX_NUM_GPUS = 4
    NUM_COMPUTE_NODES = 16
    BARLENGTH = 7
    DATABARLENGTH = BARLENGTH - 2
    CGGAP= 4
    NL = '\n'

    VDIV = "|"
    HDIV = "-"
    HDIV2 = "#"
    LINE_BREAK = (VDIV + HDIV*7) + (VDIV + HDIV*BARLENGTH)*(MAX_PROC//BIN_SIZE) + VDIV*1 + "*"*(CGGAP+1) + VDIV + (HDIV*6 + VDIV)*MAX_NUM_GPUS + (HDIV*7 + VDIV)

    BLACK_TEXT = '\033[30m'
    WHITE_TEXT = '\033[97m'

    c = {
    '':'',
    "NONE" : '',
    "BLINK" : '\033[5m',
    "BOLDUNDERLINED" : "\033[1;4m",

    "ENDC" : '\033[0m',

    "MAGENTA" : '\033[35m',
    "RED" : '\033[91m',
    "YELLOW" : '\033[93m',
    "GREEN" : '\033[32m',
    "CYAN" : '\033[36m',

    "BGMAGENTA" : "\033[45m" + WHITE_TEXT,
    "BGRED" : "\033[41m" + WHITE_TEXT,
    "BGYELLOW" : "\033[43m" + BLACK_TEXT,
    "BGGREEN" : "\033[42m" + BLACK_TEXT,
    "BGCYAN" : "\033[46m" + BLACK_TEXT,

    "BGBLACK" : '\033[40m' + WHITE_TEXT,
    "BGWHITE" : '\033[107m' + BLACK_TEXT,

    "BLINKBGMAGENTA" : '\033[5;45m'

    }

    def colorize(x, params):
        st = ""
        for elem in params:
            st += c[elem] 
        return "{}{}{}".format(st, x, c["ENDC"])

    def check_load(num):
        if num == None:
            return ""
        
        MP = MAX_PROC//2

        unit = MP//3
        retcolor = []

        if num == 0:
            retcolor += []
        elif num > 0 and num <= unit:
            retcolor += ["BGGREEN"]
        elif num > unit and num <=unit*2 :
            retcolor += ["BGYELLOW"]
        elif num > unit*2 and num <= unit*3:
            retcolor += ["BGRED"]
        else:
            retcolor += ["BLINK", "BGMAGENTA"]

        return retcolor

    def get_load_bar_color(num):
        if num == None:
            return ""

        MP = MAX_PROC//2

        unit = MP//3
        retcolor = ""

        if num == 0:
            retcolor += ""
        elif num > 0 and num <= unit:
            retcolor += "BGGREEN"
        elif num > unit and num <=unit*2 :
            retcolor += "BGYELLOW"
        elif num > unit*2 and num <= unit*3:
            retcolor += "BGRED"
        else:
            retcolor += "BLINK" + "BGMAGENTA"

        return retcolor

    def bar_msg_format(msg, split_index, color):

        MP = MAX_PROC // 2

        if len(msg) >= 93:
            msg = msg[0:92] + '...'

        msg2 = [" "]*(MP+1)
        for i in range(1, MP):
            if i-1 < len(msg):
                msg2[i] = msg[i-1]
        msg2 = "".join(msg2)

        flag = False
        new_msg = color
        for i in range(len(msg2)):
            if i == split_index:
                new_msg += c["ENDC"] + msg2[i]
                flag = True
            else:
                new_msg += msg2[i]

        if flag == False:
            new_msg = new_msg[0:MP+1] + c['ENDC']
        # print(len(new_msg))
        return new_msg


    ############### Testing ###################
    def get_dummy_gpu():
        return [False if random.randint(0,99999) % 2 == 0 else True for i in range(MAX_NUM_GPUS+1) ]

    def get_dummy_cpu():
        return random.randint(0,MAX_PROC+1)

    # all_cpus = [get_dummy_cpu() for i in range(NUM_COMPUTE_NODES) ]
    # all_gpus = [get_dummy_gpu() for i in range(NUM_COMPUTE_NODES) ]
    # # messages = ["hongyu2 dmu dash3 tlim33" + "k"*90 for i in range(NUM_COMPUTE_NODES)]
    # messages = ["hongyu2 dmu dash3 tlim33" for i in range(NUM_COMPUTE_NODES)]

    all_cpus = [0 for i in range(NUM_COMPUTE_NODES)]
    all_gpus = [0 for i in range(NUM_COMPUTE_NODES)]
    messages = ["" for i in range(NUM_COMPUTE_NODES)]
    ctr = 0
    for k,v in node_info.items():
        all_cpus[ctr] = v['cpus'] // 2
        all_gpus[ctr] = [True if i < v['gpus'] else False for i in range(MAX_NUM_GPUS)]
        for (jobid, user) in v['users_jobids']:
            if display_select_users == True:
                messages[ctr] += "{} {} c:{} g:{}, ".format(user, jobid, jobid_info[jobid]['cpus'], jobid_info[jobid]['gpus']) if user in allowed_users else ""
            else:
                messages[ctr] += "{} {}, ".format(user, jobid)

        ctr += 1

    ###########################################

    subprocess.run(['clear'])

    final_strings_list = [LINE_BREAK]
    print(LINE_BREAK)
    print("| nodes | 1{}CPUS{}64{}128{}160{}| 1{}GPUS{}4{} | nodes |".format("."*12, "."*13, "."*30, "."*13, " "*(CGGAP-1), "."*9, "."*10, " "*0))
    print(LINE_BREAK)
    for i in range(NUM_COMPUTE_NODES):
        node_line = " " + colorize("hal{}{}", check_load(all_cpus[i])).format("0" if i+1 < 10 else "", i+1) + " "

        ###### INITIAL ######
        print(VDIV + node_line + VDIV, end="")
        line = VDIV + node_line + VDIV

        ### CPU & MESSAGE ###
        cur_load = (all_cpus[i] if all_cpus[i] <= MAX_PROC else MAX_PROC)
        bar_color_code = get_load_bar_color(cur_load) if all_cpus[i] <= MAX_PROC else "BLINK" + "BGMAGENTA"

        message = bar_msg_format(messages[i], split_index=cur_load, color=c[bar_color_code])
        line += colorize(" ", params=[bar_color_code])* cur_load
        if hide_names == True:
            print(colorize(" ", params=[bar_color_code])* cur_load, end="")
        else:
            print(message, end="")
        space = (MAX_PROC + 1 - cur_load)
        line += " "*space
        # print(" "*(99-len(message)), end="")
        line += "-"*CGGAP
        print("-"*CGGAP, end="")


        ###### GPUS ##########
        # line += VDIV
        print(VDIV, end="")
        gpus = all_gpus[i]
        for g in range(len(gpus)):
            gpu_color = ["BGCYAN"] if gpus[g] == True else ["NONE"]
            line += colorize("   GPU{}  ".format(g+1), gpu_color) + VDIV
            print(colorize(" GPU{} ".format(g+1), gpu_color) + VDIV, end="")

        ##### FINAL END ######
        line += "->" + node_line + VDIV
        print(node_line + VDIV, end="\n")

        final_strings_list.append(line)
        final_strings_list.append(LINE_BREAK)
        print(LINE_BREAK)

    # for line in final_strings_list:
    #   print("{}{}{}".format(c["NONE"], line, c["ENDC"]))

    print("\nLegend: {} {}->{} {}->{} {} means lower to higher usage and {} {} means above expected usage.\n        Whereas {} {} means that a GPU is being {}USED{}.\n".format(c["BGGREEN"], c["ENDC"], c["BGYELLOW"], c["ENDC"], c["BGRED"], c["ENDC"], c["BGMAGENTA"] + c["BLINK"], c["ENDC"], c["BGCYAN"], c["ENDC"], c["BOLDUNDERLINED"], c["ENDC"]))


def display_full_nodes(node_info, nodes_to_display):
    for k,v in node_info.items():
        if k in nodes_to_display:
            print(k)
            print(v)
            subprocess.run(['ssh', k, 'nvidia-smi'])
            
def display_full_user(job_info, users_to_display):
    for k,v in job_info.items():
        if v['users'][0] in users_to_display and v['state'] == 'RUNNING':
            print(k)
            print(v)


def lprint(data):
    for line in data:
        print(line)

def reformat(data, divider):
    return str(data)[2:-1].split(divider)

def split_frames(m_data):
    x = []
    indices = []
    for i in range(len(m_data)):
        line = m_data[i]
        for l in line:
            if 'JobId' in l:
                indices.append(i)

    for i in range(len(indices)):
        if i+1 < len(indices):
            indices[i] = (indices[i], indices[i+1])
    indices[-1] = (indices[-1], len(m_data))

    frames = []
    for i in indices:
        frames.append(m_data[i[0]:i[1]])

    return frames

def get_nodes_from_range(node_range):
    node_range_list = node_range.split('-')
    start = int(node_range_list[0])
    end = int(node_range_list[1])
    nodes = [i for i in range(start, end+1)]
    return nodes

def get_nodes(info):
    nodes = []
    if info[0] == '[':
        info = info.replace('[', '').replace(']', '').split(',')
        for elem in info:
            if '-' in elem:
                nodes.extend(get_nodes_from_range(elem))
            else:
                nodes.append(int(elem))
    else:
        nodes = [int(info)]

    nodes = [COMPUTE_NODES[i-1] for i in nodes]
    return nodes

def get_node_to_resource_mapping(running_jobs):
    info_dict = {}
    for node in COMPUTE_NODES:
        info_dict[node] = {'cpus':0, 'gpus':0, 'users_jobids':[]}

    for k,v in running_jobs.items():
        for frame in v:
            # Process a frame below
            job_id = 0
            for line in frame:
                # numnodes = 1
                for item in line:
                    if 'JobId=' in item:
                        job_id = int(item.split('=')[1])
                    if 'UserId=' in item:
                        uid = item.split('=')[1]
                        user = uid.split('(')[0]
                        info_dict[k]['users_jobids'].append((job_id, user))

                    numnodes = 1
                    numcpus = 1
                    if 'TRES=' in item:
                        subitem = item.split(',')
                        for s in subitem:
                            if 'gres/gpu=' in s:
                                info_dict[k]['gpus'] += int(s.split('=')[1])
                            if 'cpu=' in s:
                                numcpus = int(s.split('=')[2])
                            if 'node=' in s:
                                numnodes = int(s.split('=')[1])
                        info_dict[k]['cpus'] += (numcpus//numnodes)

    return info_dict

def get_jobid_to_resouce_mapping(jobs):
    info_dict = {}

    for k,frame in jobs.items():
        # for frame in v:
        #     # Process a frame below
        #     print(frame)
        job_id = 0
        for line in frame:
            numnodes = 1
            for item in line:
                if 'JobId=' in item:
                    job_id = int(item.split('=')[1])
                    info_dict[job_id] = {'state':'UNKNOWN', 'cpus':0, 'gpus':0, 'users':[], 'nodes': [], 'submit_time':0, 'start_time':0, 'time_limit':0}

                if 'UserId=' in item:
                    uid = item.split('=')[1]
                    user = uid.split('(')[0]
                    info_dict[k]['users'].append(user)

                numnodes = 1
                numcpus = 1
                if 'TRES=' in item:
                    subitem = item.split(',')
                    for s in subitem:
                        if 'gres/gpu=' in s:
                            info_dict[k]['gpus'] += int(s.split('=')[1])
                        if 'cpu=' in s:
                            numcpus = int(s.split('=')[2])
                        if 'node=' in s:
                            numnodes = int(s.split('=')[1])
                    info_dict[k]['cpus'] += (numcpus//numnodes)

                if 'JobState=' in item:
                    info_dict[k]['state'] = item.split('=')[1]
                if 'SubmitTime=' in item:
                    info_dict[k]['submit_time'] = item.split('=')[1]
                if 'StartTime=' in item:
                    info_dict[k]['start_time'] = item.split('=')[1]
                if 'NodeList=hal' in item:
                    info_dict[k]['nodes'] = get_nodes(item.split("=hal")[1])
                if 'TimeLimit=' in item:
                    info_dict[k]['time_limit'] = item.split('=')[1]

    # for k,v in info_dict.items():
    #     print(k)
    #     print(v)

    return info_dict

def process_frames(frames):
    # map jobs to job info
    jobs = {}
    # map hal nodes to complete job info of running jobs
    # to create a picture of resource utilization
    running_jobs = {}

    for line in frames:
        consider = False
        for entry in line:
            for label in entry:
                if label == 'JobState=RUNNING':
                    consider = True

                if 'NodeList=hal' in label and consider == True:
                    nodes = get_nodes(label.split("=hal")[1])
                    for n in nodes:
                        if n not in running_jobs:
                            running_jobs[n] = [line]
                        else:
                            running_jobs[n].append(line)

                if label == 'JobState=RUNNING' or label == 'JobState=PENDING':
                    line1 = line[0]
                    for elem in line1:
                        if 'JobId' in elem:
                            jobid = int(elem.split('=')[1])
                            jobs[jobid] = line

    node_info = get_node_to_resource_mapping(running_jobs)
    jobid_info = get_jobid_to_resouce_mapping(jobs)

    return node_info, jobid_info


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--show", 
        help="Show a stylized view of the cluster with the cpu and gpu usage across all nodes.", 
        action="store_true")
    parser.add_argument("-t", "--timestep", 
        help="Specify delay of update in seconds(>= 60s), by default updates occur every 60 seconds.", 
        type=int,
        default=60)
    parser.add_argument("-m", "--monitor", 
        help="Monitor the cluster at a refresh rate either dafaulted at 60 seconds or specified by user (lower limit of 60s).", 
        action="store_true")
    parser.add_argument("-u", "--users", 
        help="Monitor by users", 
        nargs='+')
    parser.add_argument("--fpuser", 
        help="Monitor full usage of user", 
        nargs='+')
    parser.add_argument("-n", "--nodev", 
        help="Check some nodes verbosely if they don't fit in the line of colorized output", 
        nargs='+')

    return parser.parse_args()


def main():
    args = parse_args()
    if args.timestep < 60:
        raise ValueError("TimeStep needs to be >= 60s.")

    users = []
    disp_sel_users = False
    if type(args.users) == type(users):
        users.extend(args.users)
        disp_sel_users = True

    flag = True
    while flag:
        subprocess.run(["clear"])
        
        m_data = subprocess.check_output(["/opt/apps/swsuite/src/swqueue.sh"], stderr=subprocess.STDOUT)
        # m_data = ""
        # with open("scontrol_sample_data.txt", 'r') as f:
        #     m_data = f.read()

        m_data = reformat(m_data, divider='\\n')
        m_data = [line.strip().split(" ") for line in m_data]
        frames = split_frames(m_data)
        node_info, jobid_info = process_frames(frames)

        if args.show == True:
            display(False, jobid_info, node_info, allowed_users=users, display_select_users=disp_sel_users)

        nodes = []
        if type(args.nodev) == type(nodes):
            nodes.extend(args.nodev)
            display_full_nodes(node_info, nodes_to_display=nodes)

        users_for_fp = []
        if type(args.fpuser) == type(users_for_fp):
            users_for_fp.extend(args.fpuser)
            display_full_user(jobid_info, users_to_display=users_for_fp)

        flag = args.monitor
        if flag == True:
            subprocess.run(["sleep", str(args.timestep)])

if __name__ == '__main__':
    main()
