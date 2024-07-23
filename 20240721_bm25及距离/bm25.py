#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2024-03-28 17:27
# @Author   : NING MEI
# @Desc     :


import paddle
paddle.set_device("cpu")
import os


import re
import jieba
import torch
import random
import pickle
import langid
import numpy as np
import pandas as pd
from tqdm import tqdm
from paddlenlp import Taskflow
from ordered_set import OrderedSet
from collections import OrderedDict
from utils import get_text_embeddings
from typing import List, Dict, Union
from os.path import abspath, dirname, join, exists


""" BM25文本搜索 """

def model_init():
	pwd = abspath(dirname(__file__))
	path_dir = join(pwd, "data/config")
	jieba.load_userdict(f"{path_dir}/zhuke_jieba.dict")
	jieba.load_userdict(f"{path_dir}/my_jieba_dict.txt")
	device_id = 0
	user_dict = join(path_dir, "user_dict.txt")
	ner = Taskflow('ner', user_dict=user_dict, entity_only=True)
	seg = Taskflow("word_segmentation", user_dict=user_dict, mode="base")
	return ner, seg


# ner词性标签
FETCH_TAGS = [
    '风格',
	'团队人物',
	'家装品牌',
	'人物类_实体',
	'人物类_概念',
	'作品类_实体',
	'作品类_概念',
	'组织机构类',
	'组织机构类_概念',
	'组织机构类_企事业单位',
	'组织机构类_企事业单位_概念',
	'组织机构类_国家机关',
	'组织机构类_国家机关_概念',
	'组织机构类_体育组织机构',
	'组织机构类_体育组织机构_概念',
	'组织机构类_军事组织机构',
	'组织机构类_军事组织机构_概念',
	'组织机构类_医疗卫生机构',
	'组织机构类_医疗卫生机构_概念',
	'组织机构类_教育组织机构',
	'组织机构类_教育组织机构_概念',
	'物体类',
	'物体类_概念',
	'物体类_兵器',
	'物体类_化学物质',
	'其他角色类',
	'文化类',
	'文化类_语言文字',
	'文化类_奖项赛事活动',
	'文化类_制度政策协议',
	'文化类_姓氏与人名',
	'生物类',
	'生物类_植物',
	'生物类_动物',
	'品牌名',
	'品牌名_品牌类型',
	'场所类',
	'场所类_概念',
	'场所类_交通场所',
	'场所类_交通场所_概念',
	'场所类_网上场所',
	'场所类_网上场所_概念',
	'位置方位',
	'世界地区类',
	'世界地区类_国家',
	'世界地区类_区划概念',
	'世界地区类_地理概念',
	'饮食类',
	'饮食类_菜品',
	'饮食类_饮品',
	'药物类',
	'药物类_中药',
	'术语类',
	'术语类_术语类型',
	'术语类_符号指标类',
	'术语类_医药学术语',
	'术语类_生物体',
	'疾病损伤类',
	'疾病损伤类_植物病虫害',
	'宇宙类',
	'事件类',
	'时间类',
	'时间类_特殊日',
	'时间类_朝代',
	'时间类_具体时间',
	'时间类_时长',
	'词汇用语',
	'信息资料',
	'信息资料_性别',
	'个性特征',
	'感官特征',
	'场景事件',
	'数量词',
	'数量词_序数词',
	'数量词_单位数量词',
	'修饰词',
	'修饰词_性质',
	'修饰词_类型',
	'外语单词',
	'汉语拼音',
]

WEIGHTED_TAGS = [
	'团队人物',
	'人物类_实体',
	'人物类_概念',
	'家装品牌',
	'品牌名',
	'品牌名_品牌类型',
	'世界地区类',
	'世界地区类_国家',
	'世界地区类_区划概念',
	'世界地区类_地理概念',
	'时间类',
	'时间类_特殊日',
	'时间类_朝代',
	'时间类_具体时间',
]


