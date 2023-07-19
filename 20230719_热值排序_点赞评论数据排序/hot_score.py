#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-07-17 8:57
# @Author   : NING MEI
# @Desc     :

import time
import math
import numpy as np
import pandas as pd
from datetime import datetime

def decay(x, A, b):
	""" 衰减分数 """
	return A * np.exp(-b * x)


def exponential_decay(t, init=0.8, m=300, finish=0.2):

	alpha = np.log(init / finish) / m
	l = - np.log(init) / alpha
	decay = np.exp(-alpha * (t + l))

	return decay



class Pareto:
	"""Pareto算法
	用法：
	   pareto = Pareto(100, 25)
	   pareto.transform(20)
	"""

	def __init__(self, max_value: float = 0, eighty_percent_level: float = 1, minimum_threshold: float = 0):
		""""""
		self.max_value = max_value
		self.eighty_percent_level = eighty_percent_level
		self.minimum_threshold = minimum_threshold

	def transform(self, value: float):
		""""""
		if value < self.minimum_threshold:
			return 0
		alpha = math.log(5) / self.eighty_percent_level
		exp = math.exp(-alpha * value)

		return self.max_value * (1 - exp)



class ItemScoring():
	""" 正向打分 """

	def diff_month(self, x):
		""" 距离当前的月份 """
		now = datetime.now()
		now_year, now_month = now.year, now.month

		if isinstance(x, pd._libs.tslibs.timestamps.Timestamp):
			query_year, query_month = x.year, x.month
		else:
			query = datetime.strptime(x, '%Y-%m-%d')
			query_year, query_month = query.year, query.month

		months = (now_year - query_year) * 12 + (now_month - query_month)

		return months

	def diff_day(self, datetime_str: str, point_date: str = '1970-1-1'):
		""" reddit 日期 day差值 """

		format = '%Y-%m-%d'
		if not point_date:
			point_date = datetime.now()

		if isinstance(point_date, str):
			point_date = datetime.strptime(point_date, format)

		date_time = datetime.strptime(datetime_str, format)
		diff_days = (date_time - point_date).days

		return diff_days

	def pareto_dist(self, pareto_func, x):
		""" 帕累托转换 """
		return pareto_func.transform(x)

	def stamp2date(self, timestamp):
		""" 时间戳转日期 """
		time_format = "%Y-%m-%d %H:%M:%S"
		time_local = time.localtime(timestamp)
		new_date = time.strftime(time_format, time_local)
		return new_date

	def hackernews_scoring(self, h_init, h_interact=0, item_month_age=0, h_weight=0):
		""" Hacker News 分值计算 """
		gravity = 1.8
		return ((h_init + (h_interact + 2)) / pow((item_month_age + 2), gravity)) + h_weight

	def reddit_scoring(self, h_init, ups, downs=0, item_day_age=0, h_weight=0):
		""" reddit 分值计算 """

		score = h_init + ups - downs + h_weight
		order = np.log10(max(abs(score), 1))
		sign = 1 if score > 0 else -1 if score < 0 else 0
		return round(order + sign * item_day_age / 45000, 7)

	def __init__(self, zhuke_data):
		self.click_weight = 0.3
		self.collection_weight = 0.7

		self.data = zhuke_data
		self.data['month2now'] = self.data['publish_time'].apply(lambda x: self.diff_month(x))
		self.data['dayspan'] = self.data['publish_time'].apply(lambda x: self.diff_day(x))
		self.max_date_span = self.data['month2now'].max()
		self.median_date_span = self.data['month2now'].median()
		self.max_day_span = self.data['dayspan'].max()
		self.median_day_span = self.data['dayspan'].median()
		self.max_aesthetics_score = self.data['score'].max()
		self.median_aesthetics_score = self.data['score'].median()
		self.max_num_clicks = self.data['num_clicks'].max()
		self.median_num_clicks = self.data['num_clicks'].median()
		self.max_num_collects =self.data['num_collects'].max()
		self.median_num_collects = self.data['num_collects'].median()
		# 帕累托转化
		self.pareto_date = Pareto(self.max_date_span, self.median_date_span)
		self.pareto_day = Pareto(self.max_day_span, self.median_day_span)
		self.pareto_aesthetics = Pareto(self.max_aesthetics_score, self.median_aesthetics_score)
		self.pareto_click = Pareto(self.max_num_clicks, self.median_num_clicks)
		self.pareto_collect = Pareto(self.max_num_collects, self.median_num_collects)


	def get_hackernews_score(self, x):

		aesthetics_score = float(x['score'])
		num_click = float(x['num_clicks'])
		num_collection = float(x['num_clicks'])
		publish_span = float(x['month2now'])

		# 用美学分做初始值
		h_init = self.pareto_aesthetics.transform(aesthetics_score)
		click = self.pareto_click.transform(num_click)
		fav = self.pareto_collect.transform(num_collection)
		# 交互数
		h_interact = h_init + click * self.click_weight + fav * self.collection_weight

		# 时间衰减因子（利用图片发布的月份数）
		item_date = self.pareto_date.transform(publish_span)

		return self.hackernews_scoring(h_init, h_interact, item_date)


	def get_reddit_score(self, x):
		aesthetics_score = float(x['score'])
		num_click = float(x['num_clicks'])
		num_collection = float(x['num_clicks'])
		day_span = int(x['dayspan'])

		h_init = self.pareto_aesthetics.transform(aesthetics_score)
		click = self.pareto_click.transform(num_click)
		fav = self.pareto_collect.transform(num_collection)
		item_date = self.pareto_day.transform(day_span)
		h_interact = h_init + click * self.click_weight + fav * self.collection_weight

		return self.reddit_scoring(h_init=h_init, ups=h_interact, downs=0, item_day_age=item_date)


	def item_score(self):
		self.data['item_score'] = self.data.apply(lambda x: self.get_hackernews_score(x), axis=1)
		# self.data['item_score2'] = self.data.apply(lambda x: self.get_reddit_score(x), axis=1)
		data = self.data
		return data



zhuke_data = pd.read_parquet("test.parquet")
zhuke_data['click_collect'] = zhuke_data.apply(lambda x: x.num_collects / x.num_clicks, axis=1) # 看藏比
zhuke_data['num_clicks'] = zhuke_data['num_clicks'].apply(lambda x: np.log10(int(x+1)))
zhuke_data['num_collects'] = zhuke_data['num_collects'].apply(lambda x: np.log10(int(x+1)))
ScoreFunc = ItemScoring(zhuke_data)
zhuke_data = ScoreFunc.item_score()
zhuke_data