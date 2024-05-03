#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-07-10 14:52
# @Author   : NING MEI
# @Desc     :


""" 学习和使用es """
import hashlib
# 先启动 es及kibana
import time
from datetime import datetime

from elasticsearch import Elasticsearch

ES_HOST = "http://127.0.0.1:9200/"

es = Elasticsearch(ES_HOST)

data = {"mid": [i for i in range(100)], "desc": [f"text-{x}" for x in range(100)]}


def insert_es_index1(es, index_name: str = "testme"):
	""" 创建索引并插入索引 """

	start = time.time()

	mapping_body = {
		"properties": {
			"media_id": {"type": "long"},
			"desc": {"type": "text"}
		}
	}

	es_body = {"mappings": mapping_body}

	try:
		has_index = es.indices.exists(index=index_name)
		print("索引是否存在：", has_index)
		if not has_index:
			es.indices.create(index=index_name, body=es_body)
		else:
			es.indices.put_mapping(body=mapping_body, index=index_name)
	except Exception as e:
		print(e)

	for i in range(100):
		print(i)
		es.index(index=index_name, id=str(i), document={
			"media_id": data['mid'][i],
			"desc": data['desc'][i]}
		         )

	end = time.time()
	print(f"耗时: {end - start} ")


def sha1(txt):
	return hashlib.sha1(str(txt).encode('utf-8')).hexdigest() if txt else ''


def insert_es_index2(es, index_name: str = "testme"):
	""" """

	names = ['刘一', '陈二', '张三', '李四', '王五', '赵六', '孙七', '周八', '吴九', '郑十']
	sexs = ['男', '女', '男', '女', '男', '女', '男', '女', '男', '女']
	ages = [25, 28, 29, 32, 31, 26, 27, 30, 27, 30]
	character = ['自信但不自负,不以自我为中心',
	             '努力、积极、乐观、拼搏是我的人生信条',
	             '抗压能力强，能够快速适应周围环境',
	             '敢做敢拼，脚踏实地；做事认真负责，责任心强',
	             '爱好所学专业，乐于学习新知识；对工作有责任心；踏实，热情，对生活充满激情',
	             '主动性强，自学能力强，具有团队合作意识，有一定组织能力',
	             '忠实诚信,讲原则，说到做到，决不推卸责任',
	             '有自制力，做事情始终坚持有始有终，从不半途而废',
	             '肯学习,有问题不逃避,愿意虚心向他人学习',
	             '愿意以谦虚态度赞扬接纳优越者,权威者',
	             '会用100%的热情和精力投入到工作中；平易近人',
	             '为人诚恳,性格开朗,积极进取,适应力强、勤奋好学、脚踏实地',
	             '有较强的团队精神,工作积极进取,态度认真']
	subjects = ['语文', '数学', '英语', '生物', '地理', '语文', '数学', '英语', '生物', '地理']
	grades = [85, 77, 96, 74, 85, 69, 84, 59, 67, 69, 86, 96, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86]
	create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	# 创建字段映射
	mapping_body = {
		"properties": {
			"name": {"type": "keyword"},
			"age": {"type": "long"},
			"sex": {"type": "keyword"},
			"desc": {"type": "text"},
			"subject": {"type": "keyword"},
			"score": {"type": "long"},
			# 给‘text’添加了分词
			"desc_multi": {
				"properties": {
					"analyzer_ik": {
						"type": "text",
						"analyzer": "ik_max_word",
						"search_analyzer": "ik_smart"
					},
					"analyzer_standard": {
						"type": "text",
						"analyzer": "standard"
					}
				}
			}
		}
	}

	settings_body = {
		"analysis": {
			"normalizer": {"lowercase": {"type": "custom", "filter": ["lowercase"]}}
		}
	}

	es_body = {"mappings": mapping_body, "settings": settings_body}

	try:
		has_index = es.indices.exists(index=index_name)
		print("是否存在索引：", has_index)
		if not has_index:
			es.indices.create(index=index_name, body=es_body)
		else:
			es.indices.put_mapping(body=mapping_body, index=index_name)
	except Exception as e:
		print(e)

	for i in range(len(names)):
		name = names[i]
		age = ages[i]
		sex = sexs[i]
		desc = character[i]
		subject = subjects[i]
		score = grades[i]
		# create_time_str = create_time[i]

		es.index(index=index_name, id=sha1(i), document={
			"name": name,
			"age": age,
			"sex": sex,
			"desc": desc,
			"subject": subject,
			"score": score,
			"desc_multi": {
				"analyzer_ik": desc,
				"analyzer_standard": desc
			},
		})



