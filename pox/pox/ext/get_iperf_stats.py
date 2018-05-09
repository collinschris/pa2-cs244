from os import listdir
from os.path import isfile, join

TMP_DIR_PATH = "/home/ubuntu/poxStartup/pox/pox/ext/tmp"

def get_bandwidth_from_file(file_name):
    with open("%s/%s" % (TMP_DIR_PATH, file_name), "r") as f:
        return int(f.readlines()[-1].split(" ")[-2]) # last line, 2nd to last text element

def get_units(file_name):
    with open("%s/%s" % (TMP_DIR_PATH, file_name), "r") as f:
        return f.readlines()[-1].split(" ")[-1] # last line, last text element

def average(nums):
    return sum(nums) / len(nums)

all_files = [f for f in listdir(TMP_DIR_PATH) if isfile(join(TMP_DIR_PATH, f))]
all_bandwidths = []
for file_name in all_files:
    all_bandwidths.append(get_bandwidth_from_file(file_name))

print "Average:", average(all_bandwidths), get_units(all_files[0])
