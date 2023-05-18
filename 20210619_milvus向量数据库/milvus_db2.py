#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-05-16 11:35
# @Author   : NING MEI
# @Desc     :

""" milvus 数据库 """

from pymilvus import (
	connections,
	utility,
	FieldSchema,
	CollectionSchema,
	DataType,
	Collection,
)

import numpy as np
from collections import defaultdict
from typing import Dict, Callable, List, Union
from config import *


"""
milvus2.2.x 问题：

1. collection.drop 后需要重新创建索引；
2. collection.delete后，使用collection.num_entities向量数量未减少；
3. insert后必须 使用collection.flush();
"""

def load_milvus_collection(collection_name, host="127.0.0.1", port="19530"):
	""" 连接milvus 集合, milvus2.2.x """

	try:
		connections.connect(host=host, port=port)
		if utility.has_collection(collection_name) == False:
			print(f"{collection_name}: 创建中 ... ")

			# milvus字段
			default_fields = [FieldSchema(name="img_id", dtype=DataType.INT64, is_primary=True, description="图片编号"),
			                  FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=IMAGE_VECTOR_DIM,
			                              description="图片向量")
			                  ]
			# 创建collection
			default_schema = CollectionSchema(fields=default_fields, description="img_collection")
			COLLECTION = Collection(name=collection_name, schema=default_schema)

			if COLLECTION.name == collection_name:
				print(f"{collection_name}: 创建成功 ")
				return COLLECTION
			else:
				print(f"{collection_name}: 创建失败！")
				return None
		else:
			print(f"{collection_name}: 已存在！")

			return Collection(name=collection_name)

	except Exception as error:
		print(f"milvus链接失败: {error}")
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
		entities = [
			image_ids,
			vectors
		]
		insert_result = COLLECTION.insert(entities)

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
			entities = [
				bs_ids,
				bs_vectors
			]
			insert_result = COLLECTION.insert(entities)

			insert_succeed.extend(bs_ids)
			print("insert_result: ", insert_result)

		except Exception as error:
			print(f"插入失败：{error}")

	COLLECTION.flush()

	del image_ids, vectors
	return len(insert_succeed)



def create_index(COLLECTION):
	""" 创建向量索引（只需创建一次） """

	# COLLECTION.release()
	index = {
		"index_type": "IVF_FLAT",
		"metric_type": "IP",
		"params": {"nlist": 1024},
	}

	Status = COLLECTION.create_index(field_name="embeddings", index_params=index)

	COLLECTION.load()

	return True if Status.code == 0 else False


def milvus_search(query_emb: List[List], tok_k:int=3000):
	"""
	特征查询
	Args:
		query_emb: 二维别表
		tok_k:

	Returns:

	"""

	search_params = {"metric_type": "IP", "params": {"nprobe": 10}}

	if len(np.array(query_emb).shape) == 1:
		query_emb = [query_emb]

	result = COLLECTION.search(query_emb, "embeddings", search_params, limit=tok_k, output_fields=['img_id'])

	if result:
		hit_ids, hit_dist = [], []
		for hit in result:
			hit_ids.extend([h.id for h in hit])
			hit_dist.extend([h.distance for h in hit])
		return hit_ids, hit_dist

	else:
		return [[]], [[]]


def milvus_search_with_ids(query_emb, photo_ids:List[int]):
	""" milvus搜索结果过滤，指定用于收藏搜索 """

	if len(np.array(query_emb).shape) == 1:
		query_emb = [query_emb]

	search_params = {
		"data": query_emb,
		"anns_field": "embeddings",
		"param": {"metric_type": "IP", "params": {"nprobe": 10}},
		"offset": 0,
		"limit": 16384,
		"expr": f"img_id in {photo_ids}",
	}
	result = COLLECTION.search(**search_params)

	if result:
		hit_ids, hit_dist = [], []
		for hit in result:
			hit_ids.extend([h.id for h in hit])
			hit_dist.extend([h.distance for h in hit])
		return hit_ids, hit_dist

	else:
		return [[]], [[]]



def get_entity_by_id(image_ids:List[int], return_index:bool=False):
	"""
	根据id获取向量: 过滤不在milvus中的id
	Args:
		image_ids: milvus id
		return_index: True: 返回查询milvus对应image_ids索引，False返回milvus查询 id

	Returns:

	"""

	expr = f'img_id in {image_ids}'
	res = COLLECTION.query(
		expr=expr,
		output_fields=["img_id", "embeddings"],
		consistency_level="Strong"
	)

	if res:
		ids = []
		embeddings = []
		for hit in res:
			id = hit.get('img_id', -1)
			emb = hit.get("embeddings", [])
			if emb and id > -1:
				embeddings.append(emb)
				# 返回id对应索引
				if return_index:
					ids.append(image_ids.index(id))
				else:
					ids.append(id)
				del emb

		return ids, embeddings

	else:
		return [], [[]]



def milvus_delete(image_ids: List[int]):
	"""
	milvus删除向量
	Args:
		image_ids:

	Returns:

	"""

	if len(image_ids):
		expr = f'img_id in {image_ids}'
		COLLECTION.delete(expr)



COLLECTION = None
if COLLECTION is None:
	COLLECTION = load_milvus_collection(COLLECTION_NAME, MILVUS_HOST, MILVUS_PORT)


if __name__ == '__main__':
	print()
	import time
	import pandas as pd

	# # 图片特征写入milvus
	# df = pd.read_parquet("/data/1_qunosen/project/res/img_downs/embs/h14/img2_embs_vith14.parquet")
	# df['img_emb'] = df['img_emb'].apply(lambda x: x.tolist())
	# img_names = df['img_name'].tolist()
	# img_embs = df['img_emb'].tolist()
	#
	# img_ids = [i for i in range(len(img_names))]
	# img_id_dict = dict(zip(img_ids, img_names))
	#
	# start = time.time()
	# num_inserted = milvus_batch_insert(vectors=img_embs, image_ids=img_ids, batch_size=1000)
	# print("写入milvus消耗：", time.time() - start, f"总数：{len(img_ids)}, 成功插入：{num_inserted}")

	# # 创建特征索引
	# start = time.time()
	# status_index = create_index(COLLECTION)
	# print(f"创建特征索引: {status_index}")
	# print("创建特征索引消耗: ", time.time() - start)

	# # 相似特征查询
	# start = time.time()
	# query_emb = [img_embs[0]]
	# hits, scores = milvus_search(query_emb, tok_k=10)
	# print("query_emb: ", query_emb)
	# print("hits: ", hits)
	# print("相似特征查询消耗：", time.time() - start)

	# # 获取id对应向量
	# start = time.time()
	# for _ in range(10):
	# 	# start = time.time()
	# 	query_ids = [9999999999999900, 9, 0]
	# 	query_ids = list(range(50000))
	# 	ids, embs = get_entity_by_id(query_ids, return_index=False)
	# 	# print(ids)
	# 	# print(embs)
	# 	# print("获取id对应向量消耗：", time.time() - start )
	#
	# print("获取id对应向量消耗：", (time.time() - start)/10)
