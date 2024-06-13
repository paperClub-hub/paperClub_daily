#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2024-06-12 17:32
# @Author   : NING MEI
# @Desc     :


import cv2
import time
from ocr import OCR_Engine
from typing import Callable
from paddleocr import PaddleOCR
from rapidocr_onnxruntime import RapidOCR

def use_rapid_ocr_engine(img):
	res = rapid_ocr_engine(img)
	return res

def use_paddle_ocr_engine(img):
	res = paddle_ocr_model.ocr(img)
	return res

def use_ocrserver_engine(img):
	res = OCR_Engine(img)
	return res

def test_ocr(funs: Callable, img, num = 2):
	t1 = time.perf_counter()
	for _ in range(num):
		res = funs(img)

	t2 = time.perf_counter()
	time_cost = t2 - t1
	print(f"funs: {funs}, 测试 {num}次, 耗时: {time_cost}")


### 其他时间统计方法
def demo():

	############### 方法1
	import timeit
	num = 1000
	your_code = """"""
	timer = timeit.Timer(stmt=your_code)
	exec_time = timer.timeit(number=num) # 执行num次消耗时间

	############### 方法2
	import cProfile
	def your_function():  # 在这里放置你要测量的代码
		""""""
	cProfile.run('your_function()')

	############### 方法3
	# pip install line_profiler
	from line_profiler import LineProfiler
	lp = LineProfiler()

	@lp.profiledef
	def your_function():
		"""在这里放置你要测量的代码"""

	your_function()
	lp.print_stats()


paddle_ocr_model = None
if paddle_ocr_model is None:
	paddle_ocr_model = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=True, show_log=False)

rapid_ocr_engine = None
if rapid_ocr_engine is None:
	rapid_ocr_engine = RapidOCR()

num = 5
file_path = "../test.jpg"
img_array = cv2.imread(file_path)
test_ocr(use_rapid_ocr_engine, img_array, num)
test_ocr(use_paddle_ocr_engine, img_array, num)
test_ocr(use_ocrserver_engine, img_array, num)
