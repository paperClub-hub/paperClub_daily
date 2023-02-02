#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte :
# @Date     : 2023-02-02 15:49
# @Author   : paperclub@163.com
# @Desc     :


import sys
from os.path import abspath, dirname
sys.path.append(abspath(dirname(__file__)))
import json
from typing import List
import recognizers_suite as Recognizers
from recognizers_suite import Culture, ModelResult
import langid



def is_cn(strs):
	"""语言检测： 是否为中文"""
	# for i in strs:
	# 	if not '\u4e00' <= i <= '\u9fa5':
	# 		return False

	if langid.classify(strs)[0] != "zh":
		return False

	return True


def parse(strs: str) -> List[List[ModelResult]]:
	""" 强制转为中英文模式 """

	culture = Culture.Chinese if is_cn(strs) else Culture.English
	res = [
	        Recognizers.recognize_number(strs, culture), # 数值提取， E.g "I have two apples" will return "2".
	        Recognizers.recognize_ordinal(strs, culture),  # 序号提取，# E.g "eleventh" will return "11".
	        Recognizers.recognize_percentage(strs, culture),  # 百分数提取， E.g "one hundred percents" will return "100%"
			Recognizers.recognize_age(strs, culture), # 年龄提取， E.g "After ninety five years of age, perspectives change" will return 95 Year
	        Recognizers.recognize_currency(strs, culture),  # 现金货币提取, # E.g "Interest expense in the 1988 third quarter was $ 75.3 million"
	        Recognizers.recognize_dimension(strs, culture),  # 距离提取， "The six-mile trip to  airport“   return "6 Mile"
			Recognizers.recognize_temperature(strs, culture), # 温度提取， "Set the temperature to 30 degrees celsius" will return "30 C"
	        Recognizers.recognize_datetime(strs, culture),
	        Recognizers.recognize_phone_number(strs, culture),
	        Recognizers.recognize_email(strs, culture),
    ]


	data = json.dumps(res, default=lambda o:o.__dict__, indent='\t', ensure_ascii=False)

	del res, strs
	return data



if __name__ == '__main__':
	text = "第八届比赛：年轻人“胆大包天”！设计师夫妻的80㎡LOFT！2020.09"

	print(parse(text))

