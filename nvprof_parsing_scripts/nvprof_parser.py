"""
This program is a parser for all NVprof CSV files that can be found in
a subdirectory passed as an argument when running this script

To run:
    python3 nvprof_parser.py path/to/directory

Output:
"""

import os
from sys import argv

def process_csv(csv):
    # Keep track of the application name
    application_name = csv.split("/")[-1].split(".")[0]

    # Read out all the lines in the CSV file
    lines = []
    with open(csv, 'r') as f:
        lines = f.readlines()

    fields = lines[3].split(",")
    units = lines[4].split(",")

    exec_time_index = fields.index("\"Duration\"")
    name_index = fields.index("\"Name\"")

    exec_time_units = units[exec_time_index]

    kernels = []
    exec_times = []
    for i in range(5, len(lines)):
        if "[" not in lines[i]:
            metrics = lines[i].split(",")
            kernels.append(metrics[name_index])
            exec_times.append(float(metrics[exec_time_index]))
        else:
            continue

    total_exec_time = sum(exec_times)

    with open(application_name + "_exec_time.csv", "w+") as f:
        for i in range(len(kernels)):
            f.write(kernels[i] + "," + str(exec_times[i] / total_exec_time) + "\n")

def main():
    # Unpack the command line arguments
    program,directory = argv

    # Walk the directory and find all CSV files
    csvs = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            if ".csv" in name:
                csvs.append(os.path.join(root, name))

    for csv in csvs:
        process_csv(csv)


if __name__ == "__main__":
    main()
