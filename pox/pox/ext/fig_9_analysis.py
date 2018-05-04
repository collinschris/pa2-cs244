from k_shortest_paths import *
from random_regular_graph import *
from itertools import combinations
import matplotlib.pyplot as plt

def count_paths_for_all_links(graph, paths):
    # add both directions of link
    path_counts = {key:0 for key in graph.edges()}
    for key in graph.edges():
        path_counts[(key[1], key[0])] = 0

    for path in paths:
        for i in range(len(path)-1):
            path_counts[(path[i], path[i+1])] += 1

    return path_counts

def find_all_k_shorest_paths(graph, k):
    # create all unordered pairs in graph
    all_pairs = combinations(graph.nodes(), 2)
    # find k shorest paths for all
    paths = []
    for pair in all_pairs:
        paths += k_shortest_paths(graph, pair[0], pair[1], k)
    return paths

def find_all_ecmp_paths(graph, k):
    # create all unordered pairs in graph
    all_pairs = combinations(graph.nodes(), 2)
    # find k shorest paths for all
    paths = []
    for pair in all_pairs:
        paths += ecmp(graph, pair[0], pair[1], k)
    return paths

# init graph
n_switches = 60
n_nbr_switches_per_switch = 8
g = make_rrg(n_nbr_switches_per_switch, n_switches)

# k shortest paths
all_k_shortest_paths = find_all_k_shorest_paths(g, 8)
k_shortest_path_counts = count_paths_for_all_links(g, all_k_shortest_paths)
sorted_k_shortest_path_counts = sorted(k_shortest_path_counts.values())

# 8 way ecmp paths
all_ecmp_8_paths = find_all_ecmp_paths(g, 8)
ecmp_8_path_counts = count_paths_for_all_links(g, all_ecmp_8_paths)
sorted_ecmp_8_path_counts = sorted(ecmp_8_path_counts.values())

# 64 way ecmp paths
all_ecmp_64_paths = find_all_ecmp_paths(g, 64)
ecmp_64_path_counts = count_paths_for_all_links(g, all_ecmp_64_paths)
sorted_ecmp_64_path_counts = sorted(ecmp_64_path_counts.values())

# plot results
max_range = max(len(sorted_ecmp_8_path_counts), len(sorted_k_shortest_path_counts), len(sorted_ecmp_64_path_counts))
y_axis = [x for x in range(max_range)]
plt.plot(y_axis, sorted_ecmp_8_path_counts)
plt.plot(y_axis, sorted_ecmp_64_path_counts)
plt.plot(y_axis, sorted_k_shortest_path_counts)
plt.legend(["8-way ECMP", "64-way ECMP", "8 Shortest Paths", ], loc="upper left")
plt.show()



