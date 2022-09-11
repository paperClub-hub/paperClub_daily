#!/usr/bin/python
# coding=utf-8

import time,os,json
import keyphrase


"""
目的：提取文章摘要/正文关键词；
日期：2021-01-19, 初次创建

"""



def get_key_words(text, allow_length_weight=True, topic_theta=0.5, max_phrase_len=10):
	article_remove_words_list = ['剧照', '作者', '下方', 'TEL', 'COM', '们', '再', '时', '分公司', '董事长', '情况', '女孩儿']
	article_remove_phrases_list = ['剧照曹雪芹', '项目简介项目名称', '科技有限公司青岛鸿源', "总经理黄晓华青岛南华", '设计师人手']
	
	extractor_obj = keyphrase.extractor()
	
	key_words = extractor_obj.extract_keyphrase(text,
												topic_theta=topic_theta,
												max_phrase_len=max_phrase_len,
												allow_length_weight=allow_length_weight,
												remove_phrases_list=article_remove_phrases_list,
												remove_words_list=article_remove_words_list,
												)
	
	return key_words





	
	


if __name__ == "__main__":
	start = time.time()
	
	extractor_obj = keyphrase.extractor()
	
	con_text = """
	据国外媒体报道，当处于相当于1亿颗超新星爆发产生的能量的情况下，引力波或许可以将超大质量黑洞从遥远星系中央弹射出来。近日，哈勃望远镜观测到目前最大的一个黑洞正处于星系核外部，这个黑洞的质量是太阳质量的数十亿倍。天文学家们推测这个“怪物天体”可能是由于两个黑洞合并，释放出能量巨大的引力波，从而被踢出星系中央。
	NASA表示，这个发现非比寻常。太空望远镜科学研究所（STScI）的Marco Chiaberge表示，我第一次看到这个的时候，我还以为这只是个个例。后来我们结合了哈勃、钱德拉X射线望远镜、以及斯隆数字巡天的观测结果，发现都是同样的结果。根据我们收集的所有数据，从X射线到紫外线到近红外线，所有数据均表明这个黑洞比其他流浪黑洞要大得多。哈勃望远镜的可见光和近红外线观测发现一个名为3C 186的明亮类星体位于一个距离地球80亿光年外的星系中。不过，这个天体却离星系核很远。
	黑洞通常位于星系中央，因此类星体不在星系中央很不寻常。研究者进一步调查了该现象，通过将宿主星系中的恒星光线的分布情况与一个正常的椭圆星系相比较，来计算黑洞距离星系核的距离，从而得出大约是3.5万光年，比太阳距银河系中央的距离还远。
	哈勃望远镜与斯隆数字巡天望远镜的光谱分析能够让研究团队估算出黑洞的质量，以及黑洞下气体的速度。STScl的Justin Ely表示，出于意料的是，我们发现黑洞周围的气体逃离星系中央的速度大约是4700万英里/小时。这些数据表明，黑洞远离星系中央的速度极快，以这种速度都地球到月球仅需3分钟。
	哈勃望远镜拍摄图像中的昏暗的弧形状物体表明引力拖拽作用或许对黑洞的异常移位也有关。这些物质是由两个相互碰撞的星系间产生的引力拖拽作用产生的，研究者表示，3C 186星系可能跟另一个系统合并了，而它们的中央黑洞也随之合并。当两个超大质量黑洞碰撞时，会产生出引力波，这可能会导致新形成的黑洞朝与引力波相反的方向回弹，像火箭升空一样。
	"""
	
	key_phase = get_key_words(con_text)
	
	print(key_phase)
	
	end1 = time.time()
	print("关键词提取时间：{}".format(end1 - start))
	
	

