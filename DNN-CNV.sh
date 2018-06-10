#!/usr/bin/env bash

ERDS_filename=$1
CNVnator_filename=$2
job_ID=$3
BAM_file=$4

SCRIPTS_DIR="/root/DNN-CNV"
DATA_DIR="/data"

export PATH="$SCRIPTS_DIR/:$PATH"

if [[ $BAM_file ]]; then
	depth_option="--depth-filename $DATA_DIR/$BAM_file.depth"
	model_name="ABCD"
	if [ ! -e $DATA_DIR/$BAM_file.depth ]; then
    		samtools depth $DATA_DIR/$BAM_file > $DATA_DIR/$BAM_file.depth
	fi

	if [ ! -e $DATA_DIR/$BAM_file.depth.idx ]; then
		index_samtools_depth.py $DATA_DIR/$BAM_file.depth
	fi
else
	depth_option=""
	model_name="ABD"
fi

print_status "Converting ERDS file to common format...\n"
convert_CNV_calls_to_common_format.py $DATA_DIR/$ERDS_filename ERDS > $DATA_DIR/$job_ID.ERDS.common.txt

print_status "Converting CNVnator file to common format...\n"
convert_CNV_calls_to_common_format.py $DATA_DIR/$CNVnator_filename CNVnator > $DATA_DIR/$job_ID.CNVnator.common.txt

print_status "Merging ERDS and CNVnator files...\n"
CNV_overlap.py -f Zhuozhi $DATA_DIR/$job_ID.ERDS.common.txt $DATA_DIR/$job_ID.CNVnator.common.txt > $DATA_DIR/$job_ID.merged.txt

print_status "Generating features from merged file...\n"
generate_features.py $depth_option --repeat-filename $SCRIPTS_DIR/RLCRs_DNN-CNV.txt $DATA_DIR/$job_ID.merged.txt

print_status "Generating predictions...\n"
run_model.py --omit-truth $DATA_DIR/$job_ID.merged.txt.features $SCRIPTS_DIR/all.features.$model_name.DNN-CNV/models/all.features.$model_name.all.model.meta
