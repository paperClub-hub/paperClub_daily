#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @ Date: 2022-08-27 9:42
# @ Author: paperClub

import os
import jieba
from pathlib import Path
from collections import defaultdict
from typing import  List, Dict
from ordered_set import OrderedSet




def init():
	""" 初始化 """

	CUSTOM_DICT = Path.cwd() / "MODELS/custom_dict.txt"
	LABEL_PATH = Path.cwd() / "MODELS/jieba_dict.txt"

	def load_dict():
		""" 加载 lac自定义字典 """
		label_dict = defaultdict(list)
		with open(CUSTOM_DICT, 'r') as f:
			for line in f.readlines():
				line = line.strip()
				k, v = line.split('/')[-1].strip(), line.split('/')[0].strip()
				label_dict[k].append(v)
		label_dict = dict([k, sorted(v)] for k, v in label_dict.items())
		return label_dict


	def save_dict(label_dict):
		""" 生成自定义jieba字典 """
		label_set = OrderedSet()
		all_labels = label_dict.values()
		for labels in all_labels:
			for label in labels:
				label_set.add(label)
		print('\n'.join(label_set), file=open(LABEL_PATH, 'w', encoding='utf-8'))

	label_dict = load_dict()
	save_dict(label_dict)
	if os.path.exists(LABEL_PATH):
		print(" 加载自定义jieba字典 ... ")
		jieba.load_userdict(str(LABEL_PATH))

	return label_dict



def predict(text: str = '现代风的餐厅里加入盆栽桌玩、屏风等中式家居元素，提高了家居的观赏性和东方韵味👍。', ):
	""" 标签类型预测 """
	result = defaultdict(list)
	tokenizer = list(jieba.tokenize(text))
	TAGS_DICT = { # 标签类型对应关系
		"STYLE": "风格", "SPACE": "空间", "LOSPACE": "局部空间", "OBJECT": "物体",
		 "SHAPE": "形状", "COLOR": "颜色", "MATERIAL": "材质",  "PATTERN": "纹理",
		 "FEATURE": "特征", "BRAND": "品牌", 	"PROPTY": "户型",
		}


	for item in tokenizer:
		token, start_offset, end_offset = item
		for label_type, label_name in TAGS_DICT.items():
			labels = CUSTOM_DICT.get(label_type, [])
			if token in labels:
				dic = {"text": token, 'start': start_offset, 'end': end_offset, 'probability': 10, }
				result[label_type].append(dic)

	return [dict(result)]



CUSTOM_DICT = {}
if not CUSTOM_DICT:
	CUSTOM_DICT = init()

if __name__ == '__main__':

	text = "客厅装修"
	print(predict(text))


