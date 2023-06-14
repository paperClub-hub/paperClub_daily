#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-11-24 10:57
# @Author   : NING MEI
# @Desc     :



""" demoapi 请求 """

import json
import requests
from urllib import parse

BASE_URL = "http://127.0.0.1:8000"


def demo_login():
	taskapi = f"{BASE_URL}/login"

	data = {
		'username': 'paperclub',
		'password': '1234'
	}

	# data = parse.urlencode(data) # 生成key:value键值对字符串
	# headers = {"Content-Type": "application/x-www-form-urlencoded"}
	# resp = requests.post(url=taskapi,
	#                      data=data,
	#                      headers=headers
	#                      )

	resp = requests.post(url=taskapi,
	                     data=data,
	                     )
	print(resp.status_code)
	print(resp.text)



def demo_uploadfile1():
	""" """

	taskapi = f"{BASE_URL}/upload"

	file_path = "./demoapi.py"
	files = {'a_file': (open(file_path, 'rb'), 'text/plain')} # 参数键值需要和前端保持一致

	resp = requests.post(url=taskapi, files=files)

	print(resp.status_code)
	print(resp.text)


def demo_uploadfile2():
	taskapi = f"{BASE_URL}/upload2"

	file_patha = "./demoapi.py"
	file_pathb = "./demoapi.py"
	files = {'a_file': open(file_patha, 'rb'),
	         'b_file': open(file_pathb, 'rb') }

	resp = requests.post(url=taskapi, files=files)
	print(resp.status_code)
	print(resp.text)



def demo_uploadfile3():
	taskapi = f"{BASE_URL}/upload3"

	file_patha = "./demoapi.py"
	file_pathb = "./demoapi.py"
	files = {'a_file': open(file_patha, 'rb'),
	         'b_file': open(file_pathb, 'rb') }

	# headers = {
	# 	# 'content-type': 'multipart/form-data',
    #     # 'content-type':'text/xml',
    #     # 'content-type': 'text/plain',
    #     "Content-Type": "application/json"
	# }

	resp = requests.post(url=taskapi, files=files )
	print(resp.status_code)
	print(resp.text)



def demo_uploadfile3x():

	taskapi = f"{BASE_URL}/upload2x"
	uploafiles = ["./demoapi.py", "./demoapi.py", "./demoapi.py"]
	uploafiles = [('files', open(p, 'rb')) for p in uploafiles]

	resp = requests.post(url=taskapi, files=uploafiles)
	print(resp.status_code)
	print(resp.text)



def demo_uploadfile4():
	""" 本地图片"""

	taskapi = f"{BASE_URL}/upload4"

	img_file = "./test/1.png"
	# files = {"url": open(img_file, 'rb')}
	#  规范写法
	files= {'url':
            ( '1.png',
                open(img_file, 'rb'),
            'image/png',
            )
		}
	resp = requests.post(url=taskapi, files=files )
	print(resp.status_code)
	print(resp.text)


def demo_uploadfile5():
	""" 网络图片"""
	import numpy as np
	def url2bytes(url_img):
		"""        """
		try:
			img_bytes = requests.get(url_img, timeout=3).content
			del url_img
			return img_bytes

		except Exception as e:
			print(f"url转字节失败: {e}")
			return np.asarray([])

	taskapi = f"{BASE_URL}/upload4"

	img_file = 'https://img2.baidu.com/it/u=1918897812,428515511&fm=253&fmt=auto&app=138&f=JPEG?w=567&h=500'
	# files = {"url": open(img_file, 'rb')}
	#  规范写法
	files = {'url':
		         ('1.png',
		          url2bytes(img_file),
		          'image/png',
		          )
	         }
	resp = requests.post(url=taskapi, files=files)
	print(resp.status_code)
	print(resp.text)


def demo_uploadfil6():
	taskapi = f"{BASE_URL}/upload5"
	file_patha = "./demoapi.py"

	byte = open(file_patha, 'rb')
	params = {"user": "paperclub", "password": 1234 }

	# resp = requests.post(url=taskapi, data={})
	## 方法2
	files = {'params':  json.dumps(params), 'a_file': byte  }
	resp = requests.post(url=taskapi, data=files)

	print(resp.status_code)
	print(resp.text)



def demo_uploadfil7():
	taskapi = f"{BASE_URL}/upload6"
	file_patha = "./demoapi.py"

	byte = open(file_patha, 'rb')
	params = {"user": "paperclub", "password": 1234}
	files = {'a_file': byte }
	resp = requests.post(url=taskapi,
	                     data={"params": json.dumps(params)},
	                     files=files,
	                     )

	print(resp.status_code)
	print(resp.text)


def demo_upload8():
	taskapi = f"{BASE_URL}/upload7"

	file_patha = "./demoapi.py"

	params = {
		"file_name": file_patha,
		"create_id": "ff5aac5d_c935_4a86_b356_bfe05f0e924c",
		"upload_names": ["pdf0.pdf", "pdf1.pdf"],
		"docment_type": "pdf",
		"dataset_type": "text",
		"language": "cn"
	}

	resp = requests.post(url=taskapi,
	                     data=json.dumps(params)
	                     )


	print(resp.status_code)
	print(resp.text)



def demo_post_imgbyte():
	taskapi = f"{BASE_URL}/post_imgbyte"

	file_patha = r"D:\linux_preject\project\meta_ago\app\resource\images\obj_min\p004358.jpg"
	
	params = {"file": file_patha}
	
	resp = requests.post(url=taskapi,
	                     data=params
	                     )

	
	print(resp.status_code)
	print(resp.content)
	
	import io
	from PIL import Image
	
	bytes_stream = io.BytesIO(resp.content)
	capture_img = Image.open(bytes_stream)
	capture_img.show()


def demo_post_list():
	""" 传递数组 """
	url = F"{BASE_URL}/post_list"

	data = {'file': [1234]}
	res = requests.post(url, data=json.dumps(data))
	print(res, res.json())

	data = {'file': 100 }
	res = requests.post(url, data=json.dumps(data))
	print(res, res.json())

	data = {'file': '123'}
	res = requests.post(url, data=json.dumps(data))
	print(res, res.json())


def demo_post_list2():
	""" Body 传递数组 """

	url = F"{BASE_URL}/post_list2"
	data = {'text': ['房间干净明亮', '非常不错']}
	res = requests.post(url, data=json.dumps(data))
	print(res, res.json())



def demo_get_query():
	url = f"{BASE_URL}/query_items"

	data = {'filename': '你好', "fileid": 111, 'inputs': [1,2,3,4]}
	res = requests.get(url, params=data)
	print(res, res.json())

def demo_post_query():
	url = f"{BASE_URL}/text_image_hits"
	text = "450㎡简约风别墅设计 这样的设计才叫格调"
	imgurl = "https://img0.baidu.com/it/u=3405212848,2275342701&fm=253&fmt=auto&app=138&f=JPEG?w=1266&h=500"

	res = requests.post(url, params={"text": text, "imgurl": imgurl})

	print(res.json())


def demo_post_params():
	query = "客厅"
	url = f"{BASE_URL}/vector/"

	resp = requests.post(url, params={"query": query})
	print(res.json())


if __name__ == '__main__':
	print()
	# demo_login()
	# demo_uploadfile1()
	# demo_uploadfile2()
	# demo_uploadfile3()
	# demo_uploadfile3x()
	# demo_uploadfile4()
	# demo_uploadfile5()
	# demo_uploadfil6()
	# demo_uploadfil7()
	# demo_upload8()
	# demo_post_list()
	demo_get_query()