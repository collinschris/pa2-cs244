Reproduce Figure 9:
```
python fig_9_analysis.py
```

Reproduce Table 1:
To reproduce table 1, you must have access to a linux machine (we used Ubuntu Server 16.04 LTS (HVM)) with sufficient computing capacity (at least 8 CPUs). Install mininet (v 2.3.0d1). Then make a copy of the operating system's default routing table:
```
cp /etc/iproute2/rt_tables ~/rt_table_cpy
```
You only need to do this once. The script will be making changes to `/etc/iproute2/rt_tables` and needs to reset the default rules before each run.

Then you can run the following commands to reproduce each of the 4 routing protocols tested:
```
sudo ./table1.sh --route-proto 8-shortest-1-flow
sudo ./table1.sh --route-proto 8-shortest-8-flow
sudo ./table1.sh --route-proto ecmp-1-flow
sudo ./table1.sh --route-proto ecmp-8-flow
```

To limit console output, you can optionally add `-q` flag.
