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

def ecmp(graph, ways, nid):
    bfs_tree = snap.GetBfsTree(g, nid, True, False)
    n = graph.GetNodes()
    d = {}
    for other in range(n):
        if other != nid:
            all_paths_to_root = get_all_paths_to_root(bfs_tree, nid, other)
            tupled = [(len(x), x) for x in all_paths_to_root]
            srted = sorted(tupled)
            shortest_len, shortest_path = srted[0]
            d[other] = [path for length, path in srted[:ways] if length == shortest_len]
    return d


n_switches = 12
n_nbr_switches_per_switch = 4
g = make_rrg(n_nbr_switches_per_switch, n_switches)
g.Dump()
labels = snap.TIntStrH()
for NI in g.Nodes():
    labels[NI.GetId()] = str(NI.GetId())
snap.DrawGViz(g, snap.gvlDot, "output.gif", " ", labels)
print ecmp(g, 2, 1)

