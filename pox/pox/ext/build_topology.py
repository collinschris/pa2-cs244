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

n_switches = 1
n_hosts_per_switch = 5
n_nbr_switches_per_switch = 2

class JellyFishTop(Topo):
    def build(self):
        self._switches = [self.addSwitch('s%d' % x) for x in range(n_switches)]
        for i, switch in enumerate(self._switches):
            for x in range(n_hosts_per_switch):
                host = self.addHost('h%ds%d' % (x, i))
                self.addLink(host, switch)
                print "%s <-> %s" % (host, switch)

        self._graph = make_rrg(n_nbr_switches_per_switch, n_switches)

        for edge in self._graph.edges():
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

    net = Mininet(topo=topo, host=CPULimitedHost, link = TCLink)
    for i, sid in enumerate(topo._switches):
        switch = net.get(sid)
        for x in range(n_hosts_per_switch):
            hid = 'h%ds%d' % (x, i)
            host = net.get(hid)
            switch_iface_on_host, host_iface_on_switch = host.connectionsTo(switch)[0]
            #host.setARP(switch.IP(host_iface_on_switch), switch.MAC(host_iface_on_switch))
            #switch.setARP(host.IP(switch_iface_on_host), host.MAC(switch_iface_on_host))

    for edge in topo._graph.edges():
        src_sid = 's%d' % edge[0]
        dst_sid = 's%d' % edge[1]
    experiment(net)
if __name__ == "__main__":
    main()

