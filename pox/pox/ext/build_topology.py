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

from itertools import combinations
from random_regular_graph import *

from k_shortest_paths import *
from pprint import pprint
import random

TMP_DIR_PATH = "~/poxStartup/pox/pox/ext/tmp"

n_switches = 30
n_hosts_per_switch = 4
n_nbr_switches_per_switch = 6

k_short = True

class JellyFishTop(Topo):
    def build(self):
        linkopts = dict(bw=5, max_queue_size=1000) # bw in Mbits/sec
        self._switches = [self.addHost('s%d' % x) for x in range(n_switches)]
        for i, switch in enumerate(self._switches):
            for x in range(n_hosts_per_switch):
                host = self.addHost('h%ds%d' % (x, i))
                for x in range(8 if k_short else 1):
                    self.addLink(host, switch, **linkopts)
                print "%s <-> %s" % (host, switch)

        self._graph = make_rrg(n_nbr_switches_per_switch, n_switches)

        linkopts["bw"] *= n_hosts_per_switch
        for edge in self._graph.edges():
            src = 's%d' % edge[0]
            dst = 's%d' % edge[1]
            self.addLink(src, dst, **linkopts)
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

def make_kshost_addr(sidx, hidx, ifidx):
    return "10.%d.%d.%d/31" % (sidx, ifidx, 2 * hidx + 3)

def make_kshost_addr_no_subnet(sidx, hidx, ifidx):
    return "10.%d.%d.%d" % (sidx, ifidx, 2 * hidx + 3)

def run_load_test(net, topo):
    # get list of tuples of every randomly chosen pairs
    all_hosts = []
    for sidx in range(n_switches):
        for hidx in range(n_hosts_per_switch):
            all_hosts.append((hidx, sidx))

    all_pairs = []
    for host1_idx, host1 in enumerate(all_hosts):
        host2_idx = random.randint(0, len(all_hosts)-1)
        while host1_idx == host2_idx:
            host2_idx = random.randint(0, len(all_hosts)-1)
        host2 = all_hosts[host2_idx]
        all_pairs.append((host1, host2))

    current_port = 5001
    for src_hid, dst_hid in all_pairs:
        src, dst = net.get("h%ds%d" % src_hid, "h%ds%d" % dst_hid)
        src_hidx, src_switch = src_hid
        _, dst_switch = dst_hid
        num_paths = len(k_shortest_paths(topo._graph, src_switch, dst_switch, 8))
        for if_idx in range(num_paths):
            file_name_prefix = "%s-%s:%s" % (src.name, dst.name, current_port)
            src_iface_ip = make_kshost_addr_no_subnet(src_switch, src_hidx, if_idx)
            dst_cmd = "iperf -s -p %d -f k &> %s/%s &" % (current_port, TMP_DIR_PATH, "%s-server" % file_name_prefix)
            src_cmd = "sleep 1 && iperf -c %s -B %s -t 30 -p %d -f k &> %s/%s &" % (dst.IP(), src_iface_ip, current_port, TMP_DIR_PATH, "%s-client" % file_name_prefix)
            current_port += 1
            print src.name, src_cmd
            print dst.name, dst_cmd
            print "========="
            dst.sendCmd(dst_cmd)
            o(dst.waitOutput())
            src.sendCmd(src_cmd)
            o(src.waitOutput())


def experiment(net, topo):
    net.start()
    sleep(1)
    # smart_pingall(net, topo)
    run_load_test(net, topo)
    CLI(net)
    net.stop()

def ecmp_routing(net, topo):
    for i, sid in enumerate(topo._switches):
        switch = net.get(sid)
        for j, j_sid in enumerate(topo._switches):
            if j != i:
                print "%d <-> %d" % (i, j), ecmp(topo._graph, i, j, 8)
                all_next_hop_cmds = []
                for path in ecmp(topo._graph, i, j, 8):
                    nh_sid = 's%d' % path[1]
                    nh_switch = net.get(nh_sid)
                    nh_if, reverse = switch.connectionsTo(nh_switch)[0]
                    nh_ip = nh_switch.IP(reverse)
                    all_next_hop_cmds.append("nexthop via %s dev %s weight 1" % (nh_ip, nh_if))
                for x in range(n_hosts_per_switch):
                    hid = 'h%ds%d' % (x, j)
                    host_ip = net.get(hid).IP()
                    cmd = "ip route add %s/32 %s" % (host_ip, " ".join(all_next_hop_cmds))
                    # print cmd
                    switch.sendCmd(cmd)
                    o(switch.waitOutput())