class BM25:

	""" 文本搜索 """
	def __init__(self, USE_PADDLE: bool=True):
		self.words = {}
		root = abspath(dirname(__file__))
		src_dir = join(root, 'data/config')
		self.use_paddle = USE_PADDLE
		method_id = 'paddle' if self.use_paddle else 'jieba'
		self.croups_path = join(src_dir, f"{method_id}_croups.pkl")
		stop_words_path = join(src_dir, './stop_words.txt')
		self.STOP_WORDS = self.load_stopwords(stop_words_path)
		self.croups = self.load_croups()
		self.num_docs = len(self.croups)
		self.get_vocab(self.croups)
		self.agv_doc_len = np.mean([len(d) for d in self.croups])
		self.average_idf = np.mean([v for _, v in self.words.items()])
		self.k = 1.5
		self.b = 0.75
		self.epsilon = 0.25

	def text_clean(self, text):
		text = re.sub(r'\W', ' ', text).strip()
		text = text.replace('丨', '')
		text = text.upper()
		return text

	def query2words_jiebalcut(self, query):
		"""jieba分词"""
		query = self.text_clean(query)
		words = jieba.lcut(query)
		words = list(filter(lambda x: x.strip() and x not in self.STOP_WORDS, words))
		del query
		return words

	def query2words_jiebalcutforsearch(self, query):
		"""jieba分词"""
		query = self.text_clean(query)
		words = jieba.lcut_for_search(query)
		words = list(filter(lambda x: x.strip() and x not in self.STOP_WORDS, words))
		del query
		return words

	def query2words_paddleseg(self, query):
		"""paddleseg分词"""
		query = self.text_clean(query)
		words = SEG(query)
		words = list(filter(lambda x: x.strip() and x not in self.STOP_WORDS, words))
		return words


	def load_stopwords(self, stopword_path):
		spw = [w.strip() for w in open(stopword_path, 'r').readlines()]
		return spw

	def doc2word(self, doc: str):
		""""""
		if self.use_paddle:
			return self.query2words_paddleseg(doc)
		else:
			return self.query2words_jiebalcutforsearch(doc)

	def build_croups(self, docs: List, save: bool = True):
		""" 通过文档统计语料：计算词矩阵 """
		if isinstance(docs, str):
			docs = [docs]

		self.num_docs += len(docs)
		for i, doc in tqdm(enumerate(docs)):
			# print(f"i={i}, doc={doc}")
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
		return score


	def words2wordstags(self, words: List):
		def tags_filter(res: List):
			res = list(filter(lambda t: len(t[0]) >=2 and t[1] in FETCH_TAGS, res))
			return res

		res = []
		if len(words) > 1:
			ner_res = NER(words)
			for item in ner_res:
				if isinstance(item, list) and len(item) > 0:
					res.append(item[0])
		else:
			res = NER(words)

		del words
		if res:
			res = tags_filter(res)

		return res

	def query2wordtags(self, query: Union[str, List], ner_to_seq:bool=False):
		"""获取词标签"""
		if ner_to_seq:
			if isinstance(query, str):
				query = self.text_clean(query)
				res = NER(query)
			else:
				res = self.words2wordstags(query)
		else:
			if isinstance(query, str):
				words = self.query2words_paddleseg(query) if self.use_paddle else \
					self.query2words_jiebalcut(query)
			else:
				words = query
			res = self.words2wordstags(words)

		return res

	def norm(self, dic: Dict, min_y: float = 0.1):
		values = list(dic.values())
		min_x, max_x = min(values), max(values)
		sigma = max(1 - min_y, 0)
		del values
		return dict([k, min_y + sigma * (v - min_x) / (max_x - min_x + 1e-10)] for k, v in dic.items())

	def words2tsearch(self, words: List, threshold:float=0.5, topk: int=100, query_intent:List=None):
		""" 搜索 """
		ts_dict = OrderedDict()
		scores = self.get_scores(words)
		idx = np.argsort(-scores)[: topk]
		res_dict = dict(zip(idx, scores[idx]))
		res_dict_norm = self.norm(res_dict)

		for i, score in zip(idx, scores[idx]):
			score_norm = res_dict_norm.get(i)
			# 截断处理
			if score_norm > threshold:
				# ts_dict[i] = score
				ts_dict[i] = score_norm # 归一化分数

		del scores, idx, res_dict
		return ts_dict


	def term_weight(self, words: List, query:str=None):
		if isinstance(words, List) and len(words) == 1:
			return np.array([1.0])

		if not query: query = " ".join(words)
		embs = get_text_embeddings(words + [query], method='bce_embedding')
		query_vector = torch.tensor(np.array([embs[-1]]))
		words_vector = torch.tensor(np.array(embs[:-1]))
		weights = torch.nn.functional.softmax(torch.matmul(query_vector, words_vector.t()), dim=-1)
		weights = weights / weights.sum()
		weights = weights.numpy().squeeze(0)
		del embs, query_vector, words_vector
		return weights

	def key_terms(self, query: str, words: List, topk: int = 5):
		""" 截断 """
		tags = self.query2wordtags(query)
		# print("tags: ", tags)
		tags = dict([t[0], t[1]] for t in tags if t[1] in WEIGHTED_TAGS )
		print("tags: ", tags)

		weights = self.term_weight(words, query)
		trunc_idx = np.argsort(-weights)[:topk*2]
		trunc_words = np.array(words)[trunc_idx]
		trunc_scores = weights[trunc_idx]
		weight_dict = {}
		for w, s in zip(trunc_words, trunc_scores):
			weight_dict[w] = max(weight_dict.get(w, 0), s)

		# print("weight_dict: ", weight_dict, "tags: ", tags)
		res = [[w, weight_dict.get(w), tags[w]] for w in list(OrderedSet([w for w in trunc_words if w in tags]))[:topk]]

		return res


	# def query2tsearch(self, query: str, DF, threshold:float=0.5, topk: int=100):
	def query2tsearch(self, query: str, threshold: float = 0.5, topk: int = 100):
		""" 搜索结果返回 """

		if not self.text_clean(query):
			return [], [], [], [], []
		scores = []
		words = self.doc2word(query)
		intents = self.key_terms(query, words)
		ts_dict = self.words2tsearch(words, threshold, topk)
		index = list(ts_dict.keys()) # 行索引
		text_df = DF.iloc[index]
		# scores = [ts_dict.get(idx) for idx in index]

		# 改写召回分数
		for idx in index:
			score = ts_dict.get(idx) * 0.5
			if intents:
				intent_word, intent_score, _ = sorted(intents, key=lambda x: x[1], reverse=True)[0]
				if intent_word:
					intent_idx = DF[DF['content'].str.contains(intent_word)]
					if idx in intent_idx:
						score += 0.5*intent_score
			scores.append(score)

		return text_df, scores, intents


