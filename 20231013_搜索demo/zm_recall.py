#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-09-16 17:45
# @Author   : NING MEI
# @Desc     :


from utils import items2df, norm, get_trt_h14_txt_emb, dict_update, get_recall_topk, datespan2now
from process import query2wordtags, query_process, intent_match
from sklearn.metrics.pairwise import cosine_similarity
from zm_text_recall import text_search, text_search2
from zm_vision_recall import vision_search
from zm_data import IMAGE_DF
from typing import Dict, List
import pandas as pd
import numpy as np
import requests
import json


from zm_data import MID2URL_MAP
from collections import Counter
from config import LOG_DICT


def web_url(url):
	return f"{url}?imageView2/3/w/400/h/400/"



def RECALL(text: str, threshold: float=0.5, topk:int=20):
	"""

	"""

	print("_________ 知末搜索 ___________________")
	print("查询词：", text)
	global LOG_DICT

	# 意图识别
	weighted_mids = []
	tsearch_enabled = True
	query_tag_pairs = query2wordtags(query=text, ner_to_seg=True)
	print("query_tag_pairs: ", query_tag_pairs)

	is_brute_search = False
	query_content, query_intent, query_sentiment, term_weight_dict = query_process(query=text, query_tags=query_tag_pairs)

	clip_search_text = query_content
	if query_sentiment:
		text_prefix = "高级感"

		query_content_tmp = " ".join([w for w in query_content.split() if w not in list(map(lambda x: x[0], query_intent))])
		if not query_content_tmp:
			clip_search_text = text
			is_brute_search = True

		else:
			if text_prefix not in query_content:
				clip_search_text = text_prefix + query_content


	print("query_tag_pairs, query_content, query_intent: ", query_tag_pairs, query_content, query_intent)
	if not query_tag_pairs:
		tsearch_enabled = False

	recall_dict = {}
	text_recall_dict = {}
	vision_recall_dict = {}

	# 文本召回
	if tsearch_enabled:
		print(" ---------||||  文本搜索  ")

		tthreshold = 0.2
		pthreshold = threshold
		if not query_intent:
			pthreshold = 0.6

		if is_brute_search:
			pthreshold = 0.1
			tthreshold = 0.1
			text_recall_dict, weighted_mids = text_search(query_tag_pairs, query_intent, clip_search_text,
			                                              term_weight_dict, pthreshold=pthreshold,
			                                              tthreshold=tthreshold, topk=topk,
			                                              is_brute_search=is_brute_search)
		else:
			text_recall_dict, weighted_mids = text_search(query_tag_pairs, query_intent, clip_search_text,
		                                                  term_weight_dict, pthreshold=pthreshold,
		                                                  tthreshold=tthreshold, topk=topk,
		                                                  is_brute_search=is_brute_search)

		num_text_recalls = len(text_recall_dict)
		# 文本召回不足：视觉召回补充
		if num_text_recalls < topk:
			print(" ==>>>>  ", "   文本召回不足：视觉召回补充")
			# 文召回为空时
			if num_text_recalls == 0 and not query_intent:
				vision_recall_dict = vision_search(text, query_intent, query_sentiment, [],
				                                   threshold=0.18, topk=topk, query_filter=False)
			else:
				vision_recall_dict = vision_search(text, query_intent, query_sentiment, query_tag_pairs,
			                                        threshold=0.18, topk=topk, query_filter=True)

			num_vision_recalls = len(vision_recall_dict)
			# 意图明确、但文本召回为空
			if not weighted_mids:
				""""""
				v_mids = list(vision_recall_dict.keys())
				tdf = IMAGE_DF[IMAGE_DF['image_id'].isin(v_mids)]
				allpids = tdf['project_id'].tolist()
				v_pids = intent_match(query_intent, tdf)
				weighted_mids = [id for id, apid in zip(v_mids, allpids) if apid in v_pids]


			# 补充召回并更新视觉召回结果
			needed_num = topk - num_text_recalls
			intersection_mids = text_recall_dict.keys() & vision_recall_dict.keys()
			vision_recall_dict = get_recall_topk(vision_recall_dict,
			                                     topk=needed_num,
			                                     excludes=intersection_mids,
			                                     add_excludes=True)

			print("文召回数，图召回数, 交集: ", num_text_recalls, num_vision_recalls, len(intersection_mids))



		# 合并文本召回 和 视觉召回
		recall_dict = dict_update(text_recall_dict, vision_recall_dict, method='max')

	else:
		# 图片视觉召回
		# TODO: 视觉召回质量不好怎么办？
		print(" ---------||||  图片搜索")

		vision_recall_dict = vision_search(text, query_intent, query_sentiment, query_tag_pairs,
		                            threshold=0.18, topk=topk, query_filter=False)

		recall_dict = vision_recall_dict

	for k, v in vision_recall_dict.items():
		LOG_DICT[k].update({'q2m_score': v})

	for k,v in recall_dict.items():
		LOG_DICT[k].update({'similarity': v})

	# print("weighted_mids: ", weighted_mids)
	return text_recall_dict, vision_recall_dict
	# return recall_dict, weighted_mids


