#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-09-19 9:53
# @Author   : NING MEI
# @Desc     :


""" 文本召回 """

from os.path import abspath, dirname, join, exists
from modelscope.utils.constant import Tasks
from modelscope.pipelines import pipeline
from typing import List, Dict, Union
from ordered_set import OrderedSet
from paddlenlp import Taskflow
from tqdm.auto import tqdm
import jieba as _jieba
import torch.nn as nn
import pandas as pd
import numpy as np
import pickle
import random
import torch
import json
import re



from utils import norm, get_trt_h14_txt_emb, dict_update
from config import USE_ZHUKE, USE_ZM80W, USE_PADDLE
# 导入数据
if USE_ZHUKE:
	from zk_data import PROJECT_DF
else:
	from zm_data import PROJECT_DF



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
]


def softmax(x):
	return np.exp(x) / np.sum(np.exp(x), axis=0)


def text_clean(text):
	text = re.sub(r'\W', ' ', text)
	text = text.replace('丨', '')
	return text


def ner_init():
	ner_dict_path = "/data/1_qunosen/project/res/rank/zhimo_rank/dev_lib"
	dict_path = join(ner_dict_path, "./user_dict.txt")
	_jieba.load_userdict(f"{ner_dict_path}/zhuke_jieba.dict")
	_jieba.load_userdict(f"{ner_dict_path}/my_jieba_dict.txt")
	device_id = 0
	ner = Taskflow('ner', user_dict=dict_path, entity_only=True, device_id=device_id)
	seg = Taskflow("word_segmentation", user_dict=dict_path, mode="fast", device_id=device_id)
	return ner, seg

def semantic_init():
	""""""
	model_path = '/home/user/.cache/modelscope/hub/damo/nlp_structbert_sentiment-classification_chinese-ecommerce-base'
	# semantic_cls = pipeline(Tasks.text_classification, 'damo/nlp_structbert_sentiment-classification_chinese-ecommerce-base')
	semantic_cls = pipeline(Tasks.text_classification, model_path)
	return semantic_cls

def sentiment_infer(text):
	res = SENTA(input=text)
	# {'scores': [0.9941287040710449, 0.005871296394616365], 'labels': ['正面', '负面']}
	# scores = res.get("scores") #
	label = res.get("labels")[0]
	is_postive = label == '正面'
	print("query_情感分析：",  label, is_postive)

	return is_postive


class Tsearch:
	def __init__(self):
		self.words = {}
		root = abspath(dirname(__file__))
		pwd = join(root, 'dev_lib')

		dataset_id = 'zk'
		if USE_ZHUKE == False:
			if USE_ZM80W == True:
				# dataset_id = 'zm80w'
				dataset_id = 'zkzm'
			else:
				dataset_id = 'zm'

		method_id = 'paddle' if USE_PADDLE else 'jieba'

		self.croups_path = join(pwd, f"{dataset_id}_{method_id}_croups.pkl")
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

		if USE_PADDLE:
			# return [x[0] for x in query2nertags_paddlener(doc)]
			return query2words_paddleseg(doc)

		else:
			# doc = re.sub(r'\W', ' ', doc)
			# doc = doc.replace('丨', '')
			# words = [str(w.strip()).lower() for w in _jieba.lcut_for_search(doc) if w.strip() and w not in self.STOP_WORDS]
			# del doc
			# return query2words_jiebalcut(doc)
			return query2words_jiebalcutforsearch(doc)

	def build_croups(self, docs, save: bool = True):
		""" 通过文档统计语料：计算词矩阵 """
		self.num_docs += len(docs)
		for i, doc in tqdm(enumerate(docs)):
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


