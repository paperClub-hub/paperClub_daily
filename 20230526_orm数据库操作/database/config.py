#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-05-26 13:58
# @Author   : NING MEI
# @Desc     :


import os
from os.path import abspath, dirname, join
from dotenv import find_dotenv, load_dotenv

ROOT_DIR = abspath(join(dirname(abspath(__file__)), '../'))

system_variables = os.environ.get("USER", "dev")
env_name = f'.{system_variables}.env'
if os.path.exists(os.path.join(os.path.dirname(__file__), env_name)):
    load_dotenv(find_dotenv(filename=env_name))
else:
    load_dotenv(find_dotenv(filename=".env"))

MYSQL_USER = os.getenv('MYSQL_PC_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PC_PASSWORD', '123456')
MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
MYSQL_PORT = os.getenv('MYSQL_PORT', 3306)

