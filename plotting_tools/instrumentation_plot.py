# This program plots the the difference in basic block execution
# between threads from SASSI CFG instrumentation
# By: Nick from CoffeeBeforeArch

from sys import argv
import numpy as np
import matplotlib.pyplot as plt

# Parses the logs
# Returns thread_info list with tuples of TID and BBV
def parse_logs(log, name, warps, warp_info):
    with open(log, "r+") as l:
        lines = l.readlines()

    # Extract kernel name, thread ID and BBV from each line
    for i, line in enumerate(lines):
        # First line is the kernel name
        if i == 0:
            name.append(line)
        elif i == 1:
            continue
        elif i == 2:
            warps.append(int(line))
        # Remaining lines are BBVs
        else:
            warp_info.append(map(int,line.split()))

def main():
    # Get the specific logfile as an argument
    script,log = argv

    # Empty list that will be populated with thread BB distributions
    warp_info = []

    # Kernel name and warps
    name = []
    warps = []

    # Parse the logs
    parse_logs(log, name, warps, warp_info)

    # Convert to numpy array
    n_array = np.array(warp_info[0]).reshape(warps[0], warps[0])

    plt.plot(n_array, cmap='hot', interpolation='nearest')
    plt.xlabel("Warp i")
    plt.ylabel("Warp j")
    plt.title("Basic Block Comparison for kernel_name[0]")
    plt.savefig("test.png")

if __name__ == "__main__":
    main()
