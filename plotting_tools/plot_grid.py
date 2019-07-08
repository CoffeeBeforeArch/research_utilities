# This python script is used for plotting clustererd grids
# By: Nick from CoffeeBeforeArch

from sys import argv
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

def fmt(x, pos):
        a, b = '{:.2e}'.format(x).split('e')
        b = int(b)
        return r'${} \times 10^{{{}}}$'.format(a, b)


def print_grid(log_file, dimx, dimy, info):
    app = info[0]
    kernel = info[1]
    number = info[2]
    clusters = info[4]

    lines = []
    with open(log_file, "r") as f:
        lines = f.readlines()

    basic_blocks = [int(X) for X in lines[0].split()]
    numpy_blocks = np.array(basic_blocks).reshape(dimx, dimy)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    im = ax.imshow(numpy_blocks, cmap='hot', interpolation='nearest')
    ax.set_xlabel("TB i")
    ax.set_ylabel("TB j")
    ax.set_title(app + "-" + kernel + "-" + number + "- Num. Cluster-" + clusters)

    # Add the colorbar
    cbar = fig.colorbar(ax=ax, mappable=im, orientation='vertical', format=matplotlib.ticker.FuncFormatter(fmt))
    cbar.set_label("Cluster ID")

    # Save the figure
    plt.savefig("_".join(info) + ".png", dpi=500)
    plt.close()



def main():
    script,base_dir = argv
    for root, dirs, files in os.walk(base_dir):
        for name in files:
            if("Fan2" in name):
                split_name = name.split(".")[0].split("_")
                print_grid(root + "/" + name, 52, 52, split_name)


if __name__ == "__main__":
    main()
