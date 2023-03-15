#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-03-15 18:13
# @Author   : NING MEI
# @Desc     :

from typing import List
import pandas as pd
from lib.beanstalkd1 import BeanStalk


def beanstalk_init():
	return BeanStalk(QUEUE_ADDR)


def load_data():
	data = {}
	df = pd.read_csv("./src/zm_demo.csv")
	for line in df.itertuples():
		id = line[1]
		title = line[2]
		text = line[3]
		cnt = title + " " + text
		data[id] = cnt
		del line, text, title, id

	del df

	return data


def tasks2beanstalkd(docs: List, res: List, tube="cls"):
	id = 0

	while id < len(docs):
		doc = docs[id]
		id += 1
		doc = doc.encode("utf-8") # encode
		# print("doc: ", doc)
		beanstalk.producer(body=doc, tube=tube)
		res.append(id)


# data
data = load_data()
texts = [v for k, v in data.items()]

QUEUE_ADDR_HOST = "127.0.0.1"
QUEUE_ADDR_PORT = 11300
QUEUE_ADDR = [QUEUE_ADDR_HOST, QUEUE_ADDR_PORT]

beanstalk = None
if beanstalk is None:
	beanstalk = beanstalk_init()

ids = []
# tasks2beanstalkd(docs=texts, res=ids)
# print(ids)
