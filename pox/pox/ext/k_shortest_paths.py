from random_regular_graph import *
from itertools import islice
import networkx as nx

def k_shortest_paths(graph, source, target, k, weight=None):
    return list(islice(nx.shortest_simple_paths(graph, source, target, weight=weight), k))

def ecmp(graph, source, target, k, weight=None):
    shortest_paths = k_shortest_paths(graph, source, target, k, weight)
    shortest_paths = sorted(shortest_paths, key=lambda path: len(path))
    shortest_path_len = len(shortest_paths[0])
    return [path for path in shortest_paths if len(path) == shortest_path_len]
