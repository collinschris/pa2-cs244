from random_regular_graph import *
import snap

def get_all_paths_to_root(bfs_tree, root, start):
    if (root == start):
        return [[root]]
    ni = bfs_tree.GetNI(start)
    all_paths = []
    for x in range(ni.GetInDeg()):
        anc = ni.GetInNId(x)
        paths = get_all_paths_to_root(bfs_tree, root, anc)
        for path in paths:
            all_paths.append(path + [start])
    return all_paths

def k_shortest_paths(graph, k, nid):
    bfs_tree = snap.GetBfsTree(g, nid, True, False)
    n = graph.GetNodes()
    d = {}
    for other in range(n):
        if other != nid:
            all_paths_to_root = get_all_paths_to_root(bfs_tree, nid, other)
            tupled = [(len(x), x) for x in all_paths_to_root]
            d[other] = [path for length, path in sorted(tupled)[:k]]
    return d


n_switches = 4
n_nbr_switches_per_switch = 2
g = make_rrg(n_nbr_switches_per_switch, n_switches)
g.Dump()
print k_shortest_paths(g, 2, 1)