NER, SEG = None, None
if NER is None or SEG is None:
	NER, SEG = model_init()

bm25 = None
if bm25 is None:
	bm25 = BM25()

parquet_path = join(abspath(dirname(__file__)), "./data/config/docs.parquet")
DF = pd.read_parquet(parquet_path)

BCE_EMBS, SBERT_EMBS, CLIP_EMBS, PQUERY_EMBS, PPARA_EMBS = None, None, None, None, None
if BCE_EMBS is None:
	BCE_EMBS = torch.tensor([x[0] for x in DF.bce_emb.tolist()])
	SBERT_EMBS = torch.tensor([x[0] for x in DF.sbert_emb.tolist()])
	COROM_EMBS = torch.tensor([x[0] for x in DF.corom_emb.tolist()])
	CLIP_EMBS = torch.tensor([x[0] for x in DF.clip_emb.tolist()])
	PQUERY_EMBS = torch.tensor([x[0] for x in DF.pquery_emb.tolist()])
	PPARA_EMBS = torch.tensor([x[0] for x in DF.ppara_emb.tolist()])



if __name__ == '__main__':
	print(DF.columns)
	# ------------------  文本搜索 ------------------
	# 生成词库

	# doc_lst = []
	# for row in DF.itertuples():
	# 	doc_lst.append(row.content)
	# bm25 = BM25()
	# bm25.build_croups(doc_lst, save=True)

	# # 搜索测试
	# text = "筑巢奖"
	# text = "小程序 筑客网"
	# text = "筑巢奖 2024年"
	# text = "轻量模型"
	# print("搜索词：", bm25.text_clean(text))
	# # print(bm25.query2tsearch(text, DF))
	#
	# contents, file_names, scores, index, intents = bm25.query2tsearch(text, threshold=0.0)
	# for c, f, s, i in zip(contents, file_names, scores, index):
	# 	print("--" * 20)
	# 	print(f"文件: {f} , content: {c}, score: {s}, intents: {intents}")

	text = "任超 工作总结"
	text = '张有利'
	res = bm25.query2tsearch(text)
	print(res)
