#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-03-31 19:00
# @Author   : NING MEI
# @Desc     :

import os
import json
import requests


def get_request():
	url = "http://192.168.0.17:5000/get_test"

	resp = requests.get(url, params={"uname": 'get_testc 请求测试'})

	print("get_request返回结果： ", resp.json())


def post_request():
	url = "http://192.168.0.17:5000/cls1"

	data = {"doc": "这是post请求qury", "threshold": 0.9 }
	resp = requests.post(url, data=json.dumps(data))

	print("post_request返回结果： ", resp.json())

if __name__ == '__main__':
	print()
	get_request()
	post_request()
