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

from random_regular_graph import *

class JellyFishTop(Topo):
    def build(self):
        n_switches = 4
        n_hosts_per_switch = 2
        n_nbr_switches_per_switch = 2

        switches = [self.addSwitch('s%d' % x) for x in range(n_switches)]
        for i, switch in enumerate(switches):
            for x in range(n_hosts_per_switch):
                host = self.addHost('h%ds%d' % (x, i))
                self.addLink(host, switch)
                print "%s -> %s" % (host, switch)

        g = make_rrg(n_nbr_switches_per_switch, n_switches)

        for edge in g.Edges():
            src = 's%d' % edge.GetSrcNId()
            dst = 's%d' % edge.GetDstNId()
            self.addLink(src, dst)
            print "%s -> %s" % (src, dst)


def experiment(net):
    net.start()
    sleep(3)
    CLI(net)
    # net.pingAll()
    net.stop()

def main():
    topo = JellyFishTop()
    net = Mininet(topo=topo, host=CPULimitedHost, link = TCLink, controller=JELLYPOX)
    experiment(net)

if __name__ == "__main__":
    main()

