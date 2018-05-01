import random
import pdb
random.seed(42)

class Switch(object):
    def __init__(self, num_switches, k_ports, r_ToR_links, idx):
        self.idx = idx
        self.links = []
        self.non_neighbors = [i for i in range(0, num_switches)]
        self.non_neighbors.remove(self.idx)
        self.k_ports = k_ports
        self.r_ToR_links = r_ToR_links

    def has_more_ToR_ports(self):
        return self.r_ToR_links - len(self.links) > 0

def create_random_switch_pair(switches, remaining_switch_idxes):
    switch1_idx = random.randint(0, len(remaining_switch_idxes)-1)
    num_non_neighbors = len(switches[switch1_idx].non_neighbors)
    # get idx and remove from non-neighbors set
    switch2_idx = None
    switch2_idx = switches[switch1_idx].non_neighbors.pop(
                                                      random.randint(0, num_non_neighbors-1)
                                                     )
    print switch2_idx, switches[switch2_idx].non_neighbors, switch1_idx
    print switches[switch2_idx].links
    try:
        switches[switch2_idx].non_neighbors.remove(switch1_idx)
    except:
        pdb.set_trace()

    # add link in both directions
    switches[switch1_idx].links.append(switch2_idx)
    switches[switch2_idx].links.append(switch1_idx)

    return switch1_idx, switch2_idx

def remove_from_non_neighbors(idx, switches):
    if idx == 16:
        pdb.set_trace()
    for switch in switches:
        try:
            switch.non_neighbors.remove(idx)
        except:
            pass

# dict = mapping of ToR links
# set = remaining unpaired ToR switches
def rrg(N, k, r):
    switches = [Switch(N, k, r, i) for i in range(N)]
    remaining_switch_idxes = [i for i in range(N)]

    while len(remaining_switch_idxes) > 0:
        s1_idx, s2_idx = create_random_switch_pair(switches, remaining_switch_idxes)
        # check if s1 or s2 should be removed from remaining_switch_idxes
        print s1_idx, s2_idx
        # print remaining_switch_idxes
        if len(switches[s1_idx].non_neighbors) == 0 or not switches[s1_idx].has_more_ToR_ports():
            # print "idx:", s1_idx, "remaining ports?", switches[s1_idx].has_more_ToR_ports(), "non-neighbors?", len(switches[s1_idx].non_neighbors)
            remaining_switch_idxes.remove(s1_idx)
            remove_from_non_neighbors(s1_idx, switches)
        if len(switches[s2_idx].non_neighbors) == 0 or not switches[s2_idx].has_more_ToR_ports():
            # print "idx:", s2_idx, "remaining ports?", switches[s2_idx].has_more_ToR_ports(), "non-neighbors?", len(switches[s2_idx].non_neighbors)
            remaining_switch_idxes.remove(s2_idx)
            remove_from_non_neighbors(s2_idx, switches)


rrg(20, 10, 5)
