#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-06-21 16:54
# @Author   : NING MEI
# @Desc     :

""" 意图分类 """

import paddle
import numpy as np
import paddle.nn.functional as F
from os.path import abspath, dirname, join, exists
from paddlenlp.transformers import AutoModelForSequenceClassification, AutoTokenizer


def init_hierarchical():
	""" 加载层次分类模型 """

	pwd = abspath(dirname(__file__))
	checkpoint_path = join(pwd, "./checkpoint")
	label_path = join(pwd, "./label.txt")

	assert exists(checkpoint_path), f"not exists: {checkpoint_path}"
	assert exists(label_path), f"not exists: {label_path}"

	labels = list(map(lambda x: x.strip(), open(label_path, 'r').readlines()))

	model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)
	tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
	model.eval()

	return model, tokenizer, np.array(labels)


def infer(query: str, threshold: float = 0.8, debug: bool = False):
	""" 基于层次分类进行搜索词意图分类 """

	result = TOKENIZER(text=[query], max_seq_len=128)
	input_ids = result.get('input_ids')
	token_type_ids = result.get('token_type_ids')
	inputs = {"input_ids": paddle.to_tensor(input_ids), "token_type_ids": paddle.to_tensor(token_type_ids)}

	logits = CATE_MODEL(**inputs)
	probs = F.sigmoid(logits).numpy().squeeze()

	idx = np.argmax(probs.squeeze())
	scores = probs[idx]
	query_cate = CATS[idx]

	debug and print("query: ", query)
	debug and print("query_cate:, scores", query_cate, scores)

	category = ''
	if scores > threshold and query_cate:
		category = query_cate.split("#")[0]

	return category


CATE_MODEL, TOKENIZER, CATS = None, None, []
if CATE_MODEL is None:
	CATE_MODEL, TOKENIZER, CATS = init_hierarchical()

if __name__ == '__main__':
	text = "客厅沙发"

	res = infer(text)
	print(res)
