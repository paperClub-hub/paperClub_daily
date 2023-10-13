#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-09-04 11:04
# @Author   : NING MEI
# @Desc     :


""" zm 文本召回 """

import numpy as np
from config import *
from typing import List, Dict
from zm_data import IMAGE_DF
from utils import norm, similar_by_vearch, get_trt_h14_txt_emb
from process import get_match_text_from_df, query2wordtags, query_process


def text_search(query_tag_pairs: List, query_intent: List, query_content: str, term_weight_dict: Dict,
                pthreshold: float = 0.5, tthreshold:float = 0.2, topk: int = 100, is_brute_search:bool=False):
	""" 通过指定pids进行vearch查询 """

	global LOG_DICT

	weighted_mids = []
	pts_recall_dict = {}
	media_precall_map = {}

	# 文本召回: 通过搜索词召回案例
	precall_dict, word_tags, ori_precall_dict = get_match_text_from_df(query_tag_pairs, term_weight_dict,
	                                                 threshold=pthreshold,
	                                                 num_candicates=int(topk * 1.5)
	                                                 )
	if not precall_dict:
		return pts_recall_dict, weighted_mids


	# vesrch查询
	print(" ******* 文中搜图：query_content: ", query_content)
	pids = list(precall_dict.keys())
	filter_terms = [{"term": {"pid": list(map(str, pids)), "operator": "or"}}]
	query_emb = get_trt_h14_txt_emb(query_content)
	resp = similar_by_vearch(query_emb, filter_terms)
	if resp:
		hits = resp.get("hits", {}).get("hits", [])
		ts_pids, ts_mids, ts_score = [], [], []
		new_ts_mids, new_ts_score = [], []
		intents = list(map(lambda x: x[0], query_intent))
		for i, hit in enumerate(hits):
			mid = int(hit.get("_id", 0))
			score = hit.get("_score", 0)
			pid = int(hit.get("_source", {}).get('pid', 0))
			title = hit.get("_source", {}).get('title', '')
			auther = hit.get("_source", {}).get('auther', '')
			ts_pids.append(pid)
			ts_mids.append(mid)
			ts_score.append(score)
			intent_stats = [w for w in intents if w in title or w in auther]
			if intent_stats:
				weighted_mids.append(mid)

			# 案例标题匹配分数，案例标题匹配+词权重分数, 案例下图片匹配分数
			LOG_DICT[mid].update({'q2pt_score': ori_precall_dict.get(pid), 'q2ptw_score': precall_dict.get(pid), 'q2pm_score': score})


		if ts_score:
			media_precall_map = dict([m, precall_dict.get(p)] for m, p in zip(ts_mids, ts_pids))
			if is_brute_search:
				pthreshold = tthreshold
			else:
				pthreshold = max(np.mean(ts_score), tthreshold)

			print(f"文本搜索-图片截断： threshold: {pthreshold}, is_brute_search: {is_brute_search} ")

			for mid, score in zip(ts_mids, ts_score):
				if score > pthreshold:
					new_ts_mids.append(mid)
					new_ts_score.append(score)

			if len(new_ts_mids):
				pts_recall_dict = norm(dict(zip(new_ts_mids, new_ts_score)))

	# 案例下属图片召回分值更新
	project_weight, media_weight = 0.3, 0.7
	if pts_recall_dict:
		# # 案例中：文搜图召回排序更新
		for mid, score in pts_recall_dict.items():
			#图片来自weighted_mids，提升权重
			if mid in weighted_mids:
				project_weight = 0.5
				media_weight = 0.5
			# 生成召回结果
			score = project_weight * media_precall_map.get(mid) + media_weight * pts_recall_dict.get(mid)
			pts_recall_dict[mid] = score

			LOG_DICT[mid].update({'tsearch_score': pts_recall_dict.get(mid)})

	return pts_recall_dict, weighted_mids




