# This Python script is for clustering basic block vector data
# By: Nick from CoffeeBeforeArch

from sys import argv
import os
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score
import warnings
import statistics as st

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

    kmeans_sse = {}
    kmeans_max_clusters = {}
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

        Y = np.array(kernel_insns)
        s_scores = []
        clusters = []
        sse_list = []
        k_list = []
        with open(directory + "/" + app_name + "_sse.txt", "a+") as f:
            f.write(kernel_name.rstrip() + "_" + str(kid) +"_" + str(num_tbs) +"\n")

        k = 0
        while True:
            with warnings.catch_warnings(record=True) as w:
                k += 1

                # We don't need more clusters than basic blocks
                if k > num_tbs:
                    break

                # Cluster based on KMeans
                warnings.simplefilter("always")
                km = KMeans(n_clusters=k)
                clustering = km.fit_predict(Y)
                if(len(w)):
                    break

                sse = km.inertia_
                sse_list.append(sse)
                k_list.append(k)
                with open(directory + "/" + app_name + "_sse.txt", "a+") as f:
                    f.write(str(k) + "," + str(sse) + "\n")

        if kernel_name not in kmeans_sse:
            kmeans_sse[kernel_name] = []
            kmeans_max_clusters[kernel_name] = []

        kmeans_sse[kernel_name].append(sse_list[-1])
        kmeans_max_clusters[kernel_name].append(k_list[-1])
        kid += 1

    with open(directory + "/" + app_name + "_stats.txt", "a+") as f:
        f.write("Kernel SSE,mean,stdev\n")
        for k,v in kmeans_sse.items():
            f.write(k.rstrip())
            f.write("," + str(st.mean(v)) + ",")
            if(len(v) > 1):
                f.write(str(st.stdev(v)))
            f.write("\n")

        f.write("N clusters,mean,stdev\n")
        for k,v in kmeans_max_clusters.items():
            f.write(k.rstrip())
            f.write("," + str(st.mean(v)) + ",")
            if(len(v) > 1):
                f.write(str(st.stdev(v)))
            f.write("\n")

def main():
    script,base_dir = argv
    for root, dirs, files in os.walk(base_dir):
        for name in files:
            if("bb_log" in name):
                cluster(root + "/" + name)


if __name__ == "__main__":
    main()
