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
from jelly_controller import init_topo

class JellyFishTop(Topo):
    def build(self):
        n_switches = 4
        n_hosts_per_switch = 1
        n_nbr_switches_per_switch = 3

        switches = [self.addSwitch('s%d' % x) for x in range(n_switches)]
        for i, switch in enumerate(switches):
            # print "switch mac: %s" % str(switch.MAC())
            for x in range(n_hosts_per_switch):
                host = self.addHost('h%ds%d' % (x, i))
                # print "host mac: %s" % str(host.MAC())
                self.addLink(host, switch)
                print "%s <-> %s" % (host, switch)

        g = make_rrg(n_nbr_switches_per_switch, n_switches)

        for edge in g.edges():
            src = 's%d' % edge[0]
            dst = 's%d' % edge[1]
            self.addLink(src, dst)
            print "%s <-> %s" % (src, dst)

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

