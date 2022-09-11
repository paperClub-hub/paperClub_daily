#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @ Date: 2022-07-15 16:11
# @ Author: NING MEI


""" 获取 特征可视化配置文件 """


import os
import json
import numpy as np
import pandas as pd
import cv2


def load_img_data(json_path):

	with open(json_path, 'r') as f:
		data = json.load(f)

	embeddings = []
	labels = []
	files = []
	for i, dic in enumerate(data):
		input = dic['img_path'] if 'img_path' in dic else dic['words']
		embeddings.append(np.array(dic['vector']))
		labels.append(dic['label'])
		files.append(input)

	return np.array(embeddings), files, labels


def embeddings2projector_tsv(embs: np.ndarray, samples: list, title: str="images"):
	""" 借助于 tensorflow 完成：http://projector.tensorflow.org/
		输出文件：vector_pro.txt、vector_label.txt
	"""

	if not os.path.exists(title): os.mkdir(title)
	save_emb_path =  os.path.join(title, "embeddings.tsv")
	save_sample_path = os.path.join(title, "samples.tsv")

	dims = embs.shape[1]
	colums = [f"dim{1}" for i in range(dims)]
	df_emb = pd.DataFrame(embs, columns=colums)
	df_sample = pd.DataFrame(np.array(samples).T)
	df_emb.to_csv(save_emb_path, index=False, header=False, sep='\t')
	df_sample.to_csv(save_sample_path, index=False, header=False, sep='\t')




def samples2tsv(samples: list, save_path):
	""" 将样本名称为每行一个的tsv文件 """
	n = len(samples)
	with open(save_path, 'w') as f:
		for i in range(n):
			f.write('%s\n' % (str(samples[i])))


def embeddings2bytes(embs: np.ndarray, save_emb_path):
	""" 特征转为字节文件"""
	y = embs.flatten()
	n = len(y)
	with open(save_emb_path, 'wb') as f:
		for i in range(n):
			v = y[i]
			f.write(v)


def images2arrs(files_path: list, img_size:int = 224):
	""" 将多个图片文件转数组， NHWC格式 """

	def resize(cv2_img, img_size):
		""" 图片缩放到固定大小 """
		ori_h, ori_w, _ = cv2_img.shape
		ratio = img_size / max(ori_h, ori_w)
		resized_image = cv2.resize(cv2_img, (int(ori_w * ratio), int(ori_h * ratio)), cv2.INTER_AREA)

		### padding
		h, w, _ = resized_image.shape
		if h < img_size:
			h_pad_top = int((img_size - h) / 2.0)
			h_pad_bottom = img_size - h - h_pad_top
		else:
			h_pad_top = 0
			h_pad_bottom = 0
		if w < img_size:
			w_pad_left = int((img_size - w) / 2.0)
			w_pad_right = img_size - w - w_pad_left
		else:
			w_pad_left = 0
			w_pad_right = 0
		border_color = (255, 255, 255)

		del cv2_img, ori_h, ori_w, h, w
		return cv2.copyMakeBorder(resized_image, h_pad_top, h_pad_bottom, w_pad_left,
		                          w_pad_right, cv2.BORDER_CONSTANT, value=border_color)


	def files2arrs(files, img_size):
		""" 图像信息: 将图片转为数组 """
		img_arrs = []
		bg_img = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255
		for i, img_path in enumerate(files):
			try:
				src = cv2.imread(img_path)
				src = resize(src, img_size)
			except Exception as e:
				print(f" 图片获取失败：{e}, {img_path}")
				src = bg_img.copy()
			img = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
			img_arrs.append(img)
			del src, img

		img_arrs = np.stack(img_arrs)  ### 转变为 4维：NHWC
		del bg_img
		return img_arrs


	return files2arrs(files=files_path,  img_size=img_size)



def arrays2img(images, image_size=(-1, -1)):

	""" 将 NHWC 数组图片转化为一张合在一起的图片 """

	if isinstance(images, list):
		images = np.array(images)
	if image_size[0] > 0:
		img_h = image_size[0]
		img_w = image_size[1]
	else:
		img_h = images.shape[1]
		img_w = images.shape[2]
	img_c = images.shape[3]
	n_plots = int(np.ceil(np.sqrt(images.shape[0])))

	spriteimage = np.ones((img_h * n_plots, img_w * n_plots, img_c)) * 255
	for i in range(n_plots):
		for j in range(n_plots):
			this_filter = i * n_plots + j
			if this_filter < images.shape[0]:
				this_img = images[this_filter]
				this_img = cv2.resize(this_img, (img_w, img_h))
				this_img = this_img.reshape(img_w, img_h, img_c)
				if img_c > 1:
					this_img = cv2.cvtColor(this_img, cv2.COLOR_RGB2BGR)
				spriteimage[i * img_h:(i + 1) * img_h, j * img_w:(j + 1) * img_w, :] = this_img

	return np.uint8(spriteimage), [img_h, img_w]


def image2_single(imgfiles: list, img_size: int=224):
	""" 将多张图片合并为一张图片 """

	arrs = images2arrs(imgfiles, img_size=img_size)
	meta_img, img_shape = arrays2img(arrs, image_size=(img_size, img_size))
	del imgfiles, arrs
	return meta_img, img_shape ## img_shape = [img_h, img_w]




def embeddings_to_config(embs: np.ndarray, samples: list, title:str = "demo", sampletype:str="img"):
	if not os.path.exists(title): os.mkdir(title)

	if not os.path.exists(title): os.mkdir(title)
	save_emb_path =  os.path.join(title, "embeddings.bytes")
	save_sample_path = os.path.join(title, "samples.tsv")
	save_img_path = os.path.join(title, "images.png")
	config_path = os.path.join(title, 'configs.json')

	img_meta, singleImageDim = None, None
	if sampletype == "img":
		#### 获取图片
		img_meta, singleImageDim = image2_single(samples, img_size=224)
		cv2.imwrite(save_img_path, img_meta)

	### 获取特征
	embeddings2bytes(embs, save_emb_path)
	### 获取样本
	samples2tsv(samples, save_sample_path)

	### 合并结果
	config = {"modelCheckpointPath": "Demo datasets", "embeddings": []}
	item = {
			"tensorName": title,  ## 项目名字
			"tensorShape": list(embs.shape), ## 特征维度，num_samples, dim_of_feature
			"tensorPath": save_emb_path, ### 特征字节文件
			"metadataPath": save_sample_path, ## 样本名称
			}
	if sampletype == "img" and len(img_meta) > 0:
		item["sprite"] = {"imagePath": save_img_path, "singleImageDim": list(singleImageDim)}

	config["embeddings"].append(item)
	with open(config_path, 'w') as f:
		json.dump(config, f, sort_keys=True, indent=4)



if __name__ == '__main__':
	print("生成配置文件")

	json_files = ["./space.json",  "./pretrain.json", "./sbert.json"]
	for jsfile in json_files:
		embeddings, files, labels = load_img_data(jsfile)
		title = os.path.splitext(os.path.basename(jsfile))[0]
		embeddings_to_config(embs= embeddings, samples= files, title=title, sampletype='img')