#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-11-24 10:52
# @Author   : NING MEI
# @Desc     :


""" fastapi 示例api  """

import json
from typing import Union, List
from pydantic import BaseModel
from fastapi import FastAPI, Query, Body, Form, UploadFile, File, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse, Response, FileResponse

import base64

app = FastAPI()
origins = ["*", ]
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


# 接受用户名和密码
@app.post('/login')
def login(username: str = Form(...), password: str = Form(...)):
	return {'username': username, 'password': password}


# 接受单个bytes数据
@app.post('/upload')
# UploadFile  bytes
async def uploadFile(a_file: bytes = File(...)):
	print('-- 上传byte数据保存 ')
	a_content = a_file  # 接收到的是 bytes，不需要 read

	# byte数据保存到本地
	a_path = 'paperclub.txt'
	with open(a_path, 'wb') as f:
		f.write(a_content)

	# 返回结果
	dict = {
		'a_filesize': len(a_content),
	}

	return json.dumps(dict)


# 接收多个bytes文件
@app.post('/upload2')
async def uploadFile(a_file: bytes = File(...),
                     b_file: bytes = File(...)):
	print('-- 上传多byte数据保存 ')

	a_content = a_file
	b_content = b_file
	a_path = "paperclub_a.txt"
	b_path = "paperclub_b.txt"
	with open(a_path, 'wb') as f:
		f.write(a_content)

	with open(b_path, 'wb') as f:
		f.write(b_content)

	dict = {
		'a_filesize': len(a_content),
		'b_filesize': len(b_content),
	}
	return json.dumps(dict)


# 接收upload文件
@app.post('/upload3')
async def uploadFile22(a_file: UploadFile = File(...),
                       b_file: UploadFile = File(...)):
	print('-- 上传uploadFile ')

	a_content = await a_file.read()
	b_content = await b_file.read()

	a_path = "paperclub_a.txt"
	b_path = "paperclub_b.txt"
	with open(a_path, 'wb') as f:
		f.write(a_content)

	with open(b_path, 'wb') as f:
		f.write(b_content)

	dict = {
		'a_filesize': len(a_content),
		'b_filesize': len(b_content),
		'a_filename': a_file.filename,
		'b_filename': b_file.filename,
		'file_content_type': a_file.content_type
	}

	return json.dumps(dict)


# 多个文件
@app.post("/upload2x")
def upload(files: List[UploadFile] = File(...)):
	for file in files:
		try:
			contents = file.file.read()
			with open(file.filename, 'wb') as f:
				f.write(contents)
		except Exception:
			return {"message": "文件上传错误！"}
		finally:
			file.file.close()

	return {"message": f"成功上传文件： {[file.filename for file in files]}"}


# 接收upload图片字节流
@app.post('/upload4')
async def uploadFile22(url: str = File(...)):
	print('-- 上传uploadFile ')

	print(len(url))

	return json.dumps({"size": len(url)})


# 接收upload byte  和 参数
@app.post('/upload5')
async def uploadFile22(params: str = Form(...), a_file: bytes = File(...)):
	print('-- 上传uploadFile ')

	print("params: ", params)
	print(type(a_file))

	return json.dumps({"state": True})


# 接收upload UploadFile  和 参数
@app.post('/upload6')
async def uploadFile22(params: str = Form(...), a_file: UploadFile = File(...)):
	print('-- 上传uploadFile ')

	print("params: ", params)
	print(type(a_file))

	return json.dumps({"state": True})


# 传递字典
@app.post("/upload7")
async def custom_docments_datasets(params: dict):
	print(type(params))

	return {"num_params": len(params), "params": json.dumps(params)}


# post 图片字节流
@app.post("/post_imgbyte")
def demo_load_local_img(file: str = File(...)):
	# 推送字节流

	print("file: ", file)
	dat = open(file, 'rb').read()
	return StreamingResponse(io.BytesIO(dat), media_type="image/png")


# post 图片字节流(base64)
@app.post("/post_base64img")
def demo_load_local_img(file: str = File(...)):
	# 推送字节流

	dat = open(file, 'rb').read()
	base64_encoded_string = base64.b64encode(dat)  # bytes转化为string

	return Response(base64_encoded_string, media_type="image/png")





class Item(BaseModel):
	file: Union[List[int], int] = None

@app.post("/post_list/")
def demo_post_list(file: Item):
	# 传递数组

	print("file   ---> ", file)
	post_list = file.file
	print(type(post_list), post_list)

	return True


@app.post("/post_list2/")
def demo_post_list(text: List[str]=Body(..., embed=True)):
	# Body 传递数组
	print("text   ---> ", text)
	post_list = text
	print(type(post_list), post_list)

	return True




@app.get("/query_items/")
async def read_items(filename: str = Query(...), fileid: int = Query(...), inputs: list=Query([])):
	query_items = {"filename": filename, "fileid": fileid, "inputs": inputs}
	return query_items


@app.post("/text_image_hits")
async def post_text_extract(text: str = Query(title="文章内容", default="", alias="text"),
                            imgurl: str = Query(title="图片网址", default="", alias="imgurl")):
	""""""

	print("text: ", text)
	print("imgurl: ", imgurl)

	return {"api": [text, imgurl]}


@app.post("/vector/")
async def get_desc_emb(query: str):
	""""""
	return len(query)


class Item2(BaseModel):
	text: Union[str, List]

# 接受str或list
@app.post("/list_str/")
async def demo_list_str(params: Item2):
	text = params.text
	print("params: ", params, "text: ", type(text))

	return text


if __name__ == '__main__':
	ip = "127.0.0.1"
	port = 8000
	import uvicorn

	uvicorn.run(app='demoapi:app', host=ip, port=port, reload=True, debug=True)
