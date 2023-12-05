#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-10-30 14:52
# @Author   : NING MEI
# @Desc     :


import argparse
from typing import Dict
from datetime import datetime

def task(args: Dict):
	""" 业务代码 """
	config = args.get('config')
	gpu = args.get('gpu')
	expid = args.get('expid')
	print(f"task_run {datetime.now()}, expid: {expid}, config: {config}, gpu:{gpu} ")


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--config', type=str, default='./config/', help='The config directory.')
	parser.add_argument('--expid', type=str, default='test_1', help='The experiment id to run.')
	parser.add_argument('--gpu', type=int, default=-1, help='The gpu index, -1 for cpu')
	args = vars(parser.parse_args())
	# args = parser.parse_args()
	# print(args)
	task(args)