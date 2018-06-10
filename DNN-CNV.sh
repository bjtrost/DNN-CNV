#!/usr/bin/env bash

ERDS_filename=$1
CNVnator_filename=$2
job_ID=$3
BAM_file=$4

pwd
DIR=`pwd`

if [[ $BAM_file ]]; then
	depth_option="--depth-filename $BAM_file.depth"
	model_name="ABCD"
	if [ ! -e $BAM_file.depth ]; then
    		samtools depth $BAM_file > $BAM_file.depth
	fi

	if [ ! -e $BAM_file.depth.idx ]; then
		$DIR/index_samtools_depth.py $BAM_file.depth
	fi
else
	depth_option=""
	model_name="ABD"
fi

$DIR/print_status "Converting ERDS file to common format...\n"
$DIR/convert_CNV_calls_to_common_format.py $ERDS_filename ERDS > $job_ID.ERDS.common.txt

$DIR/print_status "Converting CNVnator file to common format...\n"
$DIR/convert_CNV_calls_to_common_format.py $CNVnator_filename CNVnator > $job_ID.CNVnator.common.txt

$DIR/print_status "Merging ERDS and CNVnator files...\n"
$DIR/CNV_overlap.py -f Zhuozhi $job_ID.ERDS.common.txt $job_ID.CNVnator.common.txt > $job_ID.merged.txt

$DIR/print_status "Generating features from merged file...\n"
$DIR/generate_features.py $depth_option --repeat-filename RLCRs_DNN-CNV.txt $job_ID.merged.txt

$DIR/print_status "Generating predictions...\n"
$DIR/run_model.py --omit-truth $job_ID.merged.txt.features all.features.$model_name.DNN-CNV/models/all.features.$model_name.all.model.meta
