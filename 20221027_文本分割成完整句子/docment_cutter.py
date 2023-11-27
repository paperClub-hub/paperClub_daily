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


def segment(doc):
	""" 将文章根据标点符号进行句子拆分 """
	para = re.sub('([。！？\?])([^”’])', r"\1\n\2", doc)
	para = re.sub('([\.;])(\s)', r"\1\n\2", para)  # 英文断句
	para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
	para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
	para = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
	para = para.rstrip()
	return para.split("\n")

def clean(text: str):
	""" 文本清洗 """
	text = re.sub(r'[\t]+', ' ', text)
	text = re.sub(r'[ ]{2,}', ' ', text)
	text = re.sub(r'[\n]+', ' ', text)
	text = re.sub(r'[\n|\r]', ' ', text)
	return text.strip()


def cutoff(paras, max_len: int=1024):
	""" 句子截断 """
	num = 0
	bag, bag2 = [], []
	total_len, half_len = len("".join(paras)), int(max_len / 2)
	if total_len > max_len:
		for i, txt in enumerate(paras):
			num += len(txt)
			if num <= half_len:
				bag.append(txt)

			elif num > total_len - half_len:
				if txt not in bag:
					bag2.append(txt)

		if len("".join(bag + bag2)) > max_len:
			bag2 = bag2[1:]
		
		return "".join(bag + bag2)

	else:
		return "".join(paras)


text = """140㎡自然平层，低饱和色彩下的治愈之美 宏福樘设计。 与集 140㎡四室二厅 四川·成都 ━ 扩充原本封闭局限的玄关空间，于是拆除屹立于入户左侧的墙体。厨房内退，改造为与餐厅方正结合的开放式西厨，给予两人足够宽阔的视野与回家仪式感。 空间变得宽裕后，延右侧墙面进行规划与整合，设计2570mm*1170mmL型储物柜体，保证满足日常（未来）的鞋履、生活杂物、手办玩偶的存放。 独立中厨后，餐厅空间也进一步得到释放，但同时也承接了入户、西厨、客厅之间的视觉关系，是一处较重要的纽带。 定制岛台连接餐桌（选择与空间能够产生联结呼应的原木材质），用最小的占面，将功能进行呈现。不管是亲友聚餐，或是在西厨泡咖啡、制作轻食，还是得空在长凳上阅读书籍、临时办公，都能保证左右两侧宽裕的动线距离。 全屋大部分面积使用艺术漆呈现，加入更具雕塑感的顶面造型，收获更有东方美学意境的现代空间。 吧台也不同于大众化概念，入墙式水滴龙头代替常规洗手方式（考虑到此处日常使用率偏低，不如直接将其变为一种陈设装饰），利用特别的形态结构，增强了空间的艺术调性。不管是用餐模式还是细部的优化处理，都在这里被重新赋予新的涵义。 厨房分为两部分之后，内退与原始生活阳台合并使用，独立为中厨。调换动线后，由餐厅方向进入，门洞缩小为1190mm距离。选择轨道嵌入的玻璃口袋门替换推拉门，使得空间更为简洁、连贯。 优化内部生活需求，景观阳台一分为二，大部分给予客厅、卧室，扩充实际使用面积，最右侧则新建为独立生活设备区空间，利用隐形门进行遮挡，完整客厅视觉。 Hua与Lu对栽养植物有着十分的热情，所以留出1800mm*600mm的角落面积专门请植物造型师设计了一处室内端景。 空间满足不同的功能划分，定制与墙体连接感更强的一体桌面，抽屉及悬浮吊柜用于补充部分办公储物。其余柜体则以隐形式框架进行布局，让空间氛围不受过多的物品干扰，更加隐私、幽静。 生活场景与方式之间融合、切换，客房门廊改造为与柜面同材质的隐形门后，卫生间区域得到更具质感的视觉体验。 肌理丰富的艺术漆、结构精致的一体盆、现代与古典衔接而来的SINGCHAN吊灯，自然流动的光影，将其转变为美好事物的载体。烘托出相对私密高级感的同时，营造出丰盈、优雅的空间美学。 调整主卧衣帽间布局后，空间结构得以改换，获取到更丰富的自然光线，动线也更加便捷顺畅。 改造后的空间面积较为宽裕，为避免进入卧室便直接面对柜体背面的棱角感，对墙体造型进行优化，利用圆润流动的弧形设计感，弱化这一弊端。 保留主卧景观阳台，预留给Hua与Lu之后打造一处室外园景。空间大面积延续外部色调，局部素灰艺术漆与原木进行分色呈现。 考虑到房间需要一种更舒适、纯粹的入睡氛围，在挑选床品时放弃了成品的样式，选择与空间更匹配、素净的原木进行定制，表达出更温暖、更柔和的美好日常。 于柜体角落加入独立梳妆台，满足更多元化的使用功能。辅以一盏精致的玻璃吊灯聚焦氛围，自然质感与松弛愉悦，相互得到共鸣。 卫生间进行干湿分离，简洁无边玻璃隔断最大化体现空间的通透、宽敞感。选择外部同色调乳胶漆、瓷砖塑造基调氛围，通过细节的比例、材质的搭配关系，让Hua与Lu在日常使用时，获得惬意放松的空间情绪。 户型情况 140㎡四室两厅，这是Hua与Lu的第一套房子，同为建筑工程师的他们工作要求比较集中和精细，所以居住空间希望具备能够卸下紧绷的疲累感的环境氛围。 喜欢现代风格、自然植物，需保留四间卧室，以及足够的储物空间，未来的育儿计划也要考虑其中。 改造方案 ➊原始厨房拆改，一部分与生活阳台合并独立为中厨，一部分开放在外，进行个性化设计，改造为西厨 ➋ 景观阳台一半纳入客厅，扩充内部使用面积，生活阳台也移至此处，利用隐形门进行遮蔽 ➌客房调整门洞位置，与外部阳台合并，扩大储物、睡眠空间 ❹ 书房拆除部分墙体，更换为镂空、可开放设计 ❺ 主卧衣帽间拆除，布局进行调整，扩大收纳，加入独立梳妆台，优化动线 项目面积 140㎡ 项目风格 现代 项目户型 四室二厅 项目花费 60w 项目类型 全案设计+施工 项目团队 成都宏福樘设计 项目地址 成都 · 中建鹿溪澜岸"""
paras = segment(text)
text2 = cutoff(paras, max_len=512)
print(len(text2))
print(text2)

texts = """paperClub分享一款免费的强大办公工具。我们开发了一款简单的办公小工具，paperBox，下面给大家演示一下他的功能。这里主要涉及两种情况：

（1）图片直接进行等比缩放，图片缩放为原来的0.5倍，或 缩放为原来的2倍；

（2）需要固定图像的长和宽，同时保存图片不变形，如将原来 600 x 800的图片调整为宽 300， 高300，同时保持图片不变形和扭曲，这情况主要见于证件照缩放等应用场景。

（3）PaperClub shares a powerful free office tool. We have developed a simple office gadget, paperBox. Let's demonstrate its functions. There are mainly two situations involved here

"""

sentences = docment_cutter(texts)
for i, sentence in enumerate(sentences):
	print(f"第 {i+1} 句：{sentence}")


