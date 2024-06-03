#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2024-05-30 13:12
# @Author   : NING MEI
# @Desc     :


import re
import ast
import json
import langid
import requests
from configs import *
from typing import List, Dict, Union


class Docment:
	""" 文本处理 """
	def __init__(self):
		""""""

	def clean(self, text: str):
		text = re.sub(r'[\t]+', ' ', text)
		text = re.sub(r'[ ]{2,}', ' ', text)
		text = re.sub(r'[\n]+', ' ', text)
		text = re.sub(r'[\n|\r]', ' ', text)
		return text.strip()

	def lan_detect(self, doc: str):
		return langid.classify(doc)[0]

	def segment(self, doc):
		para = re.sub('([。！？\?])([^”’])', r"\1\n\2", doc)
		para = re.sub('([\.;])(\s)', r"\1\n\2", para)  # 英文断句
		para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
		para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
		para = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
		para = para.rstrip()

		del doc

		return para.split("\n")


	def remove_nonChinese(self, doc: str):
		""" 保留中文 """
		paragraphs = self.segment(doc)
		paragraphs = list(filter(lambda t: self.lan_detect(t) == 'zh', paragraphs))
		del doc
		return "".join(paragraphs)

	def remove_Chinese(self, doc: str):
		""" 删除中文 """
		paragraphs = self.segment(doc)
		paragraphs = list(filter(lambda t: self.lan_detect(t) != 'zh', paragraphs))
		del doc
		return "".join(paragraphs)


	def text_truncated(self, doc: str, max_len: int=2048):
		""""""
		if len(doc) <= max_len:
			return doc

		num, total_len, half_len = 0, len(doc), int(max_len // 2)
		bag1, bag2 = [], []
		paragraphs = self.segment(doc)
		for idx, para in enumerate(paragraphs):
			num +=len(para)
			if num <= half_len:
				bag1.append(para)

			elif num > total_len - half_len:
				bag2.append(para)

		if len("".join(bag1 + bag2)) > max_len:
			bag1 = self.list_pop_by_index(bag1, half_len, pop_indx=-1)
			bag2 = self.list_pop_by_index(bag2, half_len, pop_indx=0)
			if len("".join(bag1 + bag2)) > max_len:
				bag2_len = max_len - len("".join(bag1)) - len("".join(bag2))
				bag2 = [" ", "".join(bag2)[-bag2_len: ]]

		return "".join(bag1 + bag2)


	def list_pop_by_index(self, lst: List, max_len: int, pop_indx: int=0):
		"""元素删除"""
		if len(lst) > 1:
			while len("".join(lst)) > max_len:
				lst.pop(pop_indx)
		return lst

	def formater(self, res: Dict):
		empyt_values = ['无', '未知']
		res_dict = {}
		if res:
			for k, v in res.items():
				if v:
					if isinstance(v, list):
						v = list(filter(lambda x: x not in empyt_values, v))
						if v:
							res_dict[k] = v
					else:
						if v not in empyt_values:
							res_dict[k] = v
		del res
		return res_dict

	def get_parser(self, res: Dict, info=None):
		"""输入结果格式化处理"""
		def get_values(dic: Dict, name: str):
			res = []
			for k, v in dic.items():
				if k.startswith(name) or name in k:
					if v:
						if isinstance(v, str):
							res.append(v)
						else:
							res.extend(v)

			return res

		def return_one(item: Union[List, str]):
			if not item:
				return ""

			if isinstance(item, str):
				item = [item]
			if isinstance(item, List):
				if len(item) > 1:
					item = item[:1]

			return "".join(item)

		# print("原始提取res: ", res)

		res = self.formater(res)
		desginer = get_values(res, "设计者")
		organization = get_values(res, "设计机构")
		area = get_values(res, "面积")
		location = get_values(res, "地址")

		if desginer and organization:
			desginer = organization
		elif len(desginer) == 0 and len(organization) >0:
			desginer = organization

		desginer = return_one(desginer)
		location = return_one(location)
		area = return_one(area)

		result = {"desginer": desginer, "location": location , "area": area, "data": res}
		if info:
			result.update({"info": info})

		return result


	def process(self, doc: str, max_len: int=3500):
		doc = self.clean(doc)
		doc_lan = self.lan_detect(doc)
		# 根据句子语种过滤
		if doc_lan == "zh":
			doc = self.remove_nonChinese(doc)
		else:
			doc = self.remove_Chinese(doc)

		if len(doc) > max_len:
			# 文本长度截取
			doc = self.text_truncated(doc, max_len)

		return doc


def generate_prompt(question: str, source_docs: Union[str, List, dict], prompt_template: str):
	""" 生成prompt """

	context = ''
	if isinstance(source_docs, str):
		context = source_docs
	elif isinstance(source_docs, list):
		context = "\n".join(source_docs)
	elif isinstance(source_docs, dict):
		context = "\n".join([d.get("page_content") for d in source_docs])

	if context:
		prompt = prompt_template.replace("{question}", question).replace("{context}", context)
		return prompt
	else:
		return None


def get_answering(prompt: str):
	""" api 调用 """
	# 限制6144 tokens、24000字符
	url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie_speed?access_token=" + get_access_token()
	# 限制126976 tokens、516096个字符
	url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-speed-128k?access_token=" + get_access_token()
	payload = json.dumps({
		"messages": [
			{
				"role": "user",
				"content": prompt,
			}
		],
		"top_p": 0,
		"temperature": 0.1
	})

	res, status = {}, '请求失败'
	headers = {'Content-Type': 'application/json'}
	response = requests.request("POST", url, headers=headers, data=payload)
	if response.status_code == 200:
		resp = response.json().get('result', "")
		if resp:
			pattern = r'\{([^}]*)\}' # 获取
			match = re.search(pattern, resp)
			if match:
				try:
					inner_string = match.group()
					res = ast.literal_eval(inner_string)
					status = f'OK：{resp}'
				except Exception as error:
					status = f"解析失败: {error}, {resp}"
			else:
				status = f'格式错误: {resp}'
		else:
			status = "提取失败"

	del prompt
	return res, status



def get_extract(context: str):
	""" 基于GPT今天信息抽提 """
	question = """请精准这篇家装案例中信息：设计者、设计机构、作品地址、作品面积(含单位), 如果没有请用’未知‘代替。并以键值对形式输出结果，json key: 设计者，设计机构，作品面积"""
	# 文本预处理
	context = DOC.process(context)
	# prompt合成及结果生成
	prompt = generate_prompt(question, context, PROMPT2)
	res, status = get_answering(prompt)
	result = DOC.get_parser(res, info=status)

	del context
	return result


DOC = None
if DOC is None:
	DOC = Docment()


if __name__ == '__main__':
	text = """合肥中海观园 | 柏涛建筑 | 中国安徽合肥  探索公园式生态社区模式，提供开放社区、街区场景再造、
	人文关怀体验，成为城市未来发展的催化剂。
	项目试图探索一种全新的公园式生态综合社区的模式，希望在风景怡人的场地打造一处能够促进邻里交流的空间。
	项目位于合肥市包河区骆岗片区，项目紧邻骆岗机场（旧址），拥有城市珍贵的成长记忆。整体规划设计从机场汲取灵感，采用灵动飘逸的流线型元素，融入整体街区脉络，建立场地与城市的联结，传承旧机场的记忆，打造空中翱翔的理念及文化符号，构建出一个流畅、启程式的天际线。
	项目注重城市与环境的融合，融入对未来中央公园发展及整体街区脉络的理解，重新建立场地与城市的连接，塑造出生机勃勃的公园式社区场所，在城市中心呈现自然有机和生态，对话中央公园的自然景观，让自然与城市相互渗透。
	整体项目分为商业服务业设施、居住及幼儿园等一系列空间，设计试图探索一种全新的公园式生态综合社区的模式。该生态社区包括生态基底的塑造、开放社区、街区场景再造、人文关怀的体验。
	阶梯式建筑布置在中心创造了一处的城市枢纽式的社交空间，我们希望城市、建筑和景观彼此成就与互补，鼓励城市居民、旅客与周围环境及景观展开动态对话。
	建筑群的立面采用白色及银灰色线条打造流线型美学，呼应“航空”主题。
	丰富的建筑高度，让流动的“航空”主题得以延续，在银灰色线条的串联下，建筑与建筑之间也形成了彼此呼应的关系。
	作为室内、外空间的衔接点，全龄友好的架空层提供多元生活社区的场景空间。
	办公楼与商业大楼将居住区与繁忙的交通隔离开，创造出亲密静谧的内部环境。丰富的建筑群混合业态与静谧的居住氛围展现着都市魅力。
	立面注重各地块与城市界面的塑造，在易于感知的街区尺度中，植入适时的生活业态，为居者打造丰富多元的生活场景。
	将街道生活引入建筑内部，打造自由开放的街区。
	临街以融入城市肌理的商铺向邻里开放，缝补城市的功能，连续城市的界面。
	幼儿园立面融合流畅的横向曲线飘板造型以及活泼的几何立面造型，结合造型设计公共大台阶连接各层公共空间，为幼儿提供更多趣味性的成长游乐空间，打造一个在趣味玩乐中学习成长的幼儿园空间。
	项目强调了其对区域发展的积极影响，包括提升土地价值、塑造宜居环境、提供高品质生活方式、促进基础设施建设和产业发展，以及提升企业品牌形象。同时，项目的设计和规划注重创新性和可复制性，旨在为居民和城市提供长期的价值。
	项目档案
	项目名称: 合肥中海观园项目
	项目位置: 安徽合肥市
	业主单位: 中海地产
	建筑方案设计: 柏涛建筑设计（深圳）有限公司
	建筑施工图设计: 华东建筑设计研究院有限公司
	景观设计: 笛东规划设计(北京)股份有限公司
	用地面积:  47984.72  m²    
	项目摄影: 陈桂明"""

	question = """请精准提取这篇家装案例中信息：设计者、设计机构、作品地址、作品面积(含单位), 如果没有请用’未知‘代替。并以json形式输出结果，json key: 设计者，设计机构，作品面积"""

	# prompt = generate_prompt(question, text, PROMPT2)
	# dic = gpt_answering(prompt)
	# print("dic: ", dic)
	print(get_extract(text))