def get_recall_dict(precall_map: Dict, pmrecall_map: Dict, vrecall_map: Dict, weighted_mids: List = None):
	res_dict = {}
	if pmrecall_map:
		pweight, mweight = 0.2, 0.8
		interects = list(pmrecall_map.keys() & vrecall_map.keys())
		pmrecall_map = norm(pmrecall_map)
		for mid, mscore in pmrecall_map.items():
			if weighted_mids and mid in weighted_mids:
				pweight, mweight = 0.5, 0.5


			tscore = pweight * precall_map.get(mid) + mweight * mscore
			if mid in interects:
				tscore = max(tscore, vrecall_map.get(mid, 0))

			res_dict[mid] = tscore

		for mid, vscore in vrecall_map.items():
			vweight = 1.5
			res_dict[mid] = vscore * vweight

	else:
		mweight = 0.5
		for mid, vscore in vrecall_map.items():
			if mid in weighted_mids:
				mweight = 0.8

			res_dict[mid] = mweight * vscore

	del precall_map, pmrecall_map, vrecall_map, weighted_mids

	return res_dict


def RECALL2(text: str, threshold: float=0.5, topk:int=20):
	""" 统一处理召回分数 """
	# TODO: 搜索权重统一归一化

	# 查询词处理
	# # 分类词及实体判定
	query_tag_pairs = query2wordtags(query=text, ner_to_seg=True)
	# # 词权重、查询词情感、查询意图
	query_content, query_intent, query_sentiment, term_weight_dict = query_process(query=text,
	                                                                               query_tags=query_tag_pairs)
	is_brute_search = False
	clip_search_text = query_content
	if query_sentiment:
		text_prefix = "高级感"

		query_content_tmp = " ".join(
			[w for w in query_content.split() if w not in list(map(lambda x: x[0], query_intent))])
		if not query_content_tmp:
			clip_search_text = text
			is_brute_search = True

		else:
			if text_prefix not in query_content:
				clip_search_text = text_prefix + query_content

	print("query_tag_pairs, query_content, query_intent: ", query_tag_pairs, query_content, query_intent)


	# 搜索
	text_recall_dict = {}
	vision_recall_dict = {}

	tsearch_enabled = True
	if not query_tag_pairs:
		tsearch_enabled = False

	# 开启文本召回
	if tsearch_enabled:
		# TODO: 文本搜索权重合在一起归一化处理
		print(" ---------||||  文本搜索  ")
		# pthreshold用于案例过滤，tthreshold用于案例下图片过滤时参考
		tthreshold = 0.2
		pthreshold = threshold
		if not query_intent:
			pthreshold = 0.6

		# 文本搜索：
		# # 强制搜索：只有意图词，无其他内容，如“唐忠汉 苏州"
		if is_brute_search:
			pthreshold, tthreshold = 0.1, 0.1
			ts_projet_map, ts_pmedia_map, weighted_mids = text_search2(query_tag_pairs,
			                                                           query_intent,
			                                                           clip_search_text,
			                                                           term_weight_dict,
			                                                           pthreshold=pthreshold,
						                                               tthreshold=tthreshold,
						                                               is_brute_search=is_brute_search,
						                                               topk=topk
			                                                           )

		else:
			ts_projet_map, ts_pmedia_map, weighted_mids = text_search2(query_tag_pairs,
			                                                           query_intent,
			                                                           clip_search_text,
			                                                           term_weight_dict,
			                                                           pthreshold=pthreshold,
			                                                           tthreshold=tthreshold,
			                                                           is_brute_search=is_brute_search,
			                                                           topk=topk
			                                                           )


		num_text_recalls = len(ts_pmedia_map)
		# 文本文本搜索：视觉补充召回
		if num_text_recalls < topk:
			print(" ==>>>>  ", "   文本召回不足：视觉召回补充")

			# 文召回为空时 或 无意图词
			if num_text_recalls == 0 and not query_intent:
				print("补充召回：纯视觉召回。")
				vision_recall_dict = vision_search(text, query_intent, query_sentiment, [],
				                                   threshold=0.18,
				                                   query_filter=False,
				                                   topk=topk)

			else:
				print("补充召回：视觉补充召回。")
				vision_recall_dict = vision_search(text, query_intent, query_sentiment, query_tag_pairs,
				                                   threshold=0.18,
				                                   query_filter=True,
				                                   topk=topk)
		# 将文本搜索和视觉搜索合并
		text_recall_dict = get_recall_dict(ts_projet_map, ts_pmedia_map, vision_recall_dict, weighted_mids)
		text_recall_dict = norm(text_recall_dict)

		print("ts_projet_map: ", ts_projet_map)
		print("ts_pmedia_map: ", ts_pmedia_map)
		print("vision_recall_dict: ", vision_recall_dict)


	else:
		print(" ---------||||  视觉搜索  ")
		vision_recall_dict = vision_search(text, query_intent, query_sentiment, query_tag_pairs,
		                                   threshold=0.18, topk=topk, query_filter=False)
		vision_recall_dict = norm(vision_recall_dict)

	return text_recall_dict, vision_recall_dict



