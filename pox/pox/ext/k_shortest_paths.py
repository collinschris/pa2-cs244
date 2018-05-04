from random_regular_graph import *
from itertools import islice
import networkx as nx

def k_shortest_paths(graph, source, target, k, weight=None):
    return list(islice(nx.shortest_simple_paths(graph, source, target, weight=weight), k))

n_switches = 6
n_nbr_switches_per_switch = 3
g = make_rrg(n_nbr_switches_per_switch, n_switches)
print g.nodes()
print g.edges()
print k_shortest_paths(g, 0, 4, 10)
