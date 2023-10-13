#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-09-04 11:04
# @Author   : NING MEI
# @Desc     :



import torch
import requests
from collections import defaultdict

" vearch 配置 "
MASTER_URL = 'http://127.0.0.1:18821'
ROUTER_URL = 'http://127.0.0.1:19005'
DB_NAME = "zhimo"
# SPACE_NAME = "medias3" # 知末，100w
# SPACE_NAME = "medias4" # 80w, 对应筑客pro线上的知末图片
SPACE_NAME = "medias5" # 筑客pro线上 + 知末100w,去重

" 服务端 配置"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
SERVER_HOST = '192.168.0.17'
SERVER_PORT = 8011

QUERY = '' # 搜索词
NUM_RECALL = 100
USE_PADDLE = False # 分词方法
USE_ZHUKE = False  # False : 知末数据， True： zhukepro 线上测试数据
USE_ZM80W = True # USE_ZHUKE == False有效， 使用知末80w，即筑客线上数据
MAX_SEQS_LEN = 3   # 点击序列保留长度
TIMESTAMPS = []
CLICK_SEQS = []

SEARCH_TIMES = 0 # 搜索次数
CLICK_INDEX = 0 # 点击在位置
SEARCH_CLICK_DIST = 1 # 无点击搜索次数，决定兴趣
LOG_DICT = defaultdict(dict) # 日志记录
