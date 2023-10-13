#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-09-21 18:15
# @Author   : NING MEI
# @Desc     :


""" 召回结果排序 """

import numpy as np
from config  import *
from utils import norm
from typing import List, Dict
from ctr_infer import ctr_rank
from quality_infer import quality_rank, get_popular_aesthetic_score
from zm_interest_infer import interests_match
from meta_infer import meta_predict


def recall2ctr_rank(text, recall_mids, CLICK_SEQS):
	# # 点击行为预测
	ctr_dict = ctr_rank(text, recall_mids, CLICK_SEQS, mothod='din')
	# print("ctr_dict: ", ctr_dict)
	if ctr_dict:
		ctr_dict = norm(ctr_dict)

	return ctr_dict


def recall2interests_rank(recall_mids, CLICK_SEQS, TIMESTAMPS):
	## 兴趣聚类
	interest_dict = interests_match(recall_mids, CLICK_SEQS, TIMESTAMPS)
	# print("interest_dict: ", interest_dict)
	if interest_dict:
		interest_dict = norm(interest_dict)

	return interest_dict


def recall2quality_rank(recall_mids, CLICK_SEQS):
	## 流行度、质量
	popular_dict = quality_rank(recall_mids, CLICK_SEQS)
	# print("popular_dict: ", popular_dict)
	if popular_dict:
		popular_dict = norm(popular_dict)

	return popular_dict


def RECALL2RANK(text: str, recall_mids: List, recall_scores: List, weighted_ids: List, CLICK_SEQS: List, TIMESTAMPS: List):
	""""""

	ctr_dict = recall2ctr_rank(text, recall_mids, CLICK_SEQS)
	interest_dict = recall2interests_rank(recall_mids, CLICK_SEQS, TIMESTAMPS)
	quality_dict = recall2quality_rank(recall_mids, CLICK_SEQS)

	print("意图权重：", weighted_ids)

	meta_scores, rank_dict = [], {}
	recall_weight, ctr_weight, interest_weight, quality_weight = 0.25, 0.2, 0.3, 0.25
	# print("interest_dict, ctr_dict : ", interest_dict, ctr_dict)

	for mid, rscore in zip(recall_mids, recall_scores):
		cscore = ctr_dict.get(mid, 0)
		iscore = interest_dict.get(mid, 0)
		qscore = quality_dict.get(mid, 0)

		if mid in weighted_ids:
			rscore = min(1.5 * rscore, 1.0)

		rank_score = rscore * recall_weight + \
		             cscore * ctr_weight + \
		             iscore * interest_weight + \
		             qscore * quality_weight
		meta_scores.append(rank_score)
		rank_dict[mid] = rank_score

	meta_scores = np.array(meta_scores)
	rank_idxes = np.argsort(-meta_scores)
	meta_scores = meta_scores[rank_idxes].tolist()
	rank_mids = np.array(recall_mids)[rank_idxes].tolist()
	return rank_mids, meta_scores, rank_idxes


def RECALL2RANK2(text: str, recall_mids: List, recall_scores: List, weighted_ids: List, CLICK_SEQS: List,
                TIMESTAMPS: List):
	""""""

	global LOG_DICT

	interest_dict = recall2interests_rank(recall_mids, CLICK_SEQS, TIMESTAMPS)

	# 临时分数
	tmp_dict = get_popular_aesthetic_score(recall_mids, CLICK_SEQS)
	print("意图权重：", weighted_ids)

	meta_scores, rank_dict = [], {}
	meta_weight, interest_weight = 0.7, 0.3
	for mid, rscore in zip(recall_mids, recall_scores):
		iscore = interest_dict.get(mid, 0)

		popular_aesthetic_item_dict = tmp_dict.get(mid, {})
		popular_score = popular_aesthetic_item_dict.get('popular_score', 9.759064)
		aesthetic_score = popular_aesthetic_item_dict.get('aesthetic_score', 5.025700)

		rank_score = meta_predict(rscore, aesthetic_score, popular_score)

		rank_score = rank_score * meta_weight + iscore * interest_weight
		if mid in weighted_ids:
			rank_score = min(1.5 * rank_score, 1.0)

		meta_scores.append(rank_score)
		rank_dict[mid] = rank_score

		# 最终排序分数
		LOG_DICT[mid].update({'popular': popular_score, 'aesthetic': aesthetic_score, 'interest': iscore, 'rank': rank_score})


	meta_scores = np.array(meta_scores)
	rank_idxes = np.argsort(-meta_scores)
	meta_scores = meta_scores[rank_idxes].tolist()
	rank_mids = np.array(recall_mids)[rank_idxes].tolist()
	return rank_mids, meta_scores, rank_idxes


