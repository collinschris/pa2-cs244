from os import listdir
from os.path import isfile, join

TMP_DIR_PATH = "/home/ubuntu/poxStartup/pox/pox/ext/tmp"

def get_bandwidth_from_file(file_name):
    with open("%s/%s" % (TMP_DIR_PATH, file_name), "r") as f:
        return float(f.readlines()[-1].split(" ")[-2]) # last line, 2nd to last text element

def get_units(file_name):
    with open("%s/%s" % (TMP_DIR_PATH, file_name), "r") as f:
        return f.readlines()[-1].split(" ")[-1] # last line, last text element

def average(nums):
    return sum(nums) / len(nums)

server_files = [f for f in listdir(TMP_DIR_PATH) if "server" in f and isfile(join(TMP_DIR_PATH, f))]
all_bandwidths = {}
for file_name in server_files:
    try:
        key = file_name.split(":")[0]
        if key in all_bandwidths:
            all_bandwidths[key] += get_bandwidth_from_file(file_name)
        else:
            all_bandwidths[key] = 0
    except Exception as e:
        print e


print "Average:", average(all_bandwidths.values()), get_units(server_files[0])