def text_search2(query_tag_pairs: List, query_intent: List, query_content: str, term_weight_dict: Dict,
                pthreshold: float = 0.5, tthreshold:float = 0.2, is_brute_search:bool=False, topk: int = 100):
	""" 文本搜搜索结果聚合 """

	global LOG_DICT

	weighted_mids = []
	pmrecall_weight_map = {}
	precall_weight_map = {}

	# 文本召回: 通过搜索词召回案例
	precall_dict, word_tags, ori_precall_dict = get_match_text_from_df(query_tag_pairs,
	                                                                   term_weight_dict,
	                                                                   query_intent=query_intent,
						                                                threshold=pthreshold,
						                                                num_candicates=int(topk * 1.5)
						                                                )
	if not precall_dict:
		return pmrecall_weight_map, weighted_mids

	# vesrch查询
	print(" ******* 文中搜图：query_content: ", query_content)
	pids = list(precall_dict.keys())
	filter_terms = [{"term": {"pid": list(map(str, pids)), "operator": "or"}}]
	query_emb = get_trt_h14_txt_emb(query_content)
	resp = similar_by_vearch(query_emb, filter_terms)
	if resp:
		hits = resp.get("hits", {}).get("hits", [])
		ts_pids, ts_mids, ts_score = [], [], []
		new_ts_mids, new_ts_score = [], []
		intents = list(map(lambda x: x[0], query_intent))
		for i, hit in enumerate(hits):
			mid = int(hit.get("_id", 0))
			score = hit.get("_score", 0)
			pid = int(hit.get("_source", {}).get('pid', 0))
			title = hit.get("_source", {}).get('title', '')
			auther = hit.get("_source", {}).get('auther', '')
			ts_pids.append(pid)
			ts_mids.append(mid)
			ts_score.append(score)
			intent_stats = [w for w in intents if w in title or w in auther]
			if intent_stats:
				weighted_mids.append(mid)

			# 案例标题匹配分数，案例标题匹配+词权重分数, 案例下图片匹配分数
			LOG_DICT[mid].update({'q2pt_score': ori_precall_dict.get(pid), 'q2ptw_score': precall_dict.get(pid), 'q2pm_score': score})


		if ts_score:
			precall_weight_map = dict([m, precall_dict.get(p)] for m, p in zip(ts_mids, ts_pids))
			if is_brute_search:
				pthreshold = tthreshold
			else:
				truncated_thres = np.median(ts_score)
				# truncated_thres = np.percentile(ts_score, 50)
				pthreshold = max(truncated_thres, tthreshold)

			print(f"文本搜索-图片截断： threshold: {pthreshold}, is_brute_search: {is_brute_search} ")
			# 案例下文本召回截断
			for mid, score in zip(ts_mids, ts_score):
				if score > pthreshold:
					new_ts_mids.append(mid)
					new_ts_score.append(score)

			pmrecall_weight_map = dict(zip(new_ts_mids, new_ts_score))


	return precall_weight_map, pmrecall_weight_map, weighted_mids





def testme():
	topk = 100
	text = '梁志天客厅'
	text = '苏州博物馆'
	text = '唐忠汉样板间'
	text = '唐忠汉 客厅'
	# text = '冰裂纹板'
	threshold = 0.5
	query_tag_pairs = query2wordtags(text)
	print("query_tag_pairs: ", query_tag_pairs)
	query_content, query_intent, query_sentiment, term_weight_dict = query_process(query=text, query_tags=query_tag_pairs)
	# text_recall_dict, weighted_mids = text_search(query_tag_pairs, query_intent, query_content, term_weight_dict,
	#                                                pthreshold=threshold, topk=topk)

	# print("text_recall_dict, weighted_mids : ", text_recall_dict, weighted_mids)

	ts_pweight_dict, ts_pmweight_dict, weighted_mids = text_search2(query_tag_pairs, query_intent, query_content, term_weight_dict,
	                                               pthreshold=threshold, topk=topk)
	print("ts_pweight_dict: ", ts_pweight_dict)
	print("ts_pmweight_dict: ", ts_pmweight_dict)



if __name__ == '__main__':
	print()


	testme()

	# print(LOG_DICT)

