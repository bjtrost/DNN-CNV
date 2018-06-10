#!/usr/bin/env python3

import argparse
import BTlib
import re
import os.path

tools_to_check = ["CNVnator", "ERDS"]

def debug_write(debug_file, s):
	if debug_file:
		debug_file.write(s)

def generate_header(args):
	header_items = ["Instance name", "In benchmark"]

	if not args.no_setA_features:
		header_items = header_items + ["[A] CNV type", "[A] CNV size"]

	if not args.no_setB_features:
		header_items = header_items + ["[B] Predicted by " + tool for tool in tools_to_check]

	if args.depth_filename:
		header_items = header_items + ["[C] Read depth ratio", "[C] CNV standard deviation", "[C] Flanking region standard deviation"]

	if args.repeat_filename:
		header_items = header_items + BTlib.get_repeat_header(args.repeat_filename, args.num_segments)

	return("\t".join(header_items) + "\n")

def generate_in_benchmark_feature(line):
	fields = line.split("\t")
	if len(fields) < 9:
		return("-1")
	elif fields[8] == "NotApplicable":
		return("0")
	else:
		return("1")

def generate_instance_name(line, CNV_filename):
	instance_name = "***".join(line.rstrip().split("\t"))
	return(instance_name)

def generate_setA_features(line):

	setA_features = []

	if line.split("\t")[4] == "DEL": # Deletion or duplication
		setA_features.append("0")
	else:
		setA_features.append("1")

	size_MB = "{:.3f}".format(int(line.split("\t")[3]) / 1e6)

	setA_features.append(size_MB) # Size of CNV

	return(setA_features)

def generate_setB_features(line):
	setB_features = []
	for tool in tools_to_check:
		if tool in line:
			setB_features.append("1")
		else:
			setB_features.append("0")
	return(setB_features)

def generate_setC_features(line, args):
	fields = line.split("\t")
	CNV_chr, CNV_start, CNV_end = line.split("\t")[0:3]
	CNV_start = int(CNV_start)
	CNV_end = int(CNV_end)

	left_flank_depths, CNV_depths, right_flank_depths = BTlib.get_depth_lists(CNV_chr, CNV_start, CNV_end, args.depth_filename)

	if left_flank_depths is None:
		return(["-1", "-1", "-1"])

	both_flanks_depths = left_flank_depths + right_flank_depths

	CNV_mean = BTlib.mean(CNV_depths)
	flanks_mean = BTlib.mean(both_flanks_depths)

	RD_ratio = "{:.3f}".format(CNV_mean / flanks_mean)
	CNV_stdev = "{:.3f}".format(BTlib.stdev(CNV_depths))
	flanks_stdev = "{:.3f}".format(BTlib.stdev(both_flanks_depths))

	setC_features = [RD_ratio, CNV_stdev, flanks_stdev]

	return(setC_features)

def generate_setD_features(line, args):
	CNV_chr, CNV_start, CNV_end = line.split("\t")[0:3]
	return(BTlib.get_repeat_features_extended_segments(args.repeat_filename, CNV_chr, CNV_start, CNV_end, args.extend_proportion, args.num_segments))

####################################
### Parse command-line arguments ###
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.set_defaults(no_setB_features=False)
parser.set_defaults(no_setA_features=False)
parser.set_defaults(debug=False)

parser.add_argument("CNV_filename", type=str, help="CNV filename")
parser.add_argument("-d", "--depth-filename", type=str, help="samtools depth filename; if provided, model will contain depth features")
parser.add_argument("-r", "--repeat-filename", type=str, help="filename of repeats; if provided, model will contain repeat features")
parser.add_argument("-c", "--no-setB-features", action="store_true", help="Specify this option to omit features related to which callers detected a given CNV")
parser.add_argument("-t", "--no-setA-features", action="store_true", help="Specify this option to omit the feature specifying whether the CNV is a deletion or a duplication")
parser.add_argument("-s", "--num-segments", type=int, help="Number of segments in which to partition the extended CNV; default = 14", default=14)
parser.add_argument("-e", "--extend-proportion", type=float, help="Proportion of CNV to extend on either side; default = 0.2", default=0.2)
parser.add_argument("-z", "--debug", action="store_true", help="Set this option if you want debugging information to be generated")
args = parser.parse_args()
#####################################


CNV_file = open(args.CNV_filename)
header = CNV_file.readline() # Skip header line

feature_file = open(args.CNV_filename + ".features", "w")

if args.debug:
    debug_file = open(basename + ".debug", "w")
else:
    debug_file = None

feature_file.write("# ORIGINAL_DATA_HEADER:{}".format(header))
feature_file.write(generate_header(args))

# Make feature_file
for line in CNV_file:
	features = []
	features.append(generate_instance_name(line, args.CNV_filename))
	features.append(generate_in_benchmark_feature(line))

	if not args.no_setA_features:
		features = features + generate_setA_features(line)

	if not args.no_setB_features:
		features = features + generate_setB_features(line)

	if args.depth_filename:
		features = features + generate_setC_features(line, args)

	if args.repeat_filename:
		features = features + generate_setD_features(line, args)

	feature_file.write("\t".join(features) + "\n")

CNV_file.close()
feature_file.close()
