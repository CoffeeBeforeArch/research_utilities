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
            warp_info.append(line)

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

    m_distances = warp_info[0].split()
    m_int_distances = map(int, m_distances)

    # Convert to numpy array
    n_array = np.array(list(m_int_distances)).reshape(warps[0], warps[0])

    name = log.split(".")[0]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    im = ax.imshow(n_array, cmap='hot', interpolation='nearest')
    ax.set_xlabel("Warp i")
    ax.set_ylabel("Warp j")
    ax.set_title("Basic Block Comparison for kernel_name[0]")

    cbar = fig.colorbar(ax=ax, mappable=im, orientation='horizontal')

    plt.show()

if __name__ == "__main__":
    main()
