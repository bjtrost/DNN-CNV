#!/usr/bin/env python3

# Accepts any number of files containing CNVs as input, and outputs groups of those CNVs,
# for which each member of a group has 50% reciprocal overlap with at least one other CNV in that group.

import BTlib
import subprocess
import re
import argparse
import statistics
import copy

####################################
### Parse command-line arguments ###
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--CNV-file-format", type=str, default="autodetect")
parser.add_argument("-k", "--item-name-key", type=str, default="string_rep_caller_filename")
parser.add_argument("-o", "--overlap-function", type=str, default="fifty_percent_reciprocal")
parser.add_argument("CNV_filenames", type=str, default=None, nargs="+")
args = parser.parse_args()
#####################################

overlap_functions = {}
overlap_functions["fifty_percent_reciprocal"] = BTlib.fifty_percent_reciprocal_overlap
overlap_functions["any"] = BTlib.any_overlap

CNVs = {}
headers = {}

for filename in args.CNV_filenames:
    CNVs[filename], headers[filename] = BTlib.read_functions[args.CNV_file_format](filename)

CNVs_by_chromosome = {}
for i in range(0, len(args.CNV_filenames)):
    CNVs_by_chromosome[args.CNV_filenames[i]] = BTlib.CNVs_by_chromosome(CNVs[args.CNV_filenames[i]])

groups = BTlib.get_groups(CNVs_by_chromosome, args.CNV_filenames, args.item_name_key, overlap_functions[args.overlap_function])

print("Chr\tStart\tEnd\tSize\tType\tNumber of files containing this variant\tList of files containing this variant")

##################################################################################
# Done creating file containing benchmark size distribution
##################################################################################

groups = sorted(groups, key=len, reverse=True)

for group in groups:
    found = False

    # If one of the groups is ERDS, use those breakpoints; else, use the first one
    for caller in group:
        if caller["caller"] == "ERDS":
            chrom = caller["chr"]
            start = caller["start"]
            end = caller["end"]
            size = caller["size"]
            found = True

    if not found:
        chrom = group[0]["chr"]
        start = group[0]["start"]
        end = group[0]["end"]
        size = group[0]["size"]

    group_names = [item[args.item_name_key] for item in group]
    concat = "\t".join(group_names)
    print("\t".join([str(chrom), str(start), str(end), str(size), group[0]["type"], str(len(group)), ", ".join(sorted(group_names, key=str.lower))]))
