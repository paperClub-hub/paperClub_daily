#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-06-21 18:11
# @Author   : NING MEI
# @Desc     :


""" gRPC 客户端 """

import sys

sys.path.append("./proto")
import time
import grpc
import intent_pb2
import intent_pb2_grpc
from datetime import datetime
from concurrent import futures


def predict(text: str = "客厅沙发"):
	"""
	模拟请求服务方法信息
	Returns:

	"""

	# 连接服务
	with grpc.insecure_channel('192.168.0.17:50051') as channel:
		stup = intent_pb2_grpc.IntentServiceStub(channel)
		response = stup.Result(intent_pb2.IntentRequest(text=text))
		print("请求结果： " + response.result)

		return response.result


if __name__ == '__main__':
	t1 = time.time()
	text = "客厅沙发"
	text = "青山周平"
	text = "苏州博物馆"


	res = predict(text)
	print("res: ", res)
