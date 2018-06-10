#!/usr/bin/env bash

ERDS_filename=$1
CNVnator_filename=$2
job_ID=$3

print_status "Converting ERDS file to common format...\n"
convert_CNV_calls_to_common_format.py $ERDS_filename ERDS > $job_ID.ERDS.common.txt

print_status "Converting CNVnator file to common format...\n"
convert_CNV_calls_to_common_format.py $CNVnator_filename CNVnator > $job_ID.CNVnator.common.txt

print_status "Merging ERDS and CNVnator files...\n"
CNV_overlap.py -f Zhuozhi $job_ID.ERDS.common.txt $job_ID.CNVnator.common.txt > $job_ID.merged.txt

print_status "Generating features from merged file...\n"
generate_features.py --repeat-filename $RLCRS_DIR/RLCRs_DNN-CNV.txt $job_ID.merged.txt

print_status "Generating predictions...\n"
run_model.py --omit-truth $job_ID.merged.txt.features /hpf/largeprojects/tcagstor/users/btrost/papers/DNN-CNV/model_evaluation/NA12878/NA12878.txt.bm.RLCR.dirty.annotated2.features.DNN-CNV/cv_models/NA12878.txt.bm.RLCR.dirty.annotated2.features.all.model.meta
