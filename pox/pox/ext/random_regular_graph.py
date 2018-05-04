import numpy as np
import networkx as nx

def permute(graph, stub_list):
    permuted = np.random.permutation(stub_list)
    for i in range(0, len(stub_list), 2):
        if (permuted[i] == permuted[i+1]):
            # no self edges
            return False
        success = graph.add_edge(permuted[i], permuted[i+1])
        if success == -2:
            return False
    return True

def make_rrg(c_degree, num):
    np.random.seed(16)
    stub_list = []
    for node_id in range(num):
        for i in range(c_degree):
            stub_list.append(node_id)

    while True:
        graph = nx.Graph()
        for x in range(num):
            graph.add_node(x)
        success = permute(graph, stub_list)
        if (success):
            return graph
