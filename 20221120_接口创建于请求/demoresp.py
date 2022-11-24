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



if __name__ == '__main__':
	print()
	# demo_login()
	# demo_uploadfile1()
	# demo_uploadfile2()
	# demo_uploadfile3()
	# demo_uploadfile3x()
	# demo_uploadfile4()
	# demo_uploadfile5()
	demo_uploadfil6()
	# demo_uploadfil7()