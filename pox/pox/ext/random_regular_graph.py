import numpy as np
import snap

def permute(graph, stub_list):
    permuted = np.random.permutation(stub_list)
    for i in range(0, len(stub_list), 2):
        if (permuted[i] == permuted[i+1]):
            # no self edges
            return False
        success = graph.AddEdge(permuted[i], permuted[i+1])
        if success == -2:
            return False
    return True

def make_rrg(c_degree, num):
    stub_list = []
    for node_id in range(num):
        for i in range(c_degree):
            stub_list.append(node_id)

    while True:
        graph = snap.TUNGraph.New()
        for x in range(num):
            graph.AddNode(x)
        success = permute(graph, stub_list)
        if (success):
            return graph
