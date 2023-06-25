#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-06-21 17:40
# @Author   : NING MEI
# @Desc     :

""" gRPC 服务端 """

import sys
sys.path.append("./proto")
import time
import grpc
import intent_pb2
import intent_pb2_grpc
from datetime import datetime
from concurrent import futures

from detect import infer as MODEL

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class IntentService(intent_pb2_grpc.IntentServiceServicer):
	"""
	继承 IntentService,实现 intent_detct(意图检测) 方法： 对应 proto中为 ‘service’
	"""

	def __init__(self):
		pass

	def Result(self, request, context):
		"""
		具体实现intent_detct的方法，并按照pb的返回对象构造 IntentResponse 返回
		Result 对应为 proto中的方法名
		Args:
			request:
			context:

		Returns:

		"""

		# 具体实现功能方法
		res = MODEL(query=request.text)

		# 响应结果
		return intent_pb2.IntentResponse(result=str(res))


def run():
	""" 服务启动 """

	RPC_HOST = '192.168.0.17'
	RPC_PORT = 50051

	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

	# 添加服务项
	intent_pb2_grpc.add_IntentServiceServicer_to_server(IntentService(), server)

	# 访问地址
	# server.add_insecure_port('[::]:50052') # 默认为本地
	server.add_insecure_port(f'{RPC_HOST}:{RPC_PORT}')

	# 开启服务
	server.start()
	print(f"start gRPC service: {datetime.now()}")

	# 设置停止条件（可不加）
	try:
		while True:
			time.sleep(_ONE_DAY_IN_SECONDS)

	except KeyboardInterrupt:
		server.stop(0)

	# 强制终止
	# server.wait_for_termination()


if __name__ == '__main__':
	run()
