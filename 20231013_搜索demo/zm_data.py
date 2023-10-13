#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-09-19 13:02
# @Author   : NING MEI
# @Desc     :


import json
import pandas as pd
from os.path import abspath, dirname, join
from config import USE_ZM80W

DATA_DIR = abspath(dirname(__file__))
def get_mid2url():
	""""""
	json_path = join(DATA_DIR, "./data/zm_mid2url.json")
	if USE_ZM80W:
		# json_path = join(DATA_DIR, "./data/zk80w_mid2url.json")
		json_path = join(DATA_DIR, "./data/zkzm_mid2url.json")

	return json.loads(open(json_path, 'r').read())


def load_zm_media_data():
	parquet_path = join(DATA_DIR, "./data/zm_media_data.parquet")
	if USE_ZM80W:
		# parquet_path = join(DATA_DIR, "./data/zk80w_media_data.parquet")
		parquet_path = join(DATA_DIR, "./data/zkzm_media_data.parquet") # zk线上 + zm

	df = pd.read_parquet(parquet_path)
	return df


MID2URL_MAP = dict()
if not MID2URL_MAP:
	MID2URL_MAP = get_mid2url()
	MID2URL_MAP = dict([int(id), url] for id, url in MID2URL_MAP.items())

IMAGE_DF = None
if IMAGE_DF is None:
	IMAGE_DF = load_zm_media_data()

PROJECT_DF = None
if PROJECT_DF is None:
	# project_data_path = "/data/1_qunosen/project/res/rank/zhimo_rank/data/zm_project.parquet"
	project_data_path = "/data/1_qunosen/project/res/rank/zhimo_rank/data/zm_project2.parquet"
	if USE_ZM80W:
		# project_data_path = "/data/1_qunosen/project/res/rank/zhimo_rank/data/zk80w_project.parquet"
		project_data_path = "/data/1_qunosen/project/res/rank/zhimo_rank/data/zkzm_project.parquet"

	PROJECT_DF = pd.read_parquet(project_data_path)

