"""
This program is a parser for all Aerial Vision output files that can be
found in a subdirectory passed as an argument when running this script.

AerialVision is a neat GUI tool, but is clunky, and does not work well
when working with output from multiple runs.

This assumes that the directory structure is of the form created by
the job launching script in gpgpu-sim_simulations

To run:
    python3 aerialvision_parser.py path/to/directory

Output:
    A .csv file for each application run found
    Statistics for sampling, kernel, and application boundaries
    Plots of the statistics captured
"""

import os
import gzip
from sys import argv
import matplotlib.pyplot as plt

# Walks a path passed as an arugment and fills in dictionary
# With application name key and .gz file path value pairs
def locate_logs(dir_path, gz_dict):
    # Walk the directory passed
    for root, dirs, files in os.walk(dir_path):
        # Look at all files, and pick out only AerialVision files
        for gz_file in files:
            if("gpgpusim_visualizer" in gz_file):
                # Split the root string to get get the app and input
                # name, and make a tuple of it
                split_string = root.split("/")
                app_input = split_string[-2]
                app_name = split_string[-3]
                app_tuple = (app_name, app_input)

                # Create the full path to the gz file
                gz_path = root + "/" + gz_file

                # Add this to the dictionary
                gz_dict[app_tuple] = gz_path

# Takes a list of DRAM util averages and kernel timing information
# to print out DRAM plots
def process_dram(dram_util_averages):
    return

# Opens a GPGPU-Sim visualizer file, reads it in, then parses the data
# Takes a tuple of app-name and input, and path to the file as inputs
def parse_log(app_tuple, gz_path):
    # Unpack the app name and input
    app_name, app_input = app_tuple
    print(f"Parsing application {app_name}")

    # Value we will be collecting
    # DRAM statistics
    dram_util_total = 0
    dram_num_channels = 0
    dram_util_averages = [0.0]

    # Clock statistics
    sampling_period = 0
    prev_cycles = 0
    kernel_cycle_count = 0
    total_cycle_count = 0
    total_cycles = [0]
    kernel_boundaries = []

    # Instruction statistics
    prev_instructions = 0
    ipc_values = [0]

    # L1$ Stats
    l1_read_hit_rate = [0.0]
    l1_write_hit_rate = [0.0]

    # Read in the .gz logfile one line at a time
    with gzip.open(gz_path, "rt") as f:
        for line in f:
            # Gather each memory channels utilization statistics
            if "dramutil" in line:
                # Extract what we need from the line
                dram_line = line.split()
                channel = int(dram_line[1])
                util_percent = int(dram_line[2])

                # Check if we are starting over, or this is the first
                # instance
                if channel == 0:
                    # Don't do useless calculations
                    if dram_util_total == 0:
                        dram_util_averages.append(0)
                    # Handle where we have a non-0 average
                    else:
                        dram_util_total += util_percent
                        dram_util_averages.append(dram_util_total / dram_num_channels)

                    # Reset variables
                    dram_num_channels = 0
                    dram_util_total = 0

                # Add to the total and num channels
                dram_num_channels += 1
                dram_util_total += util_percent

            # Gather cycle information
            if "globalcyclecount" in line:
                # Extract what we need from the line
                cycle_line = line.split()
                cycles = int(cycle_line[1])

                # Need to calculate the sampling period
                if prev_cycles == 0:
                    sampling_period = cycles

                # Check to see if it is the start of a new kernel
                # Do it before total_cycle increment to assume it
                # finished at the end of the last sample, not in
                # the middle of the new sample (a bit conservative)
                if prev_cycles != 0:
                    if prev_cycles >= cycles:
                        kernel_boundaries.append(total_cycle_count)

                prev_cycles = cycles

                # Increment the sampling period
                total_cycle_count += sampling_period

                # Add a new sample to our global time
                total_cycles.append(total_cycle_count)

            # Gather instruction information
            if "globalinsncount" in line:
                # Extract what we need from the line
                insn_line = line.split()
                current_instructions = int(insn_line[1])

                # Calculate the IPC using the difference in instructions executed
                ipc = (current_instructions - prev_instructions) / sampling_period
                ipc_values.append(ipc)

                # Save the instruction count for the next comparison
                prev_instructions = current_instructions

            # Gather L1 cache information
            if "l1d_read_hit_rate_total" in line:
                # Extract what we need from the line
                l1_read_line = line.split()
                if "nan" in l1_read_line[1]:
                    l1_read_hit_rate.append(0)
                else:
                    l1_read_hit_rate.append(float(l1_read_line[1]))


            if "l1d_write_hit_rate_total" in line:
                # Extract what we need from the line
                l1_write_line = line.split()
                if "nan" in l1_write_line[1]:
                    l1_write_hit_rate.append(0)
                else:
                    l1_write_hit_rate.append(float(l1_write_line[1]))


def main():
    # Unpack the directory path from the command line arguments
    script_name, dir_path = argv
    print(f"Collecing all AerialVision output files in director {dir_path}")

    # Empty dictionary
    # Indexed by a tuple of app name and input
    # Value is path to file
    # Populated by locate_logs() function
    gz_dict = {}
    locate_logs(dir_path, gz_dict)

    # Go through all the available .gz files
    for key, value in gz_dict.items():
        parse_log(key, value)

if __name__ == "__main__":
    main()
