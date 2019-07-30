# This script implements Spatial SimPoint
# By Nick from CoffeeBeforeArch

from sys import argv
import subprocess as sp
import numpy as np
import os
import math
import random
import yaml

VOLTA_SMS = 80

# Launch each app and copy the data
def launch_app(launch_string, app_dir):
    p = sp.Popen(launch_string, env=os.environ, shell=True)
    p.wait()
    sp.call("mv bb_log* " + app_dir + "/.", shell=True)

# Goes through all benchmarks in the YAML file and launches all apps
# with all set inputs
def launch_benchmarks(yaml_file):
    # Load in entire dict from the yaml
    yaml_dict = {}
    with open(yaml_file, 'r') as f:
        yaml_dict = yaml.load(f)

    # Launch each of the benchmarks
    for bench, bench_dict in yaml_dict.items():
        # Create a directory for each benchmark suite
        if not os.path.exists(bench):
            os.makedirs(bench)

        # Get the directories for launching the apps
        exec_dir = bench_dict["exec_dir"]
        data_dir = bench_dict["data_dirs"]
        launch_arg = bench_dict["param"]

        # Go over all the apps for this benchmark
        for exec_dicts in bench_dict["execs"]:
            for app, inputs in exec_dicts.items():
                # Create the full path to the app
                app_path = exec_dir + app

                # Make a directory for each app we see if it doesn't exist
                app_dir = bench + "/" + app
                if not os.path.exists(app_dir):
                    os.makedirs(app_dir)

                # Go over all the inputs for this application
                for arg in inputs:
                    final_arg = str(arg)
                    # Need to add data path to input data
                    if "./data" in final_arg:
                        # Not super flexible...
                        final_arg = final_arg.split("/")
                        tmp_list = []

                        # Add data dir before relative path
                        for item in final_arg:
                            if str(item) == "data":
                                tmp_list.append(data_dir)
                                tmp_list.append(app)
                                tmp_list.append(item)
                            else:
                                tmp_list.append(item)

                        # Join the string back together
                        final_arg = "/".join(tmp_list)

                    # Launch the applications (Also copies the logs)
                    launch_string = "LD_PRELOAD=" + launch_arg + " " + app_path + " " + final_arg
                    launch_app(launch_string, app_dir)

# Helper function to unpack the logfile
def parse_kernel(kernel, k_name, dim, i_counts, bbs):
    # Read all the lines in
    lines = []
    with open(kernel, 'r') as f:
        lines = f.readlines()

    # Unpack the data
    i = 0
    k_name.append(lines[i])
    i += 1

    # Get the kernel dimensions
    dim.append(int(lines[i]));
    i += 1
    dim.append(int(lines[i]));
    i += 1

    # Get the basic block (remove this probably)
    bb = int(lines[i])
    i += 1

    # Unpack the insns counts and bbv info
    while(i < len(lines)):
        i_counts.append(int(lines[i]))
        i += 1
        bbs.append([float(x) for x in lines[i].rstrip().split()])
        i += 1

# Clustering function
def cluster_naive(app, logs):
    # Unpack each kernel
    for kernel in logs:
        # Arrays to be filled by parse_kernel
        k_name = []
        dim = []
        i_counts = []
        bbs = []

        # Unpack each kernel
        parse_kernel(kernel, k_name, dim, i_counts, bbs)

        # Get the total number of TBs
        num_tbs = dim[0] * dim[1]
        print(num_tbs)

        # Get total instruction count
        total = sum(i_counts)

        # Weigh each cluster by instruction count
        values = np.unique(i_counts)
        weighted_values = []
        indices = []
        for v in values:
            # Find all indices with this i-count
            tmp = np.where(i_counts == v)[0]

            # Multiply by number of instructions
            weight = len(tmp) * v / total

            # Append the weighted values and indices
            indices.append(tmp)
            weighted_values.append(weight)

        # Calculate max TBs for this kernel


        # Calculate the number of TBs from each cluster
        tbs_per_cluster = []
        for w in weighted_values:
            continue



# Find all the log files and create a dict of apps and file paths
def get_logs(i_dir, app_logs):
    # Walk the input directory to find the bb_log files
    for r, d, f in os.walk(i_dir):
        # Each app gets an entry in the dict
        for app in d:
            if app not in app_logs.keys():
                app_logs[app] = []

        # Add the individual log paths to the dict
        for name in f:
            # Hard coded file name for now
            if("bb_log" in name):
                for app in app_logs.keys():
                    if app in r:
                        app_logs[app].append(r + '/' + name)



def main():
    # Unpack the input and out directory arguments
    # Needs error to ensure that unpacking succeeds
    #script, i_dir, o_dir = argv

    # Create a dict of app names keys and list of log file value
    #app_logs = {}
    #get_logs(i_dir, app_logs)

    # Check to see if we already created the output dir on a previous
    # launch. If not, create it.
    #o_dir += '/ssp'
    #if not os.path.exists(o_dir):
    #    os.makedirs(o_dir)

    # Unpack the files
    #for app, logs in app_logs.items():
    #    cluster_naive(app, logs)

    launch_benchmarks("apps.yml")
if __name__ == "__main__":
    main()
