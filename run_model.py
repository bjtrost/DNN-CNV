#!/usr/bin/env python3

import numpy as np
import pandas as pd
import tensorflow as tf
import argparse
import os
import BTlib

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2" # Get rid of tensorflow messages about potential speedups

####################################
### Parse command-line arguments ###
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.set_defaults(omit_true=False)
parser.add_argument("cnv_filename", type=str, help="CNV filename")
parser.add_argument("model_meta_filename", type=str, help="Model meta filename")
parser.add_argument("--omit-truth", help="Omit truth value of CNV from outut", action="store_true")
args = parser.parse_args()
#####################################

data, labels_for_prediction_raw, instance_names_for_prediction, original_header = BTlib.prepare_data_for_tensorflow(args.cnv_filename)
probabilities_file = open(args.cnv_filename + ".prob", "w")

loaded_graph = tf.Graph()
with tf.Session(graph=loaded_graph) as sess:
    sess.run(tf.local_variables_initializer())
    new_saver = tf.train.import_meta_graph(args.model_meta_filename)
    new_saver.restore(sess, args.model_meta_filename.replace(".meta", ""))

    softmax_probabilities = loaded_graph.get_tensor_by_name('softmax_probabilities:0')
    data_placeholder = loaded_graph.get_tensor_by_name('data_placeholder:0')
    dropout_keep_proportion_placeholder = loaded_graph.get_tensor_by_name('dropout_keep_proportion_placeholder:0')

    positive_probabilities = [x[1] for x in softmax_probabilities.eval({data_placeholder: data, dropout_keep_proportion_placeholder: 1.0})]

    if args.omit_truth:
        probabilities_file.write("{}\tDNN-CNV probability\n".format(original_header))
    else:
        probabilities_file.write("{}\tIn benchmark?\tDNN-CNV probability\n".format(original_header))

    for index in range(len(positive_probabilities)):
        if args.omit_truth:
            probabilities_file.write("{}\t{:.3f}\n".format(instance_names_for_prediction[index].replace("***", "\t"), positive_probabilities[index]))
        else:
            probabilities_file.write("{}\t{}\t{:.3f}\n".format(instance_names_for_prediction[index].replace("***", "\t"), labels_for_prediction_raw[index], positive_probabilities[index]))

    probabilities_file.close()
