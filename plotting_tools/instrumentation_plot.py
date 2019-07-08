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
    """
    exec_time_dict = {}
    app_name = ""
    for root, dirs, files in os.walk(exec_time_dir):
        for name in files:
            if(".csv" in name):
                app_name = name.split("_")[0]
                lines = []
                with open (root + name, "r") as f:
                    lines = f.readlines()

                exec_time_dict[app_name] = lines
    """

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

                # Get the application's name in order to look up exec time
                app_name = root.split("/")[-2]
                #line_no  =  int(name.split(".")[0].split("_")[-1])
                #exec_lines = exec_time_dict[app_name]

                # Set up the mask, and plot the heatmap
                mask = np.tri(n_array.shape[0], k=-1)
                n_array = np.ma.array(n_array, mask=mask)
                fig = plt.figure()
                #fig.suptitle("Exec % = " + str(float(exec_lines[line_no].split(",")[1]) * 100))
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

def main():
    # Get the directories where the logfiles are located
    script,log_dir = argv
    heatmap(log_dir)


if __name__ == "__main__":
    main()
