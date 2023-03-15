#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-03-15 18:54
# @Author   : NING MEI
# @Desc     :

import json
import requests
import pandas as pd
from typing import List
from lib.beanstalkd1 import BeanStalk


def beanstalk_init():
	return BeanStalk(QUEUE_ADDR)



def cls_api(doc: str):
	url = "http://192.168.0.17:5004/cls"
	data = {"doc": doc }
	resp = requests.post(url, data=json.dumps(data))
	print(resp)

	return resp.text



def task_consumer():
	tube = 'cls'
	beanstalk.use(tube)
	stats_tube = beanstalk.stats_tube(tube)
	beanstalk.watch(tube)
	print("stats_tube: ", stats_tube)

	while True:
		job = beanstalk.consumer()  # 此时表示已被消费
		job_id = job.id  # 任务的id
		job_body = job.body  # 任务的信息体
		print(job_id, job_body)
		beanstalk.delete(job_id)  # 消


QUEUE_ADDR_HOST = "127.0.0.1"
QUEUE_ADDR_PORT = 11300
QUEUE_ADDR = [QUEUE_ADDR_HOST, QUEUE_ADDR_PORT]

beanstalk = None
if beanstalk is None:
	beanstalk = beanstalk_init()


task_consumer()