def term_weight(words: List = ['火锅店', '唐忠汉', '苏州'], text: str = None):

	print("词权重计算: ", words)
	if len(words) == 1:
		return np.array([1.0])

	if text:
		search_vector = torch.tensor([get_trt_h14_txt_emb(text)])
	else:
		search_vector = torch.tensor([get_trt_h14_txt_emb("".join(words))])

	keyword_vector = torch.tensor([get_trt_h14_txt_emb(w) for w in words])
	atws = nn.functional.softmax(torch.matmul(search_vector, keyword_vector.t()), dim=-1)
	atws = atws / atws.sum()
	weights = atws.numpy().squeeze(0)

	del keyword_vector, search_vector

	return weights


def query2truncation(query: str, words: List, topk: int = 5):
	""" 截断 """
	weights = term_weight(words, query)
	trunc_idx = np.argsort(-weights)[:topk]
	trunc_words = np.array(words)[trunc_idx]
	res = list(map(lambda x: x, [(i, w) for i, w in enumerate(words) if w in trunc_words]))

	return res


def query2words_tag_by_truncat(query: str, query_words: List = None, max_keep: int=5):
	""""""

	if not query_words:
		query_words = query2words_paddleseg(query)

	ner_res = query2nertags_paddlener(query_words)
	words = list(map(lambda x: x[0], ner_res))
	tags = list(map(lambda x: x[1], ner_res))
	if len(set(words)) > max_keep:
		info = query2truncation(query, words, max_keep)
		words = [w for (i, w) in info]
		tags = [tags[i] for (i, w) in info]
		# print(words, tags)

	return list(tuple(zip(words, tags)))



def query2words_jiebalcut(query):
	"""jieba分词"""
	query = text_clean(query)
	words = _jieba.lcut(query)
	words = list(filter(lambda x: x.strip() and x not in TS.STOP_WORDS, words))
	del query
	return words


def query2words_jiebalcutforsearch(query):
	"""jieba分词"""
	query = text_clean(query)
	words = _jieba.lcut_for_search(query)
	words = list(filter(lambda x: x.strip() and x not in TS.STOP_WORDS, words))
	del query
	return words

def query2words_paddleseg(query):
	"""paddleseg分词"""
	query = text_clean(query)
	words = SEG(query)

	words = list(filter(lambda x: x.strip() and x not in TS.STOP_WORDS, words))
	return words


def query2nertags_paddlener(query: Union[List, str], min_len: int=2):
	""" ner识别 """
	if isinstance(query, str):
		query = text_clean(query)
		ner_res = NER(query)
		ner_res = list(filter(lambda x: (len(x[0]) >= min_len) and (x[-1] in FETCH_TAGS), ner_res))
		if not ner_res:
			return []

		return ner_res

	else:
		# res = []
		res = OrderedSet()

		if len(query) > 1:
			unique_words = []
			ner_res = NER(query)
			# print("query: ", query, "ner_res: ", ner_res)
			for item in ner_res:
				item = list(filter(lambda x: (len(x[0]) >= min_len) and (x[-1] in FETCH_TAGS), item))
				if item:
					for ele in item:
						if ele[0] not in unique_words:
							unique_words.append(ele[0])
							res.update(item)
					# res.update(item)
		else:
			res = [x for x in NER(query[0]) if (len(x[0]) >= min_len) and (x[-1] in FETCH_TAGS)]

		return list(res)


def get_querywords(query: str):
	if USE_PADDLE:
		words = query2words_paddleseg(query)
	else:
		words = query2words_jiebalcut(query)

	return words

def query2wordtags(query, ner_to_seg=False):
	""" 分词 + ner """

	words = get_querywords(query)
	words.append(query)
	print("words: ", words)
	ners = query2nertags_paddlener(words)
	return ners


def query2intent(query, query_tags: List):
	""""""
	query_content, query_intent = OrderedSet(), []
	if not query_tags:
		return query, []

	else:
		for (w, t) in query_tags:
			if t in WEIGHTED_TAGS:
				query_intent.append((w, t))
			else:
				query_content.append(w)

	query_content = " ".join(query_content)
	if not query_content:
		query_content = query

	print("query_content, query_intent: ", query_content, query_intent)

	return query_content, query_intent