def make_pretables(sidx, pair_to_paths):
    pt = {}
    for (src, dst), routes in pair_to_paths.iteritems():
        if dst != sidx:
            for rid, route in enumerate(routes):
                idx = None
                try:
                    idx = route.index(sidx)
                except:
                    pass
                if idx != None:
                    pt.setdefault((src, rid), []).append((dst, route[idx + 1]))
    return pt

def k_shortest_routing(net, topo):
    current_tid = 300
    k = 8
    ordered_pairs = list(combinations([x for x in range(n_switches)], 2))
    ordered_pairs += [(p[1], p[0]) for p in ordered_pairs]
    pair_to_paths = {key:k_shortest_paths(topo._graph, key[0], key[1], k) for key in ordered_pairs}
    created_tables = set()
    for i, sid in enumerate(topo._switches):
        pretables = make_pretables(i, pair_to_paths)
        switch = net.get(sid)
        for (src, rid), entries in pretables.iteritems():
            friendly_name = "t_%d_%d_%d" % (i, src, rid)
            if friendly_name not in created_tables:
                subprocess.call("echo '%d %s' | sudo tee --append /etc/iproute2/rt_tables > /dev/null" % (current_tid, friendly_name), shell=True)
                current_tid += 1
                switch.sendCmd("ip rule add from %s lookup %s" % ("10.%d.%d.0/24" % (src, rid), friendly_name))
                o(switch.waitOutput())
            for dst, nhidx in entries:
                nh = net.get('s%d' % nhidx)
                nh_iface_on_switch, switch_iface_on_nh = switch.connectionsTo(nh)[0]
                cmd = "ip route add %s table %s via %s dev %s" % ("10.%d.0.0/16" % dst, friendly_name, switch_iface_on_nh.IP(), nh_iface_on_switch.name)
                switch.sendCmd(cmd)
                o(switch.waitOutput())


def main():
    subprocess.call("sudo cp ~/rt_table_cpy /etc/iproute2/rt_tables", shell=True)
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
            if k_short:
                for if_index in range(8):
                    switch_iface_on_host, host_iface_on_switch = host.connectionsTo(switch)[if_index]
                    host_iface_on_switch.setIP("10.%d.%d.%d/31" % (i, if_index, 2 * x + 2))
                    switch_iface_on_host.setIP(make_kshost_addr(i, x, if_index))
                    host.setARP(switch.IP(host_iface_on_switch), switch.MAC(host_iface_on_switch))
                    switch.setARP(host.IP(switch_iface_on_host), host.MAC(switch_iface_on_host))
                for j in range(n_switches):
                    if i != j:
                        cmd = ["ip route add 10.%d.0.0/16" % j]
                        for path_index in range(len(k_shortest_paths(topo._graph, i, j, 8))):
                            switch_iface_on_host, host_iface_on_switch = host.connectionsTo(switch)[path_index]
                            cmd.append("nexthop via %s dev %s weight 1" % (host_iface_on_switch.IP(), switch_iface_on_host.name))
                        host.sendCmd(" ".join(cmd))
                        o(host.waitOutput())
                    else:
                        switch_iface_on_host, host_iface_on_switch = host.connectionsTo(switch)[0]
                        host.sendCmd("ip route add 10.%d.0.0/16 via %s dev %s" % (j, host_iface_on_switch.IP(), switch_iface_on_host.name))
                        o(host.waitOutput())

            else:
                switch_iface_on_host, host_iface_on_switch = host.connectionsTo(switch)[0]
                host_iface_on_switch.setIP("10.2.%d.%d/31" % (i, 2 * x + 2))
                switch_iface_on_host.setIP("10.2.%d.%d/31" % (i, 2 * x + 3))
                host.setARP(switch.IP(host_iface_on_switch), switch.MAC(host_iface_on_switch))
                switch.setARP(host.IP(switch_iface_on_host), host.MAC(switch_iface_on_host))
                host.sendCmd("route add -net 0.0.0.0 netmask 0.0.0.0 gw %s dev %s" % (host_iface_on_switch.IP(), switch_iface_on_host))
                o(host.waitOutput())
    print "host/switch links configured"

    if k_short:
        print "k shortests routing"
        k_shortest_routing(net, topo)
    else:
        print "ecmp routing"
        ecmp_routing(net, topo)
    print "switch routes configured"

    # debug
    if False:
        for i, sid in enumerate(topo._switches):
            switch = net.get(sid)
            for interface_name in switch.intfList():
                switch.sendCmd("tcpdump -i %s &> %s/%s.txt &" % (interface_name, TMP_DIR_PATH, interface_name))
                o(switch.waitOutput())

    experiment(net, topo)
if __name__ == "__main__":
    main()