def testme():
	""" 注意：图片编号不同可能导致失败 """
	text = "唐忠汉样板间"
	candidates = [['1.0000', 61175374, 122464973, 'https://image.linggan.znzmo.com/case/img/ac1c7e285d34db62f4103b3fa9b84366213b839c.jpg?x-oss-process=image/auto-orient,1/resize,m_fill,w_300,h_461,limit_0', '97㎡厦门春江郦城97户型复式样板房', '', '样板间', 2, 0, '2017-06-23'], ['0.7956', 16354063, 12873096, 'https://image5.znztv.com/40854a16-a550-11ec-9402-00163e2b40d5.png?x-oss-process=image/auto-orient,1/resize,m_fill,w_437,h_300,limit_0', '别墅丨何应清设计形之万设计', '', '商业综合体', 29, 1, '2019-02-12'], ['0.7000', 27659357, 17574407, 'https://image.linggan.znzmo.com/case/img/6af9e5488b5cc77a67a02845fb9cbb1c5de337f8.jpeg?x-oss-process=image/auto-orient,1/resize,m_fill,w_450,h_300,limit_0', '唐忠汉丨样板间丨看这两个别墅样板房丨 纯粹又自然的高级灰格调', '', '样板间', 432, 32, '2018-07-21'], ['0.4322', 27659301, 17574407, 'https://image.linggan.znzmo.com/case/img/9bd1e749d3af4b02aea64e75ef7cb2786a5c0187.jpeg?x-oss-process=image/auto-orient,1/resize,m_fill,w_454,h_300,limit_0', '唐忠汉丨样板间丨看这两个别墅样板房丨 纯粹又自然的高级灰格调', '', '样板间', 432, 32, '2018-07-21'], ['0.3441', 23917964, 15339361, 'https://image5.znztv.com/a33fd248-9d9e-11ec-90ce-00163e2b40d5.png?x-oss-process=image/auto-orient,1/resize,m_fill,w_420,h_300,limit_0', '唐忠汉设计 | 武汉万达·御湖汉印样板间2套', '', '样板间', 2116, 69, '2020-10-07'], ['0.2991', 27659296, 17574407, 'https://image.linggan.znzmo.com/case/img/63ca4abd9f9db3f29ab7fe0cb145471ab37e54ce.jpeg?x-oss-process=image/auto-orient,1/resize,m_fill,w_532,h_300,limit_0', '唐忠汉丨样板间丨看这两个别墅样板房丨 纯粹又自然的高级灰格调', '', '样板间', 432, 32, '2018-07-21'], ['0.2897', 27659361, 17574407, 'https://image.linggan.znzmo.com/case/img/6a6841107c723ef370d2c4703766b9ce8b44e2ba.jpeg?x-oss-process=image/auto-orient,1/resize,m_fill,w_461,h_300,limit_0', '唐忠汉丨样板间丨看这两个别墅样板房丨 纯粹又自然的高级灰格调', '', '样板间', 432, 32, '2018-07-21'], ['0.2595', 60761810, 122352853, 'https://image8.znztv.com/2cb517e0-ac2b-11ed-a082-00163e25d88c.png?x-oss-process=image/auto-orient,1/resize,m_fill,w_300,h_309,limit_0', '雅居乐盛京雅府样板间 | 近境制作唐忠汉丨中国沈阳', '', '样板间', 623, 41, '2022-01-26'], ['0.1819', 60761846, 122352853, 'https://image8.znztv.com/60a0bb2c-ac2b-11ed-a42d-00163e243155.png?x-oss-process=image/auto-orient,1/resize,m_fill,w_357,h_300,limit_0', '雅居乐盛京雅府样板间 | 近境制作唐忠汉丨中国沈阳', '', '样板间', 623, 41, '2022-01-26'], ['0.1751', 50490030, 15339440, 'https://image.linggan.znzmo.com/case/img/936a220179495ca1167c172cd4db7ac0b8921a5d.jpg?x-oss-process=image/auto-orient,1/resize,m_fill,w_421,h_300,limit_0', '唐忠汉丨样板间丨近境制作--亚新紫藤样板房160户型', '', '样板间', 1193, 51, '2020-08-01'], ['0.1656', 27659340, 17574407, 'https://image.linggan.znzmo.com/case/img/a10f477b65f54ce6a0ed985fb7c3d52cf7afb798.jpeg?x-oss-process=image/auto-orient,1/resize,m_fill,w_457,h_300,limit_0', '唐忠汉丨样板间丨看这两个别墅样板房丨 纯粹又自然的高级灰格调', '', '样板间', 432, 32, '2018-07-21'], ['0.1121', 34707395, 110197863, 'https://image8.znztv.com/37aaa6b4-a9fc-11ed-97be-00163e25d88c.png?x-oss-process=image/auto-orient,1/resize,m_fill,w_300,h_303,limit_0', '唐忠汉 | 成都·中海浣云居上叠样板间', '', '样板间', 5675, 258, '2021-11-23'], ['0.0895', 38460812, 111565035, 'https://image8.znztv.com/14c037ba-a94b-11ed-bcca-00163e25d88c.png?x-oss-process=image/auto-orient,1/resize,m_fill,w_300,h_441,limit_0', '唐忠汉丨近境制作--北京珠江·天樾书院样板间[完整版]', '', '样板间', 829, 51, '2020-12-23'], ['0.0664', 48573896, 115507600, 'https://image.linggan.znzmo.com/case/img/4746cfa970934ff2b680e1fbbc73067cc2af250f.jpeg?x-oss-process=image/auto-orient,1/resize,m_fill,w_300,h_431,limit_0', '新作丨唐忠汉 × 俊峰地产样板间：精神之境！', '', '样板间', 10767, 480, '2023-04-12'], ['0.0524', 49224930, 116485948, 'https://image.linggan.znzmo.com/case/img/b2a754bb4db0d2285cf5de76a7063d18e862f8ab.png?x-oss-process=image/auto-orient,1/resize,m_fill,w_300,h_450,limit_0', '样板间丨唐忠汉新作 ｜ 极简质朴设计', '', '样板间', 15434, 340, '2021-11-24'], ['0.0490', 60761843, 122352853, 'https://image8.znztv.com/5d400a00-ac2b-11ed-b326-00163e260e62.png?x-oss-process=image/auto-orient,1/resize,m_fill,w_300,h_450,limit_0', '雅居乐盛京雅府样板间 | 近境制作唐忠汉丨中国沈阳', '', '样板间', 623, 41, '2022-01-26'], ['0.0415', 48573899, 115507600, 'https://image.linggan.znzmo.com/case/img/ab51bcf26cc8335a87cc63b96071b059d76419ae.jpeg?x-oss-process=image/auto-orient,1/resize,m_fill,w_300,h_431,limit_0', '新作丨唐忠汉 × 俊峰地产样板间：精神之境！', '', '样板间', 10767, 480, '2023-04-12'], ['0.0274', 60761844, 122352853, 'https://image8.znztv.com/5eb0cf32-ac2b-11ed-a17b-00163e1ee128.png?x-oss-process=image/auto-orient,1/resize,m_fill,w_367,h_300,limit_0', '雅居乐盛京雅府样板间 | 近境制作唐忠汉丨中国沈阳', '', '样板间', 623, 41, '2022-01-26'], ['0.0041', 34707389, 110197863, 'https://image8.znztv.com/1db67ac6-a9fc-11ed-97a8-00163e25d88c.png?x-oss-process=image/auto-orient,1/resize,m_fill,w_300,h_388,limit_0', '唐忠汉 | 成都·中海浣云居上叠样板间', '', '样板间', 5675, 258, '2021-11-23'], ['0.0000', 27659366, 17574407, 'https://image.linggan.znzmo.com/case/img/27c01881b8d9956546735ecb976cd11a2d68881b.jpeg?x-oss-process=image/auto-orient,1/resize,m_fill,w_451,h_300,limit_0', '唐忠汉丨样板间丨看这两个别墅样板房丨 纯粹又自然的高级灰格调', '', '样板间', 432, 32, '2018-07-21']]

	recall_dict = {61175374: 0.9999999925985592, 16354063: 0.7956236844167419, 27659357: 0.6999999971187384, 27659301: 0.43217165628871435, 23917964: 0.3441412053028007, 27659296: 0.29908568550670256, 27659361: 0.2896560595141763, 60761810: 0.259453606749515, 60761846: 0.18185314730557833, 50490030: 0.17514082327119523, 27659340: 0.16556436250703283, 34707395: 0.11213024455748799, 38460812: 0.08945500587564653, 48573896: 0.06640838685033945, 49224930: 0.05241099730390489, 60761843: 0.04896381490195644, 48573899: 0.041484257718702754, 60761844: 0.027442646004202344, 34707389: 0.004118243068811742, 27659366: 0.0}

	CLICK_SEQS = [61175374, 27659357]
	TIMESTAMPS = [1695293034.1374671, 1695293046.2660255]
	weighted_ids = []

	mids = list(recall_dict.keys())
	scores = list(map(recall_dict.get, mids))
	# recall2ctr_rank(text, candidates, CLICK_SEQS)
	res = RECALL2RANK(text, mids, scores, weighted_ids, CLICK_SEQS, TIMESTAMPS)
	print("排序：", res[0])




if __name__ == '__main__':
	print()
	testme()
