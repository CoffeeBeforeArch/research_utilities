# This program plots the the difference in basic block execution
# between threads from SASSI CFG instrumentation
# By: Nick from CoffeeBeforeArch

from sys import argv
import numpy as np
import matplotlib.pyplot as plt

# Parses the logs
# Returns thread_info list with tuples of TID and BBV
def parse_logs(log, name, thread_info):
    with open(log, "r+") as l:
        lines = l.readlines()

    # Extract kernel name, thread ID and BBV from each line
    for i, line in enumerate(lines):
        # First line is the kernel name
        if i == 0:
            name = line
        elif i == 1:
            continue
        # Remaining lines are BBVs
        else:
            # Split the thread ID and BBV
            split_line = line.split(",")
            # Extract the TID
            tid = split_line[0]
            # Extract the BBV
            bbv = split_line[1:-1]

            # Append the results to the tuple list
            thread_info.append((tid, list(map(int, bbv))))

# Manhattan Distance calculations
def manhattan_distance(tuples, thread_distances):
    # BBV we are comparing to all others
    for i,bbv_tuple1 in enumerate(tuples):
        # List of distances for each thread
        d_list = []
        for j,bbv_tuple2 in enumerate(tuples):
            # Accumulate distances for 1 thread
            d = 0

            # Compare each basic block
            for k in range(len(bbv_tuple1[1])):
                d += abs(bbv_tuple1[1][k] - bbv_tuple2[1][k])

            # Append distance between two threads
            if i > j:
                d_list.append(10)
            else:
                d_list.append(d)

        # Append distances for 1 thread and all remaining threads
        thread_distances.append(d_list)

def main():
    # Get the specific logfile as an argument
    script,log = argv
    # Empty list that will be populated with thread BB distributions
    thread_info = []
    # Kernel name
    name = ""

    # Parse the logs
    parse_logs(log, name, thread_info)

    # List of manhattan distances
    m_distances = []

    # Pass in tuples, get list of lists with the distances between threads
    manhattan_distance(thread_info, m_distances)

    # Convert to numpy array
    n_array = np.array(m_distances)

    plt.imshow(n_array, cmap='hot', interpolation='nearest')
    plt.xlabel("Thread i")
    plt.ylabel("Thread i")
    plt.title("Basic Block Comparison for Vector Addition")
    plt.show()

if __name__ == "__main__":
    main()
