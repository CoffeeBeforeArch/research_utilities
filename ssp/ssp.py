# This script implements Spatial SimPoint
# By Nick from CoffeeBeforeArch

# For command line arguments
from sys import argv
# For launching child apps
import subprocess as sp
# For clustering and more advanced math
import numpy as np
# For making directories
import os
# For basic statistics
import math
# For reading config and profiler output
import yaml
import csv
# For random selection from clusters
import random
import pprint
# Read in the nvprof input as a dictionary
def read_profile(nvprof_file):
    lines = []
    with open(nvprof_file, 'r') as f:
        lines = f.readlines()
    return lines

# Parse profiling data for TB size, shmem usage, reg usage, etc.
def parse_profile(profile, grid, block, regs, s_shmem, d_shmem):
    # Try and avoid bad logs
    if len(profile) < 3:
        return

    # Extract the heading and units
    headings = profile[3].replace("\"", "").split(",")
    units = profile[4].replace("\"", "").split(",")

    # Pre-calculate the indices for what we are extrating
    name = headings.index("Name")
    gx = headings.index("Grid X")
    gy = headings.index("Grid Y")
    gz = headings.index("Grid Z")
    bx = headings.index("Block X")
    by = headings.index("Block Y")
    bz = headings.index("Block Z")
    reg = headings.index("Registers Per Thread")
    s_shmem_i = headings.index("Static SMem")
    d_shmem_i = headings.index("Dynamic SMem")

    # Go over the actual lines
    for i in range(5, len(profile)):
        # Split the line
        line = profile[i].replace("\"", "").split(",")
        if "CUDA " not in line[name]:
            grid.append([int(line[gx]), int(line[gy]), int(line[gz])])
            block.append([int(line[bx]), int(line[by]), int(line[bz])])
            regs.append(int(line[reg]))
            s_shmem.append((float(line[s_shmem_i]),units[s_shmem_i]))
            d_shmem.append((float(line[d_shmem_i]),units[d_shmem_i]))

# Calculate max occupancy per-SM
def max_occupancy(blocks, regs, s_shmem, d_shmem):
    print(blocks, regs, s_shmem, d_shmem)
    return

# Read the YAML File in
def read_yaml(yaml_file):
    # Load in entire dict from the yaml
    yaml_dict = {}
    with open(yaml_file, 'r') as f:
        yaml_dict = yaml.load(f)
    return yaml_dict

# Launch each app and copy the basic block logs
def launch_instrument(launch_string, app_dir):
    p = sp.Popen(launch_string, env=os.environ, shell=True)
    p.wait()
    sp.call("mv bb_log* " + app_dir + "/.", shell=True)

# Launch each app and copy profiler output
def launch_profile(launch_string, app_dir):
    p = sp.Popen(launch_string, env=os.environ, shell=True)
    p.wait()
    sp.call("mv nvprof.csv " + app_dir + "/.", shell=True)

# Goes through all benchmarks in the YAML file and launches all apps
# with all set inputs
def launch_benchmarks(yaml_dict):
    # Launch each of the benchmarks
    for bench, bench_dict in yaml_dict.items():
        # Create a directory for each benchmark suite
        if not os.path.exists(bench):
            os.makedirs(bench)

        # Get the directories for launching the apps
        exec_dir = bench_dict["exec_dir"]
        data_dir = bench_dict["data_dirs"]
        launch_arg = bench_dict["param"]
        profile_arg = bench_dict["profile"]

        # Go over all the apps for this benchmark
        for exec_dicts in bench_dict["execs"]:
            for app, inputs in exec_dicts.items():
                # Create the full path to the app
                app_path = exec_dir + app

                # Make a directory for each app we see if it doesn't exist
                app_dir = bench + "/" + app
                print(app_dir)
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
                    profile_string = profile_arg + " " + app_path + " " + final_arg
                    launch_instrument(launch_string, app_dir)
                    launch_profile(profile_string, app_dir)


# Helper function to unpack the logfile
def parse_kernel(kernel, k_name, i_counts, bbs):
    # Read all the lines in
    lines = []
    with open(kernel, 'r') as f:
        lines = f.readlines()

    # Unpack the data
    i = 0
    k_name.append(lines[i])
    i += 1

    # Unpack the insns counts and bbv info
    while(i < len(lines)):
        i_counts.append(int(lines[i]))
        i += 1
        bbs.append([float(x) for x in lines[i].rstrip().split()])
        i += 1

# Calculates max TBs per SM
def max_tbs():
    return

# Performs clustering using some algorithm
def cluster_advanced(app, logs):
    return

# Clustering function based on exact matches
def cluster_naive(app, logs, profile):
    # Unpack the profile
    lines = read_profile(profile)

    # Get the characteristic from non-instrumented file
    grids = []
    blocks = []
    regs = []
    s_shmem = []
    d_shmem = []
    parse_profile(lines, grids, blocks, regs, s_shmem, d_shmem)

    # Unpack each kernel
    for i, kernel in enumerate(logs):
        # Arrays to be filled by parse_kernel
        k_name = []
        i_counts = []
        bbs = []

        # Unpack each kernel
        parse_kernel(kernel, k_name, i_counts, bbs)

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
            weight = float((len(tmp) * v)) / total

            # Append the weighted values and indices
            indices.append(tmp)
            weighted_values.append(weight)

        # Calculate max TBs for this kernel
        max_per_sm = max_occupancy(blocks[i], regs[i], s_shmem[i], d_shmem[i])

        # Calculate the number of TBs from each cluster
        tbs_per_cluster = []
        for w in weighted_values:
            continue

# Find all the log files and create a dict of apps and file paths
def get_logs(i_dir, execs, app_logs, app_prof):
    # Walk the input directory to find the bb_log files
    for r, d, f in os.walk(i_dir):
        # Each app gets an entry in the dict
        for app in d:
            if app not in app_logs.keys() and app in execs:
                app_logs[app] = []
                app_prof[app] = ""

        # Add the individual log and profile paths to the dict
        for name in f:
            # Hard coded file name for now
            if("bb_log" in name):
                for app in app_logs.keys():
                    if app in r and app in execs:
                        app_logs[app].append(r + '/' + name)
            elif("nvprof" in name):
                for app in app_prof.keys():
                    if app in r and app in execs:
                        app_prof[app] = r + '/' + name

def main():
    # Read out the yaml file to get executable and data dirs
    yaml_file = "apps.yml"
    yaml_dict = read_yaml(yaml_file)

    # Keys contain the output directories
    i_dirs = yaml_dict.keys()

    # If we are not analyzing a specific directory, go ahead and run
    # the benchmarks
    #if len(argv) == 1:
    #    launch_benchmarks(yaml_dict)

    for i_dir in i_dirs:
        # Create a dict of app names keys and list of log file value
        app_logs = {}
        app_prof = {}
        execs = [item.keys()[0] for item in yaml_dict[i_dir]["execs"]]
        get_logs(i_dir, execs, app_logs, app_prof)

        # Check to see if we already created the output dir on a previous
        # launch. If not, create it.
        o_dir = i_dir + '-ssp'
        if not os.path.exists(o_dir):
            os.makedirs(o_dir)

        # Unpack the files
        for app, logs in app_logs.items():
            if "irregular" in i_dir:
                continue
                cluster_advanced(app, logs)
            elif "regular" in i_dir:
                cluster_naive(app, logs, app_prof[app])

if __name__ == "__main__":
    main()
