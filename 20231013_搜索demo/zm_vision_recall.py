#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-09-22 17:17
# @Author   : NING MEI
# @Desc     :


import numpy as np
from typing import List
from utils import norm, get_trt_h14_txt_emb, similar_by_vearch
from process import query_process, intent_match, query2wordtags


def query_match_images(query: str, threshold: float = 0.18, topk: int = 100):
	""""""
	query_emb = get_trt_h14_txt_emb(query)
	resp = similar_by_vearch(query_emb, filter_terms=None, threshold=threshold, topk=topk)
	hits = resp.get("hits", {}).get("hits", [])
	cont_recall_dict = dict([int(hit.get("_id", 0)), hit.get("_score", 0)] for hit in hits)

	return cont_recall_dict


def vision_search(query: str, query_intent:List, query_sentiment: bool, query_tag_pairs: List= None,
                  threshold:float=0.18, query_filter: bool=True, topk: int = 100):
	""""""
	text_prefix = "高级感"
	query_content = query
	if not query_filter:
		print(f"直接搜索：{query_content}")

	else:
		if query_tag_pairs:
			query_content = " ".join([w for (w, t) in query_tag_pairs if w not in list(map(lambda x: x[0], query_intent))])


	if query_sentiment:
		if text_prefix not in query:
			# query_content = text_prefix + query_content
			if not query_content:
				query_content = query
			else:
				query_content = text_prefix + query_content

	print(" ****** 视觉搜索query_content: ", query_content)

	cont_recall_dict = query_match_images(query_content, threshold=threshold, topk=topk)

	# print("cont_recall_dict: ", cont_recall_dict)

	# cont_recall_dict = norm(cont_recall_dict)

	return cont_recall_dict


if __name__ == '__main__':
	text = "旋转楼梯"
	query_tag_pairs = query2wordtags(query=text, ner_to_seg=True)
	query_content, query_intent, query_sentiment, term_weight_dict = query_process(query=text,
	                                                                               query_tags=query_tag_pairs)
	res = vision_search(text, query_intent, query_sentiment, query_tag_pairs, topk=100, query_filter=False)
	print("res: ", res)
