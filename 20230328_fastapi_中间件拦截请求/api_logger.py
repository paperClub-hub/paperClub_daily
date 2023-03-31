#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-03-31 18:22
# @Author   : NING MEI
# @Desc     :


""" 通过中间件拦截请求及返回结果，并写入logger """

import re
import json
import logging
import urllib
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, Request
from starlette.concurrency import iterate_in_threadpool

""" 日志 """
def my_logger(log_obj):
	""" 日志可以根据需求进行保存 或写入文件 """
	# print(logging._handlerList)
	# 创建记录器
	logger = logging.getLogger(log_obj)
	# 及时清空原来的记录，防止累积
	logger.handlers.clear()
	logger.setLevel(logging.DEBUG)

	console_handle = logging.StreamHandler()
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s ')
	console_handle.setFormatter(formatter)
	logger.addHandler(console_handle)

	return logger






# 中间件拦截（日志）
def init_log_middleware(app: FastAPI):
	"""初始化日志中间件"""

	@app.middleware("http")
	async def stat_log(request: Request, call_next):
		my_logger('请求方法').info(request.method)
		my_logger('请求url').info(request.url)


		request_method = request.method
		if request_method == "POST":
			# 针对post请求
			await set_body(request)
			data = await request.json()
			my_logger("请求参数").info(data)
			response = await call_next(request)

			# 获取post请求返回
			response_body = [chunk async for chunk in response.body_iterator]
			response.body_iterator = iterate_in_threadpool(iter(response_body))
			response_data = [b.decode() for b in response_body]

			my_logger('返回结果').info(response_data)

		elif request_method == "GET":
			# TO DO: 参数解码
			data =  request.query_params

			# get 服务器参数
			scope = request.scope
			token = request.headers.get("Authorization", None)

			# 特殊处理：
			url = request.url
			# print("token: ", token)
			# print("sacfsdavd asv ", type(url), urllib.parse.unquote(str(url)))

			my_logger("请求参数").info(data)
			my_logger("请求参数decode").info(urllib.parse.unquote(str(url)))

			# 请求结果
			response = await call_next(request)
			response_body = [chunk async for chunk in response.body_iterator]
			response.body_iterator = iterate_in_threadpool(iter(response_body))
			response_data = [b.decode() for b in response_body]
			my_logger('返回结果').info(response_data)

		else:
			response = await call_next(request)

		return response


# post 请求拦截解析
async def set_body(request: Request):
	receive_ = await request._receive()
	async def receive():
		return receive_

	request._receive = receive


# app服务，类似 app = FastAPI()
def get_application() -> FastAPI:
	# 创建 app 应用
	application = FastAPI(title="案例分类", debug=True)
	# 添加应用
	init_log_middleware(application)
	return application




# 请求字段设置
class Item(BaseModel):
	doc: str
	threshold: float = 0.85

app = get_application()


@app.get("/")
async def api_response():
	return {"mgs": "hello api-logger"}

@app.get("/get_test/")
async def api1(uname: str):
	res = "api_get_resp_" + uname
	return { "uname": res}


@app.post("/cls1")
async def cls_title(param: Item):
	""" api 1 """
	doc = param.doc
	threshold = param.threshold
	# 模型接口输出
	res = {"param": [doc, threshold]}

	return json.dumps(res, ensure_ascii=False)


if __name__ == '__main__':
	ip = "0.0.0.0"
	port = 5000
	import uvicorn

	uvicorn.run(app='api_logger:app', host=ip, port=port, reload=True)