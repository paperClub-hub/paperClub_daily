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
from model_zoo import FinalMLP
import numpy as np
import pandas as pd
import torch
import pickle
import yaml
import glob
import re
import os





def init_finalmlp_model():
	""" """

	# 模型参数文件
	experiment_id = 'FinalMLP_meta2'
	dataset_id = 'FinalMLP_meta2'

	data_dir = f"/data/1_qunosen/project/res/rank/zhimo_rank/dev_rank/data/{dataset_id}"
	checkpoint = f"/data/1_qunosen/project/res/rank/FuxiCTR2/dev_test/checkpoints/{dataset_id}/{experiment_id}.model"
	config_file = "/data/1_qunosen/project/res/rank/FuxiCTR2/dev_test/config/FinalMLP_config"
	pickle_processo_file = os.path.join(data_dir, "feature_processor.pkl")

	# 加载特征处理器 及模型
	params = load_config(config_file, experiment_id)
	pickle_feature_processor = pickle.load(open(pickle_processo_file, 'rb'))
	feature_map = pickle_feature_processor.feature_map
	# feature_map = FeatureMap(params['dataset_id'], data_dir)
	feature_map.load(os.path.join(data_dir, "feature_map.json"), params)
	model = FinalMLP(feature_map, **params)
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



def finalmlp_infer(df: pd.core.frame.DataFrame):
	""" """

	data_tensor = preprocess(df, FEATURE_PROCESSOR, FEATURE_MAP)
	with torch.no_grad(): # 预测
		return_dict = MODEL(data_tensor)

	res = return_dict["y_pred"].data.cpu().numpy().reshape(-1)
	# print(f"din_infer, {res.tolist()[0]}")
	del data_tensor, return_dict
	return res


def meta_predict(clip_score: float = 0.2,
                aesthetic_score: float = 4.8,
                popular_score: float = 6.8):

	default_user_id = 1
	inputs = {"target": [0],
	         "userid": [default_user_id],
	         "clip_score": [clip_score],
	         "aesthetic_score": [aesthetic_score],
	         'popular_score': [popular_score],
	         }

	inputs = pd.DataFrame(inputs)
	score = finalmlp_infer(inputs).tolist()[0]

	return score




MODEL, FEATURE_PROCESSOR, FEATURE_MAP = None, None, None
if MODEL is None:
	MODEL, FEATURE_PROCESSOR, FEATURE_MAP = init_finalmlp_model()



if __name__ == '__main__':
	print()
	print(meta_predict())