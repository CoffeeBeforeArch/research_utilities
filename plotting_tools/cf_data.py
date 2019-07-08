# This script collects the unique basic block vectors for each kernel
# in a specified directory
# By: Nick from CoffeeBeforeArch

from sys import argv
import os
import numpy as np

def cf_data(bbv_file):
    # Assume bb_log.txt is within the app_name directory
    app_name = bbv_file.split("/")[-2]

    # This function generates two log files
    individual_log = "i_log.txt"
    aggregate_log = "a_log.txt"

    # Clear the files if they exist, otherwise create them
    path = "/".join(bbv_file.split("/")[:-1])
    open(path + "/" + individual_log, "w+").close()
    open(path + "/" + aggregate_log, "w+").close()

    # Dictionary to keep track of unique control flow paths
    unique_kernels = {}

    # Read in all the lines first
    lines = []
    kid = 0
    with open(bbv_file, "r") as f:
        lines = f.readlines()

    # Go over all the lines using a while loop
    i = 0
    while i < len(lines):

        # Get the kernel name
        kernel_name = lines[i]

        # Only add unique kernels to the dictionary
        if kernel_name not in unique_kernels.keys():
            unique_kernels[kernel_name] = []
        i += 1

        # Get gridDim.x
        gx = int(lines[i])
        i += 1

        # Get gridDim.y
        gy = int(lines[i])
        i += 1

        # Calculate the total number of TBs
        num_tbs = gx * gy

        # Get the number of basic blocks in the kernel
        num_bbs = int(lines[i])
        i += 1

        # Extract the BBVs for each kernels
        kernel_bbs = []
        end_of_kernel = i + num_tbs
        while i < end_of_kernel:
            kernel_bbs.append(lines[i])
            i += 1

        # Collect only the unique basic block paths
        # Not necessary, but reduces potentially expensive final computation
        numpy_kernel = np.array(kernel_bbs)
        unique_elements, counts_elements = np.unique(numpy_kernel, return_counts=True)

        # Dump data to a logfile
        path = "/".join(bbv_file.split("/")[:-1])
        with open(path + "/" + individual_log, "a+") as f:
            f.write(kernel_name.rstrip() + " " + str(len(unique_elements)) + "\n")

        # Add them to the dictionary
        for x in unique_elements:
            unique_kernels[kernel_name].append(x)

        # Increment the kernel id
        kid += 1

    # Get only the unique control flow paths across all kernel launches
    keys = []
    values = []
    paths = []
    for k, v in unique_kernels.items():
        # Append kernel name without newline character
        keys.append(k.rstrip())

        # Final reduction to unique paths
        numpy_kernel = np.array(v)
        unique_elements, counts_elements = np.unique(numpy_kernel, return_counts=True)

        # Collect total number of unique paths
        values.append(len(counts_elements))

    # Dump data to a logfile
    path = "/".join(bbv_file.split("/")[:-1])
    with open(path + "/" + aggregate_log, "a+") as f:
        for i in range(len(keys)):
            f.write(keys[i] + " " + str(values[i]) + "\n")

def main():
    # Walk the directory finding all bb_log.txt files
    script,base_dir = argv
    for root, dirs, files in os.walk(base_dir):
        for name in files:
            if("bb_log" in name):
                cf_data(root + "/" + name)

if __name__ == "__main__":
    main()
