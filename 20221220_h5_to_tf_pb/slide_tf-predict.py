#usr/bin/python3
#coding=utf-8

import os,cv2
import tensorflow as tf
import numpy as np




def tf_slide_predict(slide_path,nucl_x,nucl_y, pb_path):
	class_names = [0, 1]
	class_label = {0:"WNL",1:"MAL"}
	patch_w, patch_h = 64, 64
	dRate = 0.627
	with tf.Graph().as_default():
		output_graph_def = tf.GraphDef()
		with open(pb_path, "rb") as f:
			output_graph_def.ParseFromString(f.read())
			tensors = tf.import_graph_def(output_graph_def, name="")
		with tf.Session() as sess:
			init = tf.global_variables_initializer()
			sess.run(init)
			sess.graph.get_operations()
			input_x = sess.graph.get_tensor_by_name("lambda_1_input:0") 
			out_softmax = sess.graph.get_tensor_by_name("activation_5/Softmax:0") 
			img = cv2.imread(slide_path)
			img_w, img_h_, _ = img.shape
			#img = cv2.resize(img, (int(img_h * dRate), int(img_w * dRate)),interpolation=cv2.INTER_CUBIC) 
			img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			gray_rgb = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
			x1, x2 = nucl_x - int(patch_w / 2), nucl_x + int(patch_w / 2)
			y1, y2 = nucl_y - int(patch_h / 2), nucl_y + int(patch_h / 2)
			patch_img = gray_rgb[y1:y2, x1:x2]
			patch_img = cv2.resize(patch_img, dsize=(patch_h, patch_w))
			img_out_softmax = sess.run(out_softmax,feed_dict={input_x: np.array(patch_img).reshape((-1, patch_h, patch_w, 3))}) 
			pred_index = np.argmax(img_out_softmax[0])
			print(img_out_softmax)
			print(class_names[pred_index])
			print("class_lbael: %s"%(class_label.get(int(class_names[pred_index]))))
			return img_out_softmax


patch_to_slide = "./F7777000001.000.bmp"
patch_to_pb_model = "./tf_gpu._model.pb"
nucl_x,nucl_y = 1106,346

tf_slide_predict(patch_to_slide,nucl_x,nucl_y, patch_to_pb_model)