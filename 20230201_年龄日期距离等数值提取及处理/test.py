#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-01-03 12:30
# @Author   : paperclub@163.com
# @Desc     :




import msprocess.extractor as model


texts = [
	"Percentage recognizer - This function will find any number presented as percentage",
	"无边设计 2022打开法式风格的第101种可能—油画仙境般的家"
]

for t in texts:
	print("输入：", t)
	print(model.parse(t))
	print("*****************************")


