# This Python script is for clustering basic block vector data
# By: Nick from CoffeeBeforeArch

from sys import argv
import os
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster import hierarchy
import matplotlib.pyplot as plt

def cluster(log_file):
    app_name = log_file.split("/")[-2]
    print(app_name)
    # Dictionary to keep track of unique control flow paths
    unique_kernels = {}

    # Read in all the lines first
    lines = []
    kid = 0
    with open(log_file, "r") as f:
        lines = f.readlines()

    # Go over all the lines using a while loop
    i = 0
    while i < len(lines):
        # First two lines are number of warps and
        kernel_name = lines[i].split("(")[0]
        i += 1
        num_tbs = int(lines[i])
        i += 1
        num_bbs = int(lines[i])
        i += 1
        # Extract the bbs for a kernel and split them into lists
        kernel_bbs = []
        for k in range(i, i + num_tbs):
            kernel_bbs.append([int(x) for x in lines[k].rstrip().split()])
            i += 1

        X = np.array(kernel_bbs)
        for k in range(1, 21):
            if k >= num_tbs:
                break
            clustering = AgglomerativeClustering(n_clusters=k).fit(X)
            with open(app_name + "_" + kernel_name + "_" + str(kid) +"_clustering_" + str(k) + ".txt", "a+") as f:
                for j in clustering.labels_:
                    f.write(str(j) + " ")
                f.write("\n")

        kid += 1


def main():
    script,base_dir = argv
    for root, dirs, files in os.walk(base_dir):
        for name in files:
            if("bb_log" in name):
                cluster(root + "/" + name)


if __name__ == "__main__":
    main()
