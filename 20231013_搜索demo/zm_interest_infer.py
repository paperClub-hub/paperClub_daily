#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-09-18 11:01
# @Author   : NING MEI
# @Desc     :


""" 点击相似预测 """

from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import linkage, fcluster
from collections import defaultdict, Counter
from sklearn_extra.cluster import KMedoids
from typing import List, Dict, Union
from utils import vearch_get_by_ids
import numpy as np
import torch
import time




def mids2embs(mids: List):
	embs = vearch_get_by_ids(mids)
	if isinstance(embs, list):
		embs = np.array(embs)
	return embs



def time_decay(t, init=0.8, m=30, finish=0.2):
	alpha = np.log(init / finish) / m
	l = - np.log(init) / alpha
	decay = np.exp(-alpha * (t + l))
	return decay


def get_embs_clusters(embs, timestamps, n_clusters_keep: int = 3):
	""" 特征聚类 """

	cluster_embs = []
	cluster_idxes = []
	clusters = defaultdict(list)
	clusters_tscore = defaultdict(float)
	embs_idxs_dict = defaultdict(list)

	Z = linkage(embs, method='ward')
	max_cluster = 9999
	flattened_clusters = fcluster(Z, t=max_cluster, criterion='maxclust')
	clusters_count = Counter(flattened_clusters)

	now = time.time()
	for i, c in enumerate(flattened_clusters):
		score = time_decay(now - timestamps[i])
		clusters_tscore[c] += score

	# 保留元素最多、最新的cluster
	clusters_keep = [c[0] for c in
	                 sorted(clusters_tscore.items(), key=lambda x: (clusters_count.get(x[0]), x[1]), reverse=True)][
	                :n_clusters_keep]
	for i, c in enumerate(flattened_clusters):
		if c in clusters_keep:
			clusters[c].append(embs[i])
			embs_idxs_dict[c].append(i)

	for cluster, cembs in clusters.items():
		if len(cembs) > 1:
			km = KMedoids(n_clusters=1, random_state=0).fit(cembs)
			cluster_emb = km.cluster_centers_[0]
			if isinstance(embs, np.ndarray):
				cidx = [i for i, e in enumerate(cembs) if (e == cluster_emb).all()][0]
			else:
				cidx = cembs.index(cluster_emb.tolist())
		else:
			cidx = 0
			cluster_emb = cembs[0]

		cluster_embs.append(cluster_emb.tolist())

		del cluster_emb, cembs
		# 聚类后item在原list的索引
		idx = embs_idxs_dict.get(cluster)[cidx]
		cluster_idxes.append(idx)

	del embs, embs_idxs_dict, clusters_tscore, clusters
	return cluster_embs, cluster_idxes


def find_similar(query_emb, all_embs, topk: int = 100):
	if isinstance(query_emb, list):
		query_emb = np.array(query_emb)

	cos_sim = cosine_similarity(np.array([query_emb]), all_embs)[0]
	idx = np.argsort(cos_sim)[::-1][:topk]
	scores = cos_sim[idx]

	del query_emb, all_embs
	return idx, scores


def get_embs_similar(query_embs, all_embs, topk: int = 100, threshold: float=0.3):
	""" """

	score_dict = defaultdict(list)
	if isinstance(query_embs, list):
		query_embs = np.array(query_embs)

	cos_sim = cosine_similarity(query_embs, all_embs)
	for i, cos_scores in enumerate(cos_sim):
		idxes = np.argsort(cos_scores)[::-1][:topk]
		scores = cos_scores[idxes]
		for idx, score in zip(idxes, scores):
			if score > threshold:
				score_dict[idx].append(score)

	del query_embs, all_embs
	return score_dict



def click_sequence2embeddings(click_sequences: List[int], click_timestamps:List, num_cluster: int=3):
	"""
	通过历史点击图片，获取历史点击图片聚类特征和索引
	Args:
		click_sequences: 历史点击图片编号
		click_timestamps: 点击图片时间戳
		num_cluster: 最大聚类中心数

	Returns: 聚类簇特征，聚类簇在点击序列的索引

	"""


	click_embs = mids2embs(click_sequences)

	cluster_embs, cluster_idxs = get_embs_clusters(click_embs, click_timestamps, num_cluster)

	del click_sequences, click_embs

	return cluster_embs, cluster_idxs


def interests_match(mids: List[int], click_sequences, click_timestamps, num_cluster: int=3, threshold:float=0.3, topk:int=100):
	"""
	Args:
		mids:
		click_sequences:
		click_timestamps:
		num_cluster:
		threshold:
		topk:

	Returns:

	"""

	match_dict = {}
	mids_embs = mids2embs(mids)

	if not click_sequences:
		return match_dict

	else:
		if len(click_sequences) == 1:
			cluster_idx = 0
			seq_interests = mids2embs(click_sequences)

		else:
			seq_interests, cluster_idx = click_sequence2embeddings(click_sequences, click_timestamps, num_cluster)

		interests_candidate = np.array(click_sequences)[np.array(cluster_idx)] # 兴趣代表
		score_dict = get_embs_similar(seq_interests, mids_embs, topk, threshold)
		# print("score_dict: ")
		for idx, scores in score_dict.items():
			match_dict[mids[idx]] = sum(scores)

	del mids_embs, seq_interests
	return match_dict



def testme():

	# 知末数据
	timestamps = []
	click_sequences = [27659357, 27659301, 23917964, 27659296, 27659361, 60761810, 60761846, 50490030]
	for _ in range(len(click_sequences)):
		time.sleep(0.5)
		timestamps.append(time.time())

	num_cluster = 3
	recall_mids = [23917964, 27659296, 60761810, 50490030]
	res = interests_match(recall_mids, click_sequences, timestamps, num_cluster)
	print("知末数据 res: ", res)


if __name__ == '__main__':
	print()
	testme()