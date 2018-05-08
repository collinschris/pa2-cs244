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
import subprocess

from random_regular_graph import *

from k_shortest_paths import *

n_switches = 12
n_hosts_per_switch = 1
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


def o(output):
    if output != "":
        print output

def smart_pingall(net, topo):
    for i, sid in enumerate(topo._switches):
        for x in range(n_hosts_per_switch):
            hid = 'h%ds%d' % (x, i)
            host = net.get(hid)

            passed = True
            for j, j_sid in enumerate(topo._switches):
                for j_x in range(n_hosts_per_switch):
                    next_hid = 'h%ds%d' % (j_x, j)
                    next_host = net.get(next_hid)
                    if next_hid != hid:
                        host.sendCmd("ping -c 1 %s" % next_host.IP())
                        out = host.waitOutput()
                        if "1 packets transmitted, 1 received" not in out:
                            print out
                            print "%s could not ping %s" % (hid, next_hid)
                            path = k_shortest_paths(topo._graph, i, j, 1)[0]
                            print path
                            passed = False
            if passed:
                print "%s can reach all" % hid
    print "ping complete"

def experiment(net, topo):
    net.start()
    sleep(1)
    smart_pingall(net, topo)
    CLI(net)
    # net.pingAll()
    net.stop()


def main():
    subprocess.call("sudo sysctl -w net.ipv4.conf.default.rp_filter=0 net.ipv4.conf.all.rp_filter=0", shell=True)
    topo = JellyFishTop()
    print "topology built"

    net = Mininet(topo=topo, host=CPULimitedHost, link = TCLink, controller = JELLYPOX)
    print "network constructed"

    for i, sid in enumerate(topo._switches):
        switch = net.get(sid)
        switch.sendCmd("ip route flush table main")
        o(switch.waitOutput())
        switch.sendCmd("sysctl -w net.ipv4.ip_forward=1")
        switch.waitOutput()
    print "tables flushed and forwarding turned on"

    for i, edge in enumerate(topo._graph.edges()):
        src_sid, dst_sid = edge
        src = net.get('s%d' % src_sid)
        dst = net.get('s%d' % dst_sid)
        dst_iface_on_src, src_iface_on_dst = src.connectionsTo(dst)[0]
        dst_iface_on_src.setIP("11.%d.%d.4/24" % (src_sid, dst_sid))
        src_iface_on_dst.setIP("11.%d.%d.7/24" % (src_sid, dst_sid))
        src.setARP(dst.IP(src_iface_on_dst), dst.MAC(src_iface_on_dst))
        dst.setARP(src.IP(dst_iface_on_src), dst.MAC(dst_iface_on_src))
    print "switch/switch links configured"

    for i, sid in enumerate(topo._switches):
        switch = net.get(sid)
        for x in range(n_hosts_per_switch):
            hid = 'h%ds%d' % (x, i)
            host = net.get(hid)
            switch_iface_on_host, host_iface_on_switch = host.connectionsTo(switch)[0]
            host_iface_on_switch.setIP("10.2.%d.%d/31" % (i, 2 * x + 2))
            switch_iface_on_host.setIP("10.2.%d.%d/31" % (i, 2 * x + 3))
            host.setARP(switch.IP(host_iface_on_switch), switch.MAC(host_iface_on_switch))
            switch.setARP(host.IP(switch_iface_on_host), host.MAC(switch_iface_on_host))
            host.sendCmd("route add -net 0.0.0.0 netmask 0.0.0.0 gw %s dev %s" % (host_iface_on_switch.IP(), switch_iface_on_host))
            o(host.waitOutput())
    print "host/switch links configured"

    for i, sid in enumerate(topo._switches):
        switch = net.get(sid)
        for j, j_sid in enumerate(topo._switches):
            if j != i:
                path = k_shortest_paths(topo._graph, i, j, 1)[0]
                nh_sid = 's%d' % path[1]
                nh_switch = net.get(nh_sid)
                nh_if, reverse = switch.connectionsTo(nh_switch)[0]
                nh_ip = nh_switch.IP(reverse)
                for x in range(n_hosts_per_switch):
                    hid = 'h%ds%d' % (x, j)
                    host_ip = net.get(hid).IP()
                    switch.sendCmd("ip route add %s/32 via %s dev %s" % (host_ip, nh_ip, nh_if))
                    o(switch.waitOutput())
    print "switch routes configured"

    experiment(net, topo)
if __name__ == "__main__":
    main()