def query_process(query: str, query_tags: List):
	"""查询词处理"""

	query_sentiment = sentiment_infer(query)
	query_content, query_intent = query2intent(query, query_tags)
	words = list(map(lambda x: x[0], query_tags))
	term_weight_dict = {}
	if words:
		term_scores = term_weight(words, query).tolist()
		term_weight_dict = dict(zip(words, term_scores))
	print("term_weight_dict: ", term_weight_dict)

	return query_content, query_intent, query_sentiment, term_weight_dict



def intent_match(query_intent: List, df: pd.core.frame.DataFrame):
	"""意图匹配 """

	# authors, brands, locations, ohters = set(), set(), set(), set()

	pids = set()
	if query_intent:
		intent = list(map(lambda x: x[0], query_intent))
		if intent:
			tdf = df[df['title'].str.contains(r"|".join(intent))]
			if len(tdf):
				pids.update(tdf['project_id'].unique().tolist())
			del tdf

	return list(pids)


def grid_match(df: pd.core.frame.DataFrame, term_weight_dict: Dict):
	""""""

	# 词权重
	termweight2pids_dict = {}
	for word, score in term_weight_dict.items():
		tdf = df[df['title'].str.contains(word)]
		if len(tdf):
			pids = tdf['project_id'].tolist()
			for pid in pids:
				termweight2pids_dict[pid] = max(termweight2pids_dict.get(pid, 0), score)
		del tdf

	# # 意图
	# intent_weighted_pids = set()
	# if query_intent:
	# 	intent = list(map(lambda x: x[0], query_intent))
	# 	if intent:
	# 		tdf2 = df[df['title'].str.contains(r"|".join(intent))]
	# 		if len(tdf2):
	# 			intent_weighted_pids.update(tdf2['project_id'].unique().tolist())
	# 		del tdf2

	return termweight2pids_dict


def words2tsearch(words: List, threshold:float=0.5, topk: int=100, query_intent:List=None):
	""""""
	ts_idxes, ts_scores = [], []
	scores = TS.get_scores(words)
	idx = np.argsort(-scores)[: topk]
	res_dict = dict(zip(idx, scores[idx]))
	res_dict_norm = norm(res_dict)

	# titles = PROJECT_DF.iloc[idx]['title'].tolist()
	intents = list(map(lambda x: x[0], query_intent))

	for i, score in res_dict.items():
		score_norm = res_dict_norm.get(i)
		if score_norm > threshold:
			ts_idxes.append(i)
			ts_scores.append(score)
		# else:
		# 	title = PROJECT_DF.iloc[i]['title']
		# 	res = list(filter(lambda x: x in title, intents))
		# 	if res:
		# 		ts_idxes.append(i)
		# 		ts_scores.append(score)

	del scores, idx, res_dict
	return dict(zip(ts_idxes, ts_scores))



def get_match_text_from_df(query_tag_pairs: List, term_weight_dict, query_intent:List = None, threshold: float = 0.5, num_candicates: int = 100):
	""" 根据搜索词匹配文本，召回关联案例 """

	if not query_tag_pairs:
		return [], [], []

	# 文本查询
	query_words = list(map(lambda x: x[0], query_tag_pairs))
	print("案例匹配查询词: ", query_words)

	# 召回案例
	text_search_map = words2tsearch(query_words, threshold, num_candicates, query_intent)
	print("term_weight_dict: ", term_weight_dict)
	precall_dict = {}
	ori_precall_dict = {}
	if text_search_map:
		idxes = list(text_search_map.keys())
		p_scores = list(map(text_search_map.get, idxes))
		pdf = PROJECT_DF.iloc[idxes]
		pids = pdf['project_id'].tolist()
		term_pid_dict = grid_match(pdf, term_weight_dict)
		precall_dict = dict(zip(pids, p_scores))
		ori_precall_dict = norm(dict(zip(pids, p_scores)))
		# 跟新案例权重
		precall_dict = dict_update(precall_dict, term_pid_dict, 'weight')
		precall_dict = norm(precall_dict)

		# print("title: ", pdf['title'].tolist())
		# print(p_scores)

	return precall_dict, query_tag_pairs, ori_precall_dict


