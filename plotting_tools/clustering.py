# This Python script is for clustering basic block vector data
# By: Nick from CoffeeBeforeArch

from sys import argv
import os
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score
import warnings

def cluster(log_file):
    directory = "/".join(log_file.split("/")[:-1])
    app_name = log_file.split("/")[-2]
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
        # Get kernel name
        kernel_name = lines[i].split("(")[0]
        i += 1

        # Get grid x and y dim and calculate total TBs
        dx = int(lines[i])
        i += 1
        dy = int(lines[i])
        i += 1
        num_tbs = dx * dy

        # Get the number of basic blocks
        num_bbs = int(lines[i])
        i += 1

        # Extract the bbs for a kernel and split them into lists
        kernel_bbs = []
        kernel_insns = []

        end = i + num_tbs * 2 - 1
        while i < end:
            kernel_insns.append([int(lines[i])])
            i += 1
            kernel_bbs.append([float(x) for x in lines[i].rstrip().split()])
            i += 1

        X = np.array(kernel_bbs)
        Y = np.array(kernel_insns)
        s_scores = []
        clusters = []

        for k in range(2, 51):
            # We don't need more clusters than basic blocks
            if k > num_tbs:
                break

            # Cluster based on KMeans
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                clustering = KMeans(n_clusters=k).fit_predict(Y)
                if(len(w)):
                    break

            # Calculate silhouette score for bot
            s_avg = silhouette_score(X, clustering)

            # Track the cluster
            clusters.append(k)

            # Track the score
            s_scores.append(s_avg)

            # Write the scores
            with open(directory + "/" + kernel_name + "_" + str(kid) +"_clustering_scores" + ".txt", "a+") as f:
                f.write(str(k) + "," + str(s_avg) + "\n")


        if len(s_scores) != 0:
            max_index = s_scores.index(max(s_scores))
            k = clusters[max_index]

            clustering = AgglomerativeClustering(n_clusters=k).fit_predict(X)
            with open(directory + "/" + kernel_name + "_" + str(kid) +"_clustering_" + str(k) + "_labels" + ".txt", "a+") as f:
                f.write(kernel_name+"\n")
                f.write(str(dx)+"\n")
                f.write(str(dy)+"\n")
                for j in clustering:
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
