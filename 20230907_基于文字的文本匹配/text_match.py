#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-09-05 17:57
# @Author   : NING MEI
# @Desc     :


from os.path import abspath, dirname, join, exists
from typing import List, Dict, Union
from ordered_set import OrderedSet
import jieba as _jieba
import numpy as np
import pickle
import random
import json
import re

PWD = abspath(dirname(__file__))


class TFIDF:
	def __init__(self):
		self.words = {}
		pwd = abspath(dirname(__file__))
		self.croups_path = join(pwd, "croups.pkl")
		stop_words_path = join(pwd, './stop_words.txt')
		self.STOP_WORDS = self.load_stopwords(stop_words_path)
		self.croups = self.load_croups()
		self.num_docs = len(self.croups)
		self.get_vocab(self.croups)

	def load_stopwords(self, stopword_path):
		spw = [w.strip() for w in open(stopword_path, 'r').readlines()]
		return spw

	def doc2word(self, doc: str):
		""""""
		doc = re.sub(r'\W', ' ', doc)
		doc = doc.replace('丨', '')
		words = [str(w.strip()).lower() for w in _jieba.lcut_for_search(doc) if w.strip() and w not in self.STOP_WORDS]
		del doc
		return words

	def build_croups(self, docs, save: bool = True):
		""" 通过文档统计语料：计算词矩阵 """
		self.num_docs += len(docs)
		for i, doc in enumerate(docs):
			words = self.doc2word(doc)
			# 按序计算每篇文章的词频（TF）
			words_frc = dict([w, words.count(w) / len(words)] for w in set(words))
			self.croups.append(words_frc)
			del words, words_frc, doc

		self.get_vocab(self.croups)
		if save:
			self.save_croups()

	def get_vocab(self, croups: List[Dict]):
		""" 计算每个词在全部文档中的出现频次（统计包含每个词的文档数），用于idf计算 """
		for i, doc_words in enumerate(croups):
			for word in doc_words:
				self.words[word] = self.words.get(word, 0) + 1
				del word
			del doc_words

	def save_croups(self, save_path: str = None):
		""""""
		if not save_path:
			save_path = self.croups_path
		pickle.dump(self.croups, open(save_path, 'wb'))

	def load_croups(self):
		croups = []
		if exists(self.croups_path):
			croups = pickle.loads(open(self.croups_path, 'rb').read())

		return croups

	def _get_idf_score(self, word):
		""" 计算词idf """
		return np.log(self.num_docs / (self.words.get(word, 0) + 1))

	def get_tfidf_score(self, index: int, word: str):
		score = 0.0
		tf_map = self.croups[index]
		if word in tf_map:
			tf = tf_map.get(word)
			idf = self._get_idf_score(word)
			score = tf * idf

		del tf_map
		return score

	def get_scores(self, words: List):
		""" 计算多个词的 tfidf分数 """

		if isinstance(words, str):
			words = [words]

		score = np.zeros(self.num_docs)
		for word in words:
			for i in range(self.num_docs):
				score[i] += self.get_tfidf_score(i, word)

		return score