TS = None
if TS is None:
	TS = Tsearch()

NER = None
SEG = None
if NER is None:
	NER, SEG = ner_init()

SENTA = None
if SENTA is None:
	SENTA = semantic_init()




def testme():
	import pandas as pd
	# df = pd.read_parquet("/data/1_qunosen/project/res/rank/zhimo_rank/data/zk_project.parquet")
	# df = pd.read_parquet("/data/1_qunosen/project/res/rank/zhimo_rank/data/zm_project2.parquet")
	# df = pd.read_parquet("/data/1_qunosen/project/res/rank/zhimo_rank/data/zk80w_project.parquet")
	# df = pd.read_parquet("/data/1_qunosen/project/res/rank/zhimo_rank/data/zkzm_project.parquet")
	# titles = df['title'].tolist()
	# print(df.head())
	# print(len(titles))
	# ts = Tsearch()
	# # #创建文本索引
	# ts.build_croups(titles)

	t = "唐忠汉样板间"
	t = "唐忠汉火锅店"
	t = "安定设计案例"
	t = "孟菲斯沙发"
	# words = query2keywords_jieba(t)
	# print(t, words)
	t = "唐忠汉苏州 圆融写字楼 入户门 门厅设计"
	t = "梁志天设计集团(SLD)丨别墅丨梁志天新作Penthouse豪宅：恒禾七尚！"
	t = "博物馆"
	t = "莫兰迪"
	t = "深圳康莱德酒店"
	t = "唐忠汉样板间苏州"
	t = "三口之家在客厅享受欢乐时光"
	t = "深圳康莱德酒店"
	t = '康莱德'
	t = '梁志天客厅'
	t = '唐忠汉样板间'
	t = '开放式U型餐厅'
	t = '唐忠汉 卫生间'
	ner_res = NER(t)
	print("ner_res: ", ner_res)
	# query2words_tag_by_truncat(t)
	# print(query2words_paddleseg(t))
	# ner_res = query2nertags_paddlener(t)
	# print(query2nertags_paddlener(query2words_paddleseg(t)))

	query_tag_pairs = query2wordtags(query=t, ner_to_seg=True)
	print("query_tag_pairs: ", query_tag_pairs)

	query_content, query_intent, query_sentiment, term_weight_dict = query_process(query=t, query_tags=query_tag_pairs)

	# word_tags = query2wordtags(t, ner_to_seg=True)
	res = get_match_text_from_df(query_tag_pairs=query_tag_pairs, term_weight_dict=term_weight_dict,
	                             query_intent=query_intent,
	                             threshold=0.4, num_candicates=100)

	# print(query2wordtags('冰裂纹板'))
	# ws = ['冰', '裂纹', '板', '冰裂纹板']
	# print(NER('冰裂纹板'))
	# print("res: ", res)
	# scores = ts.get_scores(['唐忠汉'])
	# idx = np.argsort(-scores)
	# scores = scores[idx]
	# print(scores)
	# print(idx)
	# words = [x[0] for x in word_tags]
	# print(words, term_weight(words, t))
	# query2intent(t, ner_res)



if __name__ == '__main__':
	print()
	testme()

	txt = "深圳康莱德酒店"
	# words = query2words_paddleseg(txt)
	# print("words: ", words)
	# print(query2words_tag_by_truncat(txt, words))
	# print(_jieba.lcut(txt))
	words = ['咖色系', '家具']

	# d = words2tsearch(words)
	# idxes = list(d.keys())
	# pdf = PROJECT_DF.iloc[idxes]
	# print("pdf: ", pdf['title'].tolist())
	#
	kw = '茶叶店'
	kw = '下沉式 庭院'
	# print("匹配结果----------- ")
	# print(PROJECT_DF[PROJECT_DF['title'].str.contains(kw)]['title'].tolist())
	# print(NER(kw))


