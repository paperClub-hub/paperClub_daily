#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-05-16 11:35
# @Author   : NING MEI
# @Desc     :

""" milvus v1.1.2 数据库 """


from milvus import Milvus, IndexType, MetricType, Status

import torch
import numpy as np
from collections import defaultdict
from typing import Dict, Callable, List, Union
from config import *



def load_milvus_collection(collection_name, host="127.0.0.1", port="19530"):
	"""
	连接milvus 集合, milvus1.x
	"""

	_INDEX_FILE_SIZE = 1024  # 单个索引文件最大尺寸
	milvus = Milvus(host=host, port=port)
	server_mgs, connet_status = milvus.server_status(timeout=10)

	if connet_status == "OK":
		print("milvus collection loading ... ")
		status, ok = milvus.has_collection(collection_name)

		if not ok:
			print(f"创建集合：{collection_name} ...")
			param = {
				'collection_name': collection_name,
				'dimension': IMAGE_VECTOR_DIM,
				'index_file_size': _INDEX_FILE_SIZE,  # 可选
				'metric_type': MetricType.IP  # 内积，可选欧氏距离 MetricType.L2
			}

			milvus.create_collection(param)
			_, is_create = milvus.has_collection(collection_name)

			if is_create:
				print(f"创建成功：{collection_name} ")
			else:
				print(f"创建失败：{collection_name} ！")

		milvus.load_collection(collection_name=collection_name)
		_, info = milvus.get_collection_stats(collection_name=collection_name)
		if not info:
			print(f" Milvus 数据库集合{collection_name}")
		print(f"info: \n {info}")

		return milvus

	else:
		print("milvus服务连接失败 ！")
		return None



def milvus_insert(image_ids: List[int], vectors: List[List]):
	"""
	一次性插入milvus
	Args:
		image_ids: 图片编号, int
		vectors: 特征向量，二维list
	Returns:

	"""

	assert len(vectors) == len(image_ids), "'len(vectors) != len(image_ids)'"

	try:

		insert_result = MILVUS.insert(collection_name=COLLECTION_NAME, records=vectors, ids=image_ids)

	except Exception as error:
		print(f"插入失败：{error}")

	del image_ids, vectors


def milvus_batch_insert(image_ids: List[int], vectors: List[List], batch_size: int = 500):
	"""
	分批批量插入milvus
	Args:
		image_ids: 图片编号, int
		vectors: 特征向量，二维list
		batch_size: 批插入大小
	Returns:

	"""

	assert len(vectors) == len(image_ids), "'len(vectors) != len(image_ids)'"

	insert_succeed = []
	for i in range(0, len(vectors), batch_size):

		try:
			bs_vectors = vectors[i: i + batch_size]
			bs_ids = image_ids[i: i + batch_size]
			insert_result = MILVUS.insert(collection_name=COLLECTION_NAME, records=bs_vectors, ids=bs_ids)
			insert_succeed.extend(bs_ids)

			print("insert_result: ", insert_result)

		except Exception as error:
			print(f"插入失败：{error}")

	MILVUS.flush()

	del image_ids, vectors
	return len(insert_succeed)


def create_index():
	""" 创建向量索引（只需创建一次） """

	ivf_param = {'nlist': 16384}
	Status = MILVUS.create_index(COLLECTION_NAME, IndexType.IVF_FLAT, ivf_param)

	return True if Status.code == 0 else False



def milvus_search(query_emb: List[List], top_k:int=3000):
	""" 通过向量获取milvus id """
	search_param = {"nprobe": 16}
	if isinstance(query_emb, np.ndarray):
		query_emb = query_emb.tolist()


	status, result = MILVUS.search(collection_name=COLLECTION_NAME, query_records=query_emb, top_k=top_k, params=search_param)

	del query_emb

	# return result

	if status == 0:
		if result[0]:
			hit_ids, hit_dist = [], []
			for hit in result:
				hit_ids.append([h.id for h in hit])
				hit_dist.append([h.distance for h in hit])
			return hit_ids, hit_dist

		else:
			return [[]], [[]]
	else:
		return [[]], [[]]



def get_entity_by_id(milvus_ids: List[int], return_index:bool=False):
	"""
	根据id获取向量: 过滤不在milvus中的id
	Args:
		image_ids: milvus id
		return_index: True: 返回查询milvus对应image_ids索引，False返回milvus查询 id

	Returns:

	"""

	status, res = MILVUS.get_entity_by_id(collection_name=COLLECTION_NAME, ids=milvus_ids)
	if res:
		ids = []
		embeddings = []
		for i, emb in enumerate(res):
			if len(emb) !=0:
				embeddings.append(emb)
				id = milvus_ids[i]
				if return_index:
					ids.append(milvus_ids.index(id))
				else:
					ids.append(id)
				del emb

		del milvus_ids
		return ids, embeddings

	else:
		del milvus_ids
		return [], []


MILVUS = None
if MILVUS is None:
	MILVUS = load_milvus_collection(collection_name=COLLECTION_NAME,
	                                host=MILVUS_HOST,
	                                port='19530')



if __name__ == '__main__':
	print()

	# milvus==1.1.2, conda jina2
	import time
	import pandas as pd

	# # 图片特征写入milvus
	df = pd.read_parquet("/data/1_qunosen/project/res/img_downs/embs/h14/img2_embs_vith14.parquet")
	df['img_emb'] = df['img_emb'].apply(lambda x: x.tolist())
	img_names = df['img_name'].tolist()
	img_embs = df['img_emb'].tolist()
	img_ids = [i for i in range(len(img_names))]
	img_id_dict = dict(zip(img_ids, img_names))

	# 图片特征写入milvus：
	# milvus_batch_insert(image_ids=img_ids, vectors=img_embs, batch_size=1000)

	# # 创建特征索引
	# start = time.time()
	# status_index = create_index()
	# print(f"创建特征索引: {status_index}")
	#

	# # 相似特征查询
	# query_emb = img_embs[:1]
	# hit_ids, hit_dist = milvus_search(query_emb, top_k=10)
	# print("hit_ids: ", hit_ids)

	# # 获取id对应向量
	# query_ids = [99999999999, 1, 0]
	# ids_in_milvus, embeddings = get_entity_by_id(milvus_ids=query_ids)
	# print("embeddings: ", len(embeddings), ids_in_milvus)