class BM25:
	def __init__(self):
		self.words = {}
		pwd = abspath(dirname(__file__))
		self.croups_path = join(pwd, "croups.pkl")
		stop_words_path = join(pwd, './stop_words.txt')
		self.STOP_WORDS = self.load_stopwords(stop_words_path)
		self.croups = self.load_croups()
		self.num_docs = len(self.croups)
		self.get_vocab(self.croups)
		self.agv_doc_len = np.mean([len(d) for d in self.croups])
		self.average_idf = np.mean([v for _, v in self.words.items()])
		self.k = 1.5
		self.b = 0.75
		self.epsilon = 0.25

	def load_stopwords(self, stopword_path):
		spw = [w.strip() for w in open(stopword_path, 'r').readlines()]
		return spw

	def doc2word(self, doc: str):
		""""""
		doc = re.sub(r'\W', ' ', doc)
		doc = doc.replace('丨', '')
		words = [str(w.strip()).lower() for w in _jieba.lcut_for_search(doc) if w.strip() and w not in self.STOP_WORDS]
		del doc
		return words

	def build_croups(self, docs, save: bool = True):
		""" 通过文档统计语料：计算词矩阵 """
		self.num_docs += len(docs)
		for i, doc in enumerate(docs):
			words = self.doc2word(doc)
			words_tdf = dict([w, words.count(w)] for w in set(words))
			self.croups.append(words_tdf)
			del words, words_tdf, doc

		self.get_vocab(self.croups)
		if save:
			self.save_croups()

	def get_vocab(self, croups: List[Dict]):
		""" 计算每个词在全部文档中的出现频次（统计包含每个词的文档数），用于idf计算 """
		for i, doc_words in enumerate(croups):
			for word in doc_words:
				self.words[word] = self.words.get(word, 0) + 1
				del word
			del doc_words

	def save_croups(self, save_path: str = None):
		""""""
		if not save_path:
			save_path = self.croups_path
		pickle.dump(self.croups, open(save_path, 'wb'))

	def load_croups(self):
		croups = []
		if exists(self.croups_path):
			croups = pickle.loads(open(self.croups_path, 'rb').read())

		return croups

	def _cal_idf(self, word):
		idf = np.log(1 + (self.num_docs - self.words.get(word, 0) + 0.5) / (self.words.get(word) + 0.5))
		if idf < 0:
			idf = self.epsilon * self.average_idf
		return idf

	def get_paris_eles(self, lst, num_elements=2):
		if num_elements > len(lst):
			return None

		result = []
		while len(result) < (len(lst) * (len(lst) - 1) / num_elements):
			elements = sorted(random.sample(lst, num_elements))
			if elements not in result:
				result.append(elements)

		return result

	def _get_l2_score(self, a: Union[List, np.ndarray]):
		""" 词编辑距离 """
		dist = 0
		for i in range(len(a) - 1):
			x1 = a[i]
			x2 = a[i + 1]
			if x1 != x2:
				d = 1 / abs(x2 - x1) ** 2
			else:
				d = 0
			dist += d

		return dist


	def get_tpi(self, query: List, lst: List):
		""" 词编辑距离 """
		idxes = [lst.index(w) for w in query if w in lst]
		# 增加覆盖度
		coverage_rate = len(idxes) / len(query)
		return self._get_l2_score(idxes) + coverage_rate

	def get_bm25_score(self, index, word):
		""" 计算bm25 """
		tf_map = self.croups[index]
		tfv = tf_map.get(word, 0)
		if tfv == 0:
			return 0.0

		idf = self._cal_idf(word)
		bm25_score = idf * (
					(tfv * (self.k + 1)) / (tfv + self.k * (1 - self.b + self.b * (len(tf_map) / self.agv_doc_len))))
		del tf_map, tfv, idf
		return bm25_score

	def get_scores(self, words: List):
		if isinstance(words, str):
			words = [words]

		score = np.zeros(self.num_docs)
		for idx, word in enumerate(words):
			for i in range(self.num_docs):
				score[i] += self.get_bm25_score(i, word)
				# 增加词编辑距离
				if len(words) > 1 and idx == 0:
					tpi_score = self.get_tpi(words, list(self.croups[i].keys()))
					score[i] += tpi_score

		# 计算多个词编辑距离加和
		# for idx in range(self.num_docs):
		# 	tpi_score = self.get_tpi(words, list(self.croups[idx].keys()))
		# 	score[idx] += tpi_score

		return score





if __name__ == '__main__':
	import time

	docs = ['样板间丨唐忠汉新作',
	        '现代轻奢样板间',
	        '样板间丨唐忠汉新作丨沉淀 · 本我',
	        ]

	# tfidf = TFIDF()
	# t1 = time.time()
	# # tfidf.build_croups(docs, save=False)
	# scores = tfidf.get_scores(['你好'])
	# print(scores)
	# print("耗时：", time.time() - t1)

	bm25 = BM25()
	t2 = time.time()
	topk = 10
	ws = ['苏州', '博物馆']
	ws = ['唐忠汉', '样板间', '近境']




	scores = bm25.get_scores(ws)
	idx = np.argsort(scores)[::-1][:topk]
	print(scores[idx], idx)

	# import pandas as pd
	# df = pd.read_parquet("/data/1_qunosen/project/res/rank/zhimo_rank/data/zm_media_data.parquet")
	# df = df[['project_id', 'author', 'title', 'country', 'category']]
	# df.drop_duplicates(inplace=True)
	# tdf = df.iloc[idx.tolist()]
	# print(tdf)
	# print("耗时：", time.time() - t2)
