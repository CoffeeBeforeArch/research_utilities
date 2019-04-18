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

# Opens a GPGPU-Sim visualizer file, reads it in, then parses the data
# Takes a tuple of app-name and input, and path to the file as inputs
def parse_log(app_tuple, gz_path):
    # Unpack the app name and input
    app_name, app_input = app_tuple

    # Read in the .gz logfile one line at a time
    with gzip.open(gz_path, "rt") as f:
        for line in f:
            continue

    print(lines[0])

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
