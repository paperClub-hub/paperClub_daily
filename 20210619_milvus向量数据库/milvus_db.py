#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-05-16 11:35
# @Author   : NING MEI
# @Desc     :

""" milvus 数据库 """


from milvus import Milvus

import torch
import numpy as np
from collections import defaultdict
from typing import Dict, Callable, List, Union




def load_milvus_collection(collection_name: str):
	"""
	连接milvus 集合, milvus1.x
	"""

	_DIM = 1024  # 向量维度
	_INDEX_FILE_SIZE = 1024  # 单个索引文件最大尺寸
	milvus = Milvus(host=_HOST, port=_PORT)
	server_mgs, connet_status = milvus.server_status(timeout=10)

	if connet_status == "OK":
		print("milvus collection loading ... ")
		milvus.load_collection(collection_name=collection_name)
		_, info = milvus.get_collection_stats(collection_name=collection_name)
		if not info:
			print(f" Milvus 数据库集合{collection_name}")
		print(f"info: \n {info}")

		return milvus

	else:
		print("milvus服务连接失败 ！")
		return None


def get_milvus_id_by_vector(emb: List[List], top_k:int=100):
	""" 通过向量获取milvus id """
	search_param = {"nprobe": 16}
	if isinstance(emb, np.ndarray):
		emb = emb.tolist()

	status, hits = MILVUS.search(collection_name=COLLECTION_NAME, query_records=emb, top_k=top_k, params=search_param)
	del emb
	return hits



def get_entity_by_id(ids: List[int]):
	""" 通过id获取milvus向量 """

	status, milvus_embs = MILVUS.get_entity_by_id(collection_name=COLLECTION_NAME, ids=ids)
	del  ids
	return milvus_embs


_HOST = '127.0.0.1'
_PORT = '19530'
MILVUS = None
COLLECTION_NAME = "test_20230516"
if MILVUS is None:
	MILVUS = load_milvus_collection(collection_name=COLLECTION_NAME)


