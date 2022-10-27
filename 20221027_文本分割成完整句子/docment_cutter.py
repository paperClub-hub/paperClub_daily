#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-10-27 18:01
# @Author   : paperClub
# @Desc     :




import re
from typing import List
def docment_cutter(sentences: str) -> List:
	""" 将一篇文章分割成多条完成的句子。"""
	sentences = re.sub('([。！？\?])([^”’])', r"\1\n\2", sentences)
	sentences = re.sub('([\.;])(\s)', r"\1\n\2", sentences) # 英文断句
	sentences = re.sub('(\.{6})([^”’])', r"\1\n\2", sentences)  # 英文省略号
	sentences = re.sub('(\…{2})([^”’])', r"\1\n\2", sentences)  # 中文省略号
	sentences = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', sentences)
	sentences = sentences.rstrip()

	return list(filter(bool, sentences.split("\n")))



texts = """paperClub分享一款免费的强大办公工具。我们开发了一款简单的办公小工具，paperBox，下面给大家演示一下他的功能。这里主要涉及两种情况：

（1）图片直接进行等比缩放，图片缩放为原来的0.5倍，或 缩放为原来的2倍；

（2）需要固定图像的长和宽，同时保存图片不变形，如将原来 600 x 800的图片调整为宽 300， 高300，同时保持图片不变形和扭曲，这情况主要见于证件照缩放等应用场景。

（3）PaperClub shares a powerful free office tool. We have developed a simple office gadget, paperBox. Let's demonstrate its functions. There are mainly two situations involved here

"""

sentences = docment_cutter(texts)
for i, sentence in enumerate(sentences):
	print(f"第 {i+1} 句：{sentence}")


