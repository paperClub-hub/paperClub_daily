#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-09-18 18:32
# @Author   : NING MEI
# @Desc     :



""" 流行度预测 """

import numpy as np
from typing import List
from utils import items2df
from datetime import datetime
from collections import Counter
from config import *

# 导入数据
# from zk_data import IMAGE_DF
if USE_ZHUKE:
	from zk_data import IMAGE_DF
else:
	from zm_data import IMAGE_DF


def str2date(datetime_str):
	if len(datetime_str) > 10:
		date_point = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
	else:
		date_point = datetime.strptime(datetime_str, "%Y-%m-%d")

	return date_point


def date_span(datetime_str: str, init_date_point: str = "1900-1-1 0:00:00"):
	date_point = str2date(datetime_str)
	init_date_point = str2date(init_date_point)
	spans = (date_point - init_date_point)
	return spans.days


def get_score(view: int, collect: int, publish_time: str, h_init: float = 0.0):
	view = int(view)
	collect = int(collect)

	if view > 10882:
		view = 10882
	if collect > 358:
		collect = 358
	if not publish_time:
		# 中位数
		publish_time = '2021-11-01 00:00:00'

	w_view, w_collect = 0.3, 0.7
	value = h_init + view * w_view + collect * w_collect
	alpha = np.log10(max(abs(value), 1))
	span_days = date_span(publish_time)

	beta = 1
	if value > 0:
		return round(alpha + beta * span_days / 6000, 7)
	else:
		beta = 1e-3
		return round(beta * span_days / 6000, 7)


def quality_rank(mids: List, CLICK_SEQS: List = None):
	""""""
	quality_dict = {}
	tdf = items2df(mids, IMAGE_DF)
	click_seqs_dict = Counter(CLICK_SEQS) if CLICK_SEQS else {}
	print("click_seqs_dict: ", click_seqs_dict)

	if len(tdf):
		views = tdf['view_num'].tolist()
		collects = tdf['collect_num'].tolist()
		publish_times = tdf['publish_time'].tolist()

		resmen_score = tdf['resmen_score'].tolist()
		aesthetic_score = list(map(lambda x: x/10, tdf['aesthetic_score'].tolist()))

		# for i, (view, collect, publish_time) in enumerate(zip(views, collects, publish_times)):
		for i, (view, collect, publish_time, rscore, ascore) in enumerate(zip(views, collects, publish_times, resmen_score, aesthetic_score)):
			mid = mids[i]
			# 更新点击量
			view += click_seqs_dict.get(mid, 0)

			# h_init = rscore * 0.2 + ascore * 0.8
			h_init = ascore * 10
			# score = get_score(view, collect, publish_time)
			score = get_score(view, collect, publish_time, h_init=h_init)
			quality_dict[mid] = score

	return quality_dict


def get_popular_aesthetic_score(mids: List, CLICK_SEQS: List = None):
	""" 只获取 热度分分数 和 美学分数 """
	res = {}
	tdf = items2df(mids, IMAGE_DF)
	click_seqs_dict = Counter(CLICK_SEQS) if CLICK_SEQS else {}
	if len(tdf):
		views = tdf['view_num'].tolist()
		collects = tdf['collect_num'].tolist()
		publish_times = tdf['publish_time'].tolist()
		aesthetic_score = tdf['aesthetic_score'].tolist()
		for i, (view, collect, publish_time, ascore) in enumerate(zip(views, collects, publish_times, aesthetic_score)):
			mid = mids[i]
			# 更新点击量
			view += click_seqs_dict.get(mid, 0)
			score = get_score(view, collect, publish_time, h_init=0)
			res[mid] = {"popular_score": score, "aesthetic_score": ascore}

	return res


if __name__ == '__main__':

	recall_mids = [93244, 5466579, 5357379, 5409781]
	d = quality_rank(recall_mids)
	print("d: ", d)