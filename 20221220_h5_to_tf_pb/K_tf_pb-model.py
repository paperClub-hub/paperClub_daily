#!/usr/bin/env python
#*_* coding:utf-8*_*


import os,sys
import tensorflow as tf
from keras.models import load_model
from keras import backend as K
from tensorflow.python.framework import graph_io
import os.path as osp
from tensorflow.python.framework.graph_util import convert_variables_to_constants

# tensorflow                         1.13.1
# Keras                              2.2.4

def freeze_session(session, keep_var_names=None, output_names=None, clear_devices=True):
	graph = session.graph
	with graph.as_default():
		freeze_var_names = list(set(v.op.name for v in tf.global_variables()).difference(keep_var_names or []))
		output_names = output_names or []
		output_names += [v.op.name for v in tf.global_variables()]
		input_graph_def = graph.as_graph_def()
		# 从图中删除设备以获得更好的可移植性
		if clear_devices:
			for node in input_graph_def.node:
				node.device = ""
		# 用相同值的常量替换图中的所有变量
		frozen_graph = convert_variables_to_constants(session, input_graph_def, output_names, freeze_var_names)
		return frozen_graph

def keras_to_tf_model(modelfile,out_dir,pb_model):
	net_model = load_model(modelfile)
	print('input is :', net_model.input.name)
	print('output is:', net_model.output.name)
	sess = K.get_session()
	frozen_graph = freeze_session(sess, output_names=[net_model.output.op.name])
	graph_io.write_graph(frozen_graph,out_dir, pb_model, as_text=False)
	print('saved the constant graph (ready for inference) at: ',osp.join(out_dir,pb_model))
	print(K.get_uid())


modelfile = sys.argv[1]
out_dir = os.getcwd()
pb_model = "tf_"+str(os.path.basename(modelfile))+".pb"

keras_to_tf_model(modelfile,out_dir,pb_model)