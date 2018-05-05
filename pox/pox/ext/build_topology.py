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

from k_shortest_paths import *

n_switches = 6
n_hosts_per_switch = 2
n_nbr_switches_per_switch = 3

class JellyFishTop(Topo):
    def build(self):
        self._switches = [self.addHost('s%d' % x) for x in range(n_switches)]
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

    net = Mininet(topo=topo, host=CPULimitedHost, link = TCLink, controller = JELLYPOX)
    for i, sid in enumerate(topo._switches):
        switch = net.get(sid)
        switch.sendCmd("ip route flush table main")
        print switch.waitOutput()

    for i, edge in enumerate(topo._graph.edges()):
        src_sid = edge[0]
        dst_sid = edge[1]
        src = net.get('s%d' % src_sid)
        dst = net.get('s%d' % dst_sid)
        dst_iface_on_src, src_iface_on_dst = src.connectionsTo(dst)[0]
        dst_iface_on_src.setIP("10.1.%d.4/24" % i)
        src_iface_on_dst.setIP("10.1.%d.7/24" % i)
        src.setARP(dst.IP(src_iface_on_dst), dst.MAC(src_iface_on_dst))
        dst.setARP(src.IP(dst_iface_on_src), dst.MAC(dst_iface_on_src))

    for i, sid in enumerate(topo._switches):
        switch = net.get(sid)
        for x in range(n_hosts_per_switch):
            hid = 'h%ds%d' % (x, i)
            host = net.get(hid)
            switch_iface_on_host, host_iface_on_switch = host.connectionsTo(switch)[0]
            host_iface_on_switch.setIP("10.2.%d.1/24" % i)
            switch_iface_on_host.setIP("10.2.%d.%d/24" % (i, x + 2))
            host.setARP(switch.IP(host_iface_on_switch), switch.MAC(host_iface_on_switch))
            switch.setARP(host.IP(switch_iface_on_host), host.MAC(switch_iface_on_host))
            switch.sendCmd("route add -host %s dev %s" % (host.IP(), host_iface_on_switch))
            print switch.waitOutput()
            host.sendCmd("route add -net 10.0.0.0 netmask 255.0.0.0 gw %s dev %s" % (host_iface_on_switch.IP(), switch_iface_on_host))
            print switch.waitOutput()
    for i, sid in enumerate(topo._switches):
        switch = net.get(sid)
        for j, j_sid in enumerate(topo._switches):
            if j != i:
                path = k_shortest_paths(topo._graph, i, j, 1)[0]
                print path
                nh_sid = 's%d' % path[1]
                nh_switch = net.get(nh_sid)
                nh_if, reverse = switch.connectionsTo(nh_switch)[0]
                print "%s <=> %s, %s <=> %s" % (sid, nh_sid, nh_if.IP(), reverse.IP())
                for intf in nh_switch.intfList():
                    print intf.IP()
                nh_ip = nh_switch.IP(reverse)
                for x in range(n_hosts_per_switch):
                    hid = 'h%ds%d' % (x, j)
                    host_ip = net.get(hid).IP()
                    cmd = "route add -host %s gw %s dev %s" % (host_ip, nh_ip, nh_if)
                    print cmd
                    switch.sendCmd(cmd)
                    print switch.waitOutput()
    experiment(net)
if __name__ == "__main__":
    main()

