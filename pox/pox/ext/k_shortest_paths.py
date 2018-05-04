from random_regular_graph import *
import snap
from view_graph import view

def path_to_root_contains(bfs_tree, start_bfs_nid, new_nid, d):
    cur_ni = bfs_tree.GetNI(start_bfs_nid)
    while cur_ni.GetInDeg() != 0:
        anc_id = cur_ni.GetInNId(0)
        if d[anc_id] == new_nid:
            return True
        cur_ni = bfs_tree.GetNI(anc_id)
    return False


def create_bfs_tree(graph, nid):
    bfs_tree = snap.TNGraph.New()
    new_id = bfs_tree.AddNode(-1)
    queue = [new_id]
    d = {new_id: nid}

    while queue:
        cur_bfs_nid = queue.pop(0)
        orig_ni = graph.GetNI(d[cur_bfs_nid])

        for x in range(orig_ni.GetInDeg()):
            neighbor_nid = orig_ni.GetInNId(x)
            if not path_to_root_contains(bfs_tree, cur_bfs_nid, neighbor_nid, d):
                new_id = bfs_tree.AddNode(-1)
                bfs_tree.AddEdge(cur_bfs_nid, new_id)
                queue.append(new_id)
                d[new_id] = neighbor_nid

    return bfs_tree

n_switches = 6
n_nbr_switches_per_switch = 3
g = make_rrg(n_nbr_switches_per_switch, n_switches)
bfs_tree = create_bfs_tree(g, 1)
