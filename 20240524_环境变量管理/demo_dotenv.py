#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2024-05-23 10:50
# @Author   : NING MEI
# @Desc     :

""" pip install python-dotenv """

import os
import json
import requests
from os.path import exists, abspath, dirname
from dotenv import load_dotenv, find_dotenv

_pwd = abspath(dirname(__file__))
def key_init():
	env_dev_path = f"{_pwd}/.env_dev"
	if exists(find_dotenv(env_dev_path)):
		load_dotenv(env_dev_path)
	else:
		print(".env_dev 不存在")
		load_dotenv()

key_init()

KEY1 = os.getenv("KEY1")
KEY2 = os.getenv("KEY2")
KEY3 = os.getenv("KEY3")


print(f"KEY1: {KEY1}, {type(KEY1)}， KEY2: {KEY2}, {type(KEY2)}, KEY3: {KEY3}, {type(KEY3)}")