def search(index_name):
	""" 参考： https://blog.csdn.net/yangbisheng1121/article/details/128528112 """

	# 按属性查询，结果过滤返回指定字段
	body = {
		'query': {
			'match': {
				'age': 25
			}
		},
		'_source': ['name', 'tags']
	}
	# res1 = es.search(index=index_name, body=body)
	# print(f"字段查询: {res1}")

	# 按年龄排序
	body = {
		'sort': {
			'age': {
				'order': 'desc'  # asc: 升序, desc: 降序
			}
		}
	}
	# res2 = es.search(index=index_name, body=body)
	# print(f"按年龄排序: {res2}")

	# 查询年龄大于18且小于等于20的文档
	body = {
		'query': {
			'range': {
				'age': {
					'gt': 18,
					'lte': 20
				}
			}
		}
	}

	# 按年龄降序且分页查询
	body = {
		'sort': {
			'age': {
				'order': 'desc'  # asc: 升序, desc: 降序
			}
		},
		'from': 0,
		'size': 1
	}

	# # 分词查询
	body = {
		"query": {
			"match_phrase": {
				# desc分词结构中有 “学习"的文档
				"desc_multi.analyzer_ik": "学习"
			}
		}
	}
	res3 = es.search(index=index_name, body=body)
	print(f"精准查询: {res3}")

def get_es_analyzer():
	"""获取es分词结果"""
	#
	analyzers = ["standard", "simple", "whitespace", "stop", "keyword", "pattern", "fingerprint"]
	analyzers = ['ik_smart'] # 中文分词器
	text = "和珅 工 作汇报 及 年度总结"
	# text = ['和珅', '工作汇报']
	analyzers = ["whitespace", 'ik_smart']
	for analyzer in analyzers:
		res = self.client.indices.analyze(body={"analyzer": analyzer, "text": text})
		print(analyzer, res)
		print(' ---------------------------------- ')




index_name1 = "testme"
index_name2 = "testme2"
# insert_es_index1(es, index_name1)
insert_es_index2(es, index_name2)
doc_count = es.count(index=index_name2)

print(f"索引 {index_name2} 写入：{doc_count}")
search(index_name2)

"""
一些常用的query_body:
query_body = {
					"query": {  # 多个字符串(分词+全文检索）
						"match": {
							'content': {
								"query": query,
								"fuzziness": "AUTO", # 模糊搜索
							}
						}
					},
					"size": ES_BM25_SEARCH_SIZE
				}

				query_body = {
					"query": { # 短语匹配
						"match_phrase": {
							"content": "屈红森"
						}
					}
				}
				query_body = {  # 不同字段权重 -- 并集
					'query':
						{'bool':
							{
								'should': [
									{
										'match_phrase': {
											'content': {
												'query': '屈红森',
												'boost': 3
											}
										}
									},
									{
										'match_phrase': {
											'content':
												{'query': '工作汇报',
												 'boost': 1}
										}
									}
								]
							}
						}
				}

			query_body = {
				"query": {
					"query_string": {  # 字符串查询 & 逻辑查询
						"default_field": "content",
						"query": "屈红森 OR (算法 AND 工作成果)"
					}
				}

			}

"""
