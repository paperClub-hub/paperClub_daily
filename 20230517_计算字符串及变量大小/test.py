#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-05-16 19:14
# @Author   :
# @Desc     :


import numpy as np


def convert_size(inputs):
	"""
    文件大小单位换算
    :text: 文件字节
    :return: 返回字节大小对应单位的数值
    """

	def formatter(text):
		units = ["B", "KB", "MB", "GB", "TB", "PB"]
		size = 1024
		for i in range(len(units)):
			if (text / size) < 1:
				return "%.2f %s" % (text, units[i])  # 返回值保留小数点后两位
			text = text / size


	if isinstance(inputs, np.ndarray):
		inputs_bytes = inputs.nbytes

	elif isinstance(inputs, list):
		inputs = np.array(inputs)
		inputs_bytes = inputs.nbytes

	elif isinstance(inputs, str):
		inputs = bytes(inputs.encode('utf-8'))
		inputs_bytes = inputs.__sizeof__()

	elif isinstance(inputs, bytes):
		inputs_bytes = inputs.__sizeof__()

	else:
		inputs = bytes(str(inputs).encode('utf-8'))
		inputs_bytes = inputs.__sizeof__()

	print("大小: ", inputs_bytes, " ===>> ",  formatter(inputs_bytes))



inputs = "&&a1asdasfvsasd"

print(convert_size(inputs))
