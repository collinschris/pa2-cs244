#!/bin/bash
rm -rf tmp/
mkdir tmp
sudo mn -c
sudo python build_topology.py $@
python get_iperf_stats.py
