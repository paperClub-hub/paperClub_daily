#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-09-16 22:34
# @Author   : NING MEI
# @Desc     :

""" 点击预测 """

import sys
sys.path.append("/data/1_qunosen/project/res/rank/FuxiCTR2")
from zk_data import IMAGE_DF
from fuxictr.utils import load_config
from fuxictr.features import FeatureMap
from model_zoo import DIN, FinalMLP
from LAC import LAC
import numpy as np
import pandas as pd
import torch
import pickle
import yaml
import glob
import re
import os


lac = LAC(mode='rank')
def clean_text(text):
	return re.sub("\W", "", text).strip()


def get_query_kw(text):
	text = clean_text(text)
	words_, tags_, ranks_ = lac.run(text)
	lac_weighted_tags = ['w', 'c', 'p', 'u', 'xc']
	lac_words = [w for w, t, r in zip(words_, tags_, ranks_) if t not in lac_weighted_tags and t]
	if not lac_words:
		return [text]

	return lac_words



def init_dim_model():
	""" """

	# 模型参数文件
	experiment_id = 'DIN_zhukeonle_seq1'
	dataset_id = 'DIN_zhukeonline_seq1'

	data_dir = f"/data/1_qunosen/project/res/rank/zhimo_rank/dev_rank/data/{dataset_id}"
	checkpoint = f"/data/1_qunosen/project/res/rank/FuxiCTR2/dev_test/checkpoints/{dataset_id}/{experiment_id}.model"
	config_file = "/data/1_qunosen/project/res/rank/FuxiCTR2/dev_test/config/DIN_config"
	pickle_processo_file = os.path.join(data_dir, "feature_processor.pkl")

	# 加载特征处理器 及模型
	params = load_config(config_file, experiment_id)
	pickle_feature_processor = pickle.load(open(pickle_processo_file, 'rb'))
	feature_map = pickle_feature_processor.feature_map
	# feature_map = FeatureMap(params['dataset_id'], data_dir)
	feature_map.load(os.path.join(data_dir, "feature_map.json"), params)
	model = DIN(feature_map, **params)
	model.load_weights(checkpoint)
	model.eval()

	return model, pickle_feature_processor, feature_map



def preprocess(df: pd.core.frame.DataFrame, FEATURE_PROCESSOR, FEATURE_MAP):
	""" 数据预处理及编码 """
	data_arrays = []
	df = FEATURE_PROCESSOR.preprocess(df)
	data_dict = FEATURE_PROCESSOR.transform(df)
	all_cols = list(FEATURE_MAP.features.keys()) + FEATURE_MAP.labels

	for col in all_cols:
		array = data_dict[col]
		if array.ndim == 1:
			data_arrays.append(array.reshape(-1, 1))
		else:
			data_arrays.append(array)

	data_tensor = torch.from_numpy(np.hstack(data_arrays))

	del df, data_dict, data_arrays
	return data_tensor



def din_infer(df: pd.core.frame.DataFrame):
	""" """

	data_tensor = preprocess(df, DIN_FEATURE_PROCESSOR, DIN_FEATURE_MAP)
	with torch.no_grad(): # 预测
		return_dict = DIN_MODEL(data_tensor)

	res = return_dict["y_pred"].data.cpu().numpy().reshape(-1)
	# print(f"din_infer, {res.tolist()[0]}")
	del data_tensor, return_dict
	return res





def ctr_predict(query: str = '祈福树',
                mid: int=5129114,
                click_sequence: list = None,
                mothod: str = "din"):

	if isinstance(mid, str):
		mid = int(mid)

	category = "平层"
	if len(IMAGE_DF[IMAGE_DF['image_id'] == mid]) > 0:
		category = IMAGE_DF[IMAGE_DF['image_id'] == mid]['category'].tolist()[0]

	if not click_sequence:
		click_sequence = np.nan
	else:
		click_sequence = "^".join(list(map(str, click_sequence)))

	default_user_id = 1
	keywords = get_query_kw(query)
	keywords = "^".join(keywords)
	inputs = {"clk": [0],
	         "userid": [default_user_id],
	         "category": [category],
	         "query": [keywords],
	         'image_id': [mid],
	         'click_sequence': [click_sequence]
	         }

	inputs = pd.DataFrame(inputs)
	score = din_infer(inputs).tolist()[0]

	return score


def ctr_rank(query, recall_mids: list, click_sequence: list = None, mothod: str = "din"):
	""" """
	print("召回方法：", mothod)

	scores = []
	ctr_dict = {}
	for mid in recall_mids:
		score = ctr_predict(query, mid, click_sequence, mothod)
		ctr_dict[mid] = score
		scores.append(score)

	# scores = np.array(scores)
	# idx = np.argsort(-scores)
	# ctr_scores = scores[idx]

	return ctr_dict



DIN_MODEL, DIN_FEATURE_PROCESSOR, DIN_FEATURE_MAP = None, None, None
if DIN_MODEL is None:
	DIN_MODEL, DIN_FEATURE_PROCESSOR, DIN_FEATURE_MAP = init_dim_model()



if __name__ == '__main__':
	print()
	print(ctr_predict())