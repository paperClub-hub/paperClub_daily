#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-09-04 13:35
# @Author   : NING MEI
# @Desc     :

import json
import requests
import numpy as np
import pandas as pd
from config import *
from typing import Dict, List
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity


def sort_by(x, y):
	x = list(map(lambda i: y.index(i), x))
	return x

def items2df(mids: List, df: pd.core.frame.DataFrame):
	""""""
	tdf = df[df['image_id'].isin(mids)]
	if len(tdf):
		tdf = tdf.sort_values(by='image_id', key=lambda x: sort_by(x, mids))
		del df
		return tdf
	else:
		return pd.DataFrame()


def items2idxes(mids: List, df: pd.core.frame.DataFrame):
	tdf = items2df(mids, df)
	return tdf.index.tolist()


def dict_update(d1: Dict, d2: Dict, method: str = 'max'):
	dic = {}
	k1 = d1.keys() & d2.keys()
	k2 = d1.keys() | d2.keys()

	print("d1, d2, 交集数, 并集数：", len(d1), len(d2), len(k1), len(k2))

	if len(k1) > 0:
		for k in k2:
			if method == 'max':
				dic[k] = max(d1.get(k, 0), d2.get(k, 0))

			if method == 'sum':
				dic[k] = sum([d1.get(k, 0), d2.get(k, 0)])

			elif method == 'agv':
				dic[k] = sum([d1.get(k, 0), d2.get(k, 0)]) / 2.0

			elif method == 'weight':
				dic[k] = d1.get(k, 0) * d2.get(k,0)

			else:
				dic[k] = max(d1.get(k, 0), d2.get(k, 0))

	else:
		dic.update(d1)
		dic.update(d2)

	del d1, d2

	return dic


def get_recall_topk(recall_dict: Dict, topk: int = 10, excludes: List = None, add_excludes: bool = True):
	if topk >= len(recall_dict):
		return recall_dict

	top_keys = list(map(lambda d: d[0], sorted(recall_dict.items(), key=lambda x: x[1], reverse=True)))
	top_keys = list(filter(lambda id: id not in excludes, top_keys))[: topk] if excludes else top_keys[: topk]
	if add_excludes and excludes:
		top_keys += excludes

	return dict([k, recall_dict.get(k)] for k in top_keys)


# def norm(dic: Dict):
#
# 	values = list(dic.values())
# 	min_x, max_x = min(values), max(values)
# 	del values
# 	return dict([k, (v - min_x) / (max_x - min_x + 1e-10)] for k, v in dic.items())

def norm(dic: Dict, min_y:float=0.1):
	values = list(dic.values())
	min_x, max_x = min(values), max(values)
	sigma = max(1 - min_y, 0)
	del values
	return dict([k, min_y + sigma * (v - min_x) / (max_x - min_x + 1e-10)] for k, v in dic.items())



def get_trt_h14_txt_emb(s):
	url = "http://192.168.0.17:9081/api/emb/clip/?"
	try:
		resp = requests.post(url, data=json.dumps({"sentences": [s]}))
		vectors = resp.json()
		if not vectors:
			return []
		return vectors[0]
	except:
		return []


def similar_by_emb(query_emb, all_embs, threshold: float = 0.2, topk: int = 100):
	""""""
	if not isinstance(query_emb, np.ndarray):
		query_emb = np.array(query_emb)

	if not isinstance(all_embs, np.ndarray):
		all_embs = np.array(all_embs)

	sim_scores, sim_idxes = [], []
	cos_sim = cosine_similarity(np.array([query_emb]), all_embs)[0]
	idx = np.argsort(-cos_sim)[:topk]
	for i, score in zip(idx, cos_sim[idx]):
		if score > threshold:
			sim_idxes.append(i)
			sim_scores.append(score)

	del query_emb, all_embs, idx, cos_sim
	return np.array(sim_idxes), sim_scores


def similar_by_vearch(query_emb, filter_terms: List[Dict] = None, threshold: float = 0.10, topk: int = 100):
	""" """

	vearch_url = f"{ROUTER_URL}/{DB_NAME}/{SPACE_NAME}/_search"
	query_body = {
		"query": {
			"sum": [{
				"field": "emb",
				"feature": query_emb,
				"min_score": threshold,
				"boost": 0.5
			}],
			"filter": []
		},
		"is_brute_search": 1,
		"fields": [],
		"size": topk,
		"retrieval_param": {
			"metric_type": "IP",
			"nlinks": 32,
			"efConstruction": 40,
			"efSearch": 64
		}
	}

	if filter_terms:
		query_body.get('query', {}).get('filter').extend(filter_terms)

	resp = requests.post(vearch_url, json=query_body)

	del query_emb, query_body
	return resp.json()


def vearch_get_by_ids(mids: List = [27659357, 49224930]):
	""" 批量获取vearch embedding """

	data = []
	query = {"query": {"ids": list(map(str, mids)),"fields": ['emb']}}
	vearch_url = f"{ROUTER_URL}/{DB_NAME}/{SPACE_NAME}/_query_byids"
	# print(vearch_url)
	res = requests.post(vearch_url, json=query).json()
	if not res:
		return []

	for h in res:
		if h.get('found'):
			# id = int(h.get('_id'))
			vearch_emb = h.get('_source', {}).get('emb', {}).get('feature')
			data.append(vearch_emb)

	del res, query, mids
	return data


DATATIME_NOW = datetime.now()
def datespan2now(publish_time: str):

	def str2date(datetime_str: str):
		if len(datetime_str) > 10:
			datetime_point = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
		else:
			datetime_point = datetime.strptime(datetime_str, "%Y-%m-%d")

		return datetime_point

	date_point = str2date(publish_time)
	month_spans = round((DATATIME_NOW - date_point).days / 30)
	# print("spans: ", date_point, DATATIME_NOW, month_spans)

	return month_spans


if __name__ == '__main__':
	print()
	print(datespan2now("2022-07-23"))