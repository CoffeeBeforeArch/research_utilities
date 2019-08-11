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
# For plotting
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Some parameter info for Volta
volta_sms = 80

threads_per_warp = 32
warps_per_sm = 64
threads_per_sm = 2048
shmem_per_sm = 98304

register_file_size = 65536
register_allocation_unit_size = 256

max_registers_per_thread = 255
shmem_allocation_unit_size = 256
warp_allocation_granularity = 4
max_tb_size = 1024
max_tb_per_sm = 32

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

def my_ceil(a, b):
    return math.ceil(a * b) / b

def my_floor(a, b):
    return math.floor(a * b) / b

# Recursive function to return gcd of a and b
def gcd(a,b):
    if a == 0:
        return b
    return gcd(b % a, a)

# Function to return LCM of two numbers
def lcm(a,b):
    return (a*b) / gcd(a,b)

def block_warps(threads_per_block):
    return math.ceil(threads_per_block / float(threads_per_warp))

def block_registers(threads_per_block, regs):
    return my_ceil(regs * threads_per_warp, register_allocation_unit_size) * block_warps(threads_per_block)

def sm_regs(regs):
    return my_floor(register_file_size / my_ceil(regs * threads_per_warp, register_allocation_unit_size), warp_allocation_granularity) * my_ceil(regs * threads_per_warp, register_allocation_unit_size)

def block_shared_memory(shmem):
    return my_ceil(shmem, shmem_allocation_unit_size)

def tb_warp_limit(threads_per_block):
    return min(max_tb_per_sm, math.floor(warps_per_sm / block_warps(threads_per_block)))

def reg_limit(regs, threads_per_block):
    return math.floor(sm_regs(regs) / block_registers(threads_per_block, regs))

def shmem_limit(shmem):
    if(shmem > 0):
        return math.floor(shmem_per_sm / block_shared_memory(shmem))
    else:
        return max_tb_per_sm

# Calculate max occupancy per-SM
def max_occupancy(blocks, regs, s_shmem, d_shmem):
    # Calculate # warps
    threads_per_block = blocks[0] * blocks[1] * blocks[2]

    # Calculate shmem per warp
    shmem = 0
    if "K"  in s_shmem[1]:
        shmem += 1024 * s_shmem[0]
    else:
        shmem += s_shmem[0]

    if "K"  in d_shmem[1]:
        shmem += 1024 * d_shmem[0]
    else:
        shmem += d_shmem[0]

    # Calculate
    return min(tb_warp_limit(threads_per_block), reg_limit(regs, threads_per_block), shmem_limit(shmem))

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
def parse_kernel(kernel, k_name, bbs):
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
        bbs.append([int(x) for x in lines[i].rstrip().split()])
        i += 1

# Calculates max TBs per SM
def max_tbs():
    return

def plot_irregular(app, logs):
    # Unpack each kernel
    for i, kernel in enumerate(logs):
        print(app)
        # Arrays to be filled by parse_kernel
        k_name = []
        bbs = []

        # Unpack each kernel
        parse_kernel(kernel, k_name, bbs)

        # Get total instruction count
        total = sum([sum(x) for x in bbs])

        # Plot the linear order of each basic block
        for j in range(len(bbs[0])):
            indiv_block = [x[j] for x in bbs]
            indiv_block.sort()
            plt.title("Basic Block: " + str(j) + " For kernel: " + str(i))
            plt.scatter(range(len(indiv_block)), indiv_block)
            plt.savefig("kernel_"+str(i)+"_bb_"+str(j)+".png")
            plt.close()


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
        bbs = []

        # Unpack each kernel
        parse_kernel(kernel, k_name, bbs)

        # Get total instruction count
        i_counts = [sum(x) for x in bbs]
        total = sum(i_counts)

        # Weigh each cluster by instruction count
        values = np.unique(i_counts)
        weighted_values = []
        clusters = []
        indices = []
        for v in values:
            # Find all indices with this i-count
            tmp = np.where(i_counts == v)[0]
            clusters.append(tmp)

            # Multiply by number of instructions
            weight = float((len(tmp) * v)) / total

            # Append the weighted values and indices
            indices.append(tmp)
            weighted_values.append(weight)

        # Calculate max TBs per sm for this kernel
        max_per_sm = max_occupancy(blocks[i], regs[i], s_shmem[i], d_shmem[i])

        # Calculate the max TBs for a fully occupied GPU
        sub_grid_tbs = max_per_sm * volta_sms

        # Calculate the MAX number of TBs from each cluster
        tbs_per_cluster = []
        for w in weighted_values:
            tbs_per_cluster.append(math.ceil(sub_grid_tbs * w))

        # Choose sequential for now
        ssp_clusters = []
        remaining_tbs = sub_grid_tbs
        while remaining_tbs > 0:
            for j, tbs in enumerate(tbs_per_cluster):
                for k in range(min(int(tbs), len(clusters[j]))):
                    ssp_clusters.append(clusters[j][k])
                    remaining_tbs -= 1
                    if remaining_tbs == 0:
                        break
                if remaining_tbs == 0:
                    break
            break

        ssp_clusters.sort()
        with open(str(i+1) + ".txt", "w+") as f:
            f.write(str(len(ssp_clusters)) + '\n')
            for tb in ssp_clusters:
                f.write(str(tb) + " ")


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
    if len(argv) == 1:
        launch_benchmarks(yaml_dict)
    """
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
                #cluster_advanced(app, logs)
            elif "regular" in i_dir:
                cluster_naive(app, logs, app_prof[app])
    """
if __name__ == "__main__":
    main()
