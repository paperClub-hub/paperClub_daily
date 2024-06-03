#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2024-05-30 16:33
# @Author   : NING MEI
# @Desc     :

import time
import json
import requests


def do_test(text: str):
	PORT = 9912
	IP = '127.0.0.1'
	url = f"http://{IP}:{PORT}/doc_uie"
	data = {"doc": text}
	resp = requests.post(url, data=json.dumps(data))
	res = resp.json()

	return res


if __name__ == '__main__':
	text = """合肥中海观园 | 柏涛建筑 | 中国安徽合肥  探索公园式生态社区模式，提供开放社区、街区场景再造、
    人文关怀体验，成为城市未来发展的催化剂。
    项目试图探索一种全新的公园式生态综合社区的模式，希望在风景怡人的场地打造一处能够促进邻里交流的空间。
    项目位于合肥市包河区骆岗片区，项目紧邻骆岗机场（旧址），拥有城市珍贵的成长记忆。整体规划设计从机场汲取灵感，采用灵动飘逸的流线型元素，融入整体街区脉络，建立场地与城市的联结，传承旧机场的记忆，打造空中翱翔的理念及文化符号，构建出一个流畅、启程式的天际线。
    项目注重城市与环境的融合，融入对未来中央公园发展及整体街区脉络的理解，重新建立场地与城市的连接，塑造出生机勃勃的公园式社区场所，在城市中心呈现自然有机和生态，对话中央公园的自然景观，让自然与城市相互渗透。
    整体项目分为商业服务业设施、居住及幼儿园等一系列空间，设计试图探索一种全新的公园式生态综合社区的模式。该生态社区包括生态基底的塑造、开放社区、街区场景再造、人文关怀的体验。
    阶梯式建筑布置在中心创造了一处的城市枢纽式的社交空间，我们希望城市、建筑和景观彼此成就与互补，鼓励城市居民、旅客与周围环境及景观展开动态对话。
    建筑群的立面采用白色及银灰色线条打造流线型美学，呼应“航空”主题。
    丰富的建筑高度，让流动的“航空”主题得以延续，在银灰色线条的串联下，建筑与建筑之间也形成了彼此呼应的关系。
    作为室内、外空间的衔接点，全龄友好的架空层提供多元生活社区的场景空间。
    办公楼与商业大楼将居住区与繁忙的交通隔离开，创造出亲密静谧的内部环境。丰富的建筑群混合业态与静谧的居住氛围展现着都市魅力。
    立面注重各地块与城市界面的塑造，在易于感知的街区尺度中，植入适时的生活业态，为居者打造丰富多元的生活场景。
    将街道生活引入建筑内部，打造自由开放的街区。
    临街以融入城市肌理的商铺向邻里开放，缝补城市的功能，连续城市的界面。
    幼儿园立面融合流畅的横向曲线飘板造型以及活泼的几何立面造型，结合造型设计公共大台阶连接各层公共空间，为幼儿提供更多趣味性的成长游乐空间，打造一个在趣味玩乐中学习成长的幼儿园空间。
    项目强调了其对区域发展的积极影响，包括提升土地价值、塑造宜居环境、提供高品质生活方式、促进基础设施建设和产业发展，以及提升企业品牌形象。同时，项目的设计和规划注重创新性和可复制性，旨在为居民和城市提供长期的价值。
    项目档案
    项目名称: 合肥中海观园项目
    项目位置: 安徽合肥市
    业主单位: 中海地产
    建筑方案设计: 柏涛建筑设计（深圳）有限公司
    建筑施工图设计: 华东建筑设计研究院有限公司
    景观设计: 笛东规划设计(北京)股份有限公司
    用地面积:  47984.72  m²    
    项目摄影: 陈桂明"""


	print(do_test(text))

	import pandas as pd

	# csv_dir = "/data/1_qunosen/project/key_pharse/QAnything/my_test"
	# df1 = pd.read_csv(f"{csv_dir}/50套案例.csv", header=None, names=['url', 'title', 'doc'])
	# df2 = pd.read_csv(f"{csv_dir}/Untitled.csv", header=None, names=['url', 'title', 'doc'])
	# df = pd.concat([df1, df2]).reset_index(drop=True)
	# data = []
	# for i, row in enumerate(df.itertuples()):
	# 	url = row.url
	# 	title = row.title
	# 	doc = row.doc
	# 	try:
	# 		res1 = do_test(doc)
	# 		print(f"i = {i} ", "res1: ", res1)
	# 		data.append({"url": url, "res1": res1})
	# 	except Exception as error:
	# 		print(f"出错了，i={i} error={error}")
	#
	# data = pd.DataFrame(data)
	# data.to_csv("uie.csv", index=True)