def items2candidates(item_ids: List, scores: List, CLICK_SEQS: List = None):
	""""""

	df = items2df(item_ids, IMAGE_DF)
	click_seqs_dict = Counter(CLICK_SEQS) if CLICK_SEQS else {}
	candidates = []
	if not len(df):
		return []

	for score, row in zip(scores, df.itertuples()):
		score = "%.4f" % score
		mid = row.image_id
		url = row.url
		pid = row.project_id
		title = row.title
		category = row.category
		view_num = row.view_num
		# 更新点击数
		view_num += click_seqs_dict.get(mid, 0)

		collect_num = row.collect_num
		publish_time = row.publish_time
		if publish_time:
			publish_time = publish_time.split()[0]
		author = '测试'

		candidates.append([score, mid, pid, url, title, author, category, view_num, collect_num, publish_time])

	return candidates



def decimal_truncation(s, num:int=2):
	if s:
		return f"%.{num}f" % s
	return s

def items2rank_detail(LOG_DICT: Dict, item_ids: List, scores: List, CLICK_SEQS: List = None):

	df = items2df(item_ids, IMAGE_DF)
	click_seqs_dict = Counter(CLICK_SEQS) if CLICK_SEQS else {}
	candidates = []
	if not len(df):
		return []

	for score, row in zip(scores, df.itertuples()):
		score = "%.2f" % score
		mid = row.image_id
		url = row.url
		pid = row.project_id
		title = row.title
		category = row.category
		view_num = row.view_num
		view_num += click_seqs_dict.get(mid, 0)

		collect_num = row.collect_num
		publish_time = row.publish_time
		if publish_time:
			publish_time = publish_time.split()[0]

		author = ''

		details = []
		month2now = datespan2now(publish_time)

		log_dict = LOG_DICT.get(mid)
		q2pt_score = decimal_truncation(log_dict.get('q2pt_score')) # 标题匹配
		q2ptw_score = decimal_truncation(log_dict.get('q2ptw_score')) # 标题匹配 + 词权重
		q2pm_score = decimal_truncation(log_dict.get('q2pm_score')) # 案例中图片匹配
		q2m_score = decimal_truncation(log_dict.get('q2m_score')) # 图片匹配
		similarity = decimal_truncation(log_dict.get('similarity')) # 相关度

		popular = decimal_truncation(log_dict.get('popular')) # 流行度
		aesthetic = decimal_truncation(log_dict.get('aesthetic')) # 美学分
		interest = decimal_truncation(log_dict.get('interest')) # 兴趣分

		rank = decimal_truncation(log_dict.get('rank')) # 融合后排序

		details = [q2pt_score, q2ptw_score, q2pm_score, q2m_score,
		            similarity, popular, aesthetic, interest, rank ]


		details = [ score, mid, pid, url, title, author, category, view_num, collect_num, month2now] + details


		candidates.append(details)

	return candidates










if __name__ == '__main__':
	print()

	text = "唐忠汉样板间"
	# text = "客厅"
	text = '梁志天客厅'
	text = '海景房'
	# recall_mids, recall_scores = RECALL(text, threshold=0.5, topk=100)
	# print("recall_mids, recall_scores, weighted_mids: ", dict(zip(recall_mids, recall_scores)), )
	# print(items2candidates(recall_mids, recall_scores))
	# print(LOG_DICT)

	print(RECALL2(text=text, topk=25))
