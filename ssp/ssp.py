# This script implements Spatial SimPoint
# By Nick from CoffeeBeforeArch

from sys import argv
import os
import numpy as np

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
        i_counts.append([int(lines[i])])
        i += 1
        bbs.append([float(x) for x in lines[i].rstrip().split()])
        i += 1

# Clustering function
def cluster(app, logs):
    # Unpack each kernel
    for kernel in logs:
        # Arrays to be filled by parse_kernel
        k_name = []
        dim = []
        i_counts = []
        bbs = []

        # Unpack each kernel
        parse_kernel(kernel, k_name, dim, i_counts, bbs)

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
    script, i_dir, o_dir = argv

    # Create a dict of app names keys and list of log file value
    app_logs = {}
    get_logs(i_dir, app_logs)

    # Check to see if we already created the output dir on a previous
    # launch. If not, create it.
    o_dir += '/ssp'
    if not os.path.exists(o_dir):
        os.makedirs(o_dir)

    # Unpack the files
    for app, logs in app_logs.items():
        cluster(app, logs)

if __name__ == "__main__":
    main()
