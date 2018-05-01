import os
import sys
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.node import OVSController
from mininet.node import Controller
from mininet.node import RemoteController
from mininet.cli import CLI
sys.path.append("../../")
from pox.ext.jelly_pox import JELLYPOX
from subprocess import Popen
from time import sleep, time
import numpy as np

def permute(adj_set, stub_list):
    permuted = np.random.permutation(stub_list)
    for i in range(0, len(stub_list), 2):
        if (permuted[i] == permuted[i+1]):
            # no self edges
            return False
        s = sorted([permuted[i], permuted[i+1]])
        tup = (s[0], s[1])
        if tup in adj_set:
            return False
        adj_set.add(tup)
    return True

def make_rrg_al(c_degree, num):
    stub_list = []
    for node_id in range(num):
        for i in range(c_degree):
            stub_list.append(node_id)

    while True:
        adj_list = set()
        success = permute(adj_list, stub_list)
        if (success):
            return adj_list

class JellyFishTop(Topo):
    def build(self):
        n_switches = 8
        n_hosts_per_switch = 1
        n_nbr_switches_per_switch = 3

        switches = [self.addSwitch('s%d' % x) for x in range(n_switches)]
        for i, switch in enumerate(switches):
            for x in range(n_hosts_per_switch):
                host = self.addHost('h%d-%d' % (i, x))
                self.addLink(host, switch)

        adj_list = make_rrg_al(n_nbr_switches_per_switch, n_switches)
        print adj_list

        for left, right in adj_list:
            self.addLink(switches[left], switches[right])


def experiment(net):
    net.start()
    sleep(3)
    net.pingAll()
    net.stop()

def main():
    topo = JellyFishTop()
    net = Mininet(topo=topo, host=CPULimitedHost, link = TCLink, controller=JELLYPOX)
    experiment(net)

if __name__ == "__main__":
    main()

