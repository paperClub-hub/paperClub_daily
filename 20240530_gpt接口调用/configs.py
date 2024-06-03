#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2024-03-15 13:34
# @Author   : NING MEI
# @Desc     :

import os
import json
import requests
from dotenv import load_dotenv, find_dotenv


load_dotenv()

def get_access_token():
	API_Key = os.getenv("API_Key")
	Secret_Key = os.getenv("Secret_Key")
	url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_Key}&client_secret={Secret_Key}"
	payload = json.dumps("")
	headers = {'Content-Type': 'application/json','Accept': 'application/json'}
	response = requests.request("POST", url, headers=headers, data=payload)
	return response.json().get("access_token")


# ------------------------   prompt模版设置  ------------------------------- #
PROMPT1 = """参考信息：
{context}
---
我的问题或指令：
{question}
---
请根据上述参考信息回答我的问题或回复我的指令。前面的参考信息可能有用，也可能没用，你需要从我给出的参考信息中选出与我的问题最相关的那些，来为你的回答提供依据。回答一定要忠于原文，简洁但不丢信息，不要胡乱编造。我的问题或指令是什么语种，你就用什么语种回复,
你的回复："""


PROMPT2 = """参考信息：
{context}
---
我的问题或指令：
{question}
---
请从上述文本中精准提取我要的关键词字段信息，结果简洁并严格按照键值对形式给出结果，你需要精准识别并准确提取，提取结果以键值对形式返回，如果前面的文本中找不到要提取的信息，对应字段不用给出，也不回解释。
你的回复："""
