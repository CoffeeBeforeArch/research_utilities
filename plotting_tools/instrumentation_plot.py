# This program plots the the difference in basic block execution
# between threads from SASSI CFG instrumentation
# By: Nick from CoffeeBeforeArch

from sys import argv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os

# Parses the logs
# Returns thread_info list with tuples of TID and BBV
def parse_logs(log, warps, warp_info):
    with open(log, "r+") as l:
        lines = l.readlines()

    # Extract kernel name, thread ID and BBV from each line
    for i, line in enumerate(lines):
        # First line is the kernel name
        if i == 0:
            continue
        elif i == 1:
            continue
        elif i == 2:
            warps.append(int(line))
        # Remaining lines are BBVs
        else:
            warp_info.append(line)

def fmt(x, pos):
        a, b = '{:.2e}'.format(x).split('e')
        b = int(b)
        return r'${} \times 10^{{{}}}$'.format(a, b)

def heatmap(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            if ".txt" in name and "bb_" not in name:
                # Empty list that will be populated with thread BB distributions
                warp_info = []

                # Kernel name and warps
                warps = []

                # Parse the logs
                print(os.path.join(root,name))
                parse_logs(os.path.join(root,name), warps, warp_info)

                # Conver the lines into integers
                m_distances = warp_info[0].split()
                m_int_distances = map(int, m_distances)

                # Convert to numpy array
                n_array = np.array(list(m_int_distances)).reshape(warps[0], warps[0])

                # Set up the name
                name = name.split(".")[0]

                # Set up the mask, and plot the heatmap
                mask = np.tri(n_array.shape[0], k=-1)
                n_array = np.ma.array(n_array, mask=mask)
                fig = plt.figure()
                ax = fig.add_subplot(111)
                im = ax.imshow(n_array, cmap='hot', interpolation='nearest')
                ax.set_xlabel("TB i")
                ax.set_ylabel("TB j")
                ax.set_title("Manhattan Distance for: " + name)

                # Add the colorbar
                cbar = fig.colorbar(ax=ax, mappable=im, orientation='vertical', format=matplotlib.ticker.FuncFormatter(fmt))
                cbar.set_label("Distance between TBs")

                # Save the figure
                plt.savefig(name + ".png", dpi=500)
                plt.close()



def histogram(bbv_file):
    lines = []
    kid = 0
    with open(bbv_file, "r") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        # First two lines are number of warps and
        kernel_name = lines[i].split("(")[0]
        i += 1
        num_warps = int(lines[i])
        i += 1
        num_bbs = int(lines[i])
        i += 1

        # Extract the bbs for a kernel and split them into lists
        kernel_bbs = []
        for i in range(i, i + num_warps):
            kernel_bbs.append(lines[i])
            i += 1

        # Bin the basic blocks
        numpy_kernel = np.array(kernel_bbs)
        unique_elements, counts_elements = np.unique(numpy_kernel, return_counts=True)

        fig, ax = plt.subplots()
        ax.bar(np.arange(len(counts_elements)), counts_elements, align='center', alpha=0.5)
        ax.set_xlabel("BBV identifier")
        ax.set_ylabel("Number of warps with identical BBV")
        ax.set_title("BBV Distribution for: " + kernel_name)
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        minimum = 0
        maximum = max(counts_elements)
        ax.set_ylim([minimum,maximum])
        # Save the figure
        plt.savefig(kernel_name + "_" + str(kid) + ".png", dpi=200)
        plt.close()

        kid += 1

def main():
    # Get the directories where the logfiles are located
    script,directory = argv
    #histogram(directory)
    heatmap(directory)


if __name__ == "__main__":
    main()
