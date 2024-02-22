#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2024-02-21 13:24
# @Author   : NING MEI
# @Desc     :


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @ Date    : 2024/1/27 7:59
# @ Author  : paperClub
# @ Email   : paperclub@163.com
# @ Site    :

import math
import pandas as pd
from typing import List, Dict
from collections import deque
from orderedset import OrderedSet
from collections import defaultdict, Counter, OrderedDict




def testme():
	task_data = {'sequence': 'GGAAAAGCTCTAATAACAGGAGACTAGGACTACGTATTTCTAGGTAACTGGAATAACCCATACCAGCA',
	            'codons': ['GGA', 'AAA', 'GCT', 'CTA', 'ATA', 'ACA', 'GGA', 'GAC', 'TAG', 'GAC', 'TAC', 'GTA', 'TTT',
	                       'CTA', 'GGT', 'AAC', 'TGG', 'AAT', 'AAC', 'CCA', 'TAC', 'CAG'],
	            'aa': 'GKALITGD*DYVFLGNWNNPYQ',
	            'dindex': [2, 4, 6, 8, 9, 11, 13, 14, 15, 16, 17, 20, 27, 30, 36, 37, 38, 39, 40, 45, 46, 47, 48, 49],
	            'cindex': [0, 1, 2, 3, 4, 5, 6, 8, 9, 11, 12, 13, 14, 15, 16]}

	dna2aa_map = {'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L', 'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L', 'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M', 'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V', 'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S', 'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P', 'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T', 'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A', 'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*', 'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q', 'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K', 'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E', 'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W', 'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R', 'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R', 'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'}
	aa2name_map = {'A': '丙氨酸(Alanine)', 'R': '精氨酸(Arginine)', 'D': '天冬氨酸(Aspartic acid)', 'C': '半胱氨酸(Cysteine)', 'Q': '谷氨酰胺(Glutamine)', 'E': '谷氨酸(Glutamic acid)', 'H': '组氨酸(Histidine)', 'I': '异亮氨酸(Isoleucine)', 'G': '甘氨酸(Glycine)', 'N': '天冬酰胺(Asparagine)', 'L': '亮氨酸(Leucine)', 'K': '赖氨酸(Lysine)', 'M': '甲硫氨酸(Methionine)', 'F': '苯丙氨酸(Phenylalanine)', 'P': '脯氨酸(Proline)', 'S': '丝氨酸(Serine)', 'T': '苏氨酸(Threonine)', 'W': '色氨酸(Tryptophan)', 'Y': '酪氨酸(Tyrosine)', 'V': '缬氨酸(Valine)', '*': '终止密码子(STOP)'}

	def dna2aa(dna: str, codon_dict: Dict):
		"""密码子转氨基酸"""
		return codon_dict.get(dna.upper())

	def dna2codons(dna: str, codon_dict: Dict):
		""" 根据密码子获取获取同义密码子 """
		aa2codon_map = defaultdict(list)
		for k, v in codon_dict.items():
			aa2codon_map[v].append(k)

		dna = dna.upper()
		# print(aa2codon_map)
		aa = dna2aa(dna, codon_dict)
		codons = aa2codon_map.get(aa, [])
		# print(codons)
		return codons


	# 序列密码子列表
	seq_codons = task_data.get('codons')
	# 序列处理的密码子位置
	cindex = task_data.get('cindex')
	# 根据对应位置密码子获取同义密码子映射dict
	index2codon_map = {}
	dna2postion_map = OrderedDict() # 密码子位置索引
	num = 0
	for index in range(len(seq_codons)):
		dna = seq_codons[index]
		if index in cindex:
			codons = dna2codons(dna=dna, codon_dict=dna2aa_map)
		else:
			codons = [dna]

		pindex = []
		for i, c in enumerate(codons):
			p = num + i
			dna2postion_map[p] = (index, i)
			pindex.append(p)

		num +=len(codons)
		index2codon_map[index] = codons

	# print("dna2postion_map: ", dna2postion_map)


	## 方法1：使用递归算法：
	def get_seq_by_index(index, sim_dnas, seq_codons: List):
		""" 根据指定位置dna和密码子，生成序列 """
		res = []
		for dna in sim_dnas:
			seq = [dna if i == index else x for i, x in enumerate(seq_codons)]
			res.append(" ".join(seq))
		return res

	def get_seq_by_indexes(cindex, seq_codons: List):
		"""用用序列-密码子 生成全部的候选序列"""
		data = set()
		dnas = list(map(lambda i: seq_codons[i], cindex))
		for index, dna in zip(cindex, dnas):
			sim_dnas = dna2codons(dna=dna, codon_dict=dna2aa_map)
			if sim_dnas:
				seqs = get_seq_by_index(index, sim_dnas, seq_codons)
				data.update(seqs)

		return list(data)

	def gen_candicats_with_codons(cindex: List=None, seq_codons: List=None):
		""" 生成方法1 """
		codon2codons = get_seq_by_indexes(cindex, seq_codons)
		codon2codons = [c.split() for c in codon2codons]
		codon2codons.append(seq_codons)

		res =set()
		for c in codon2codons:
			seqs = get_seq_by_indexes(cindex, c)
			for seq in seqs:
				res.add("".join(seq.split()))

		return len(res), list(res)

	gen_seqs = gen_candicats_with_codons(cindex, seq_codons)
	print("gen_seqs: ", gen_seqs)


	# 根据密码子构建 index-postion映射dict
	## TODO: 计划使用深度优先算法DFS进行
	# postion2dna_map = {v: k for k, v in dna2postion_map.items()}
	# print("postion2dna_map: ", len(postion2dna_map)== len(dna2postion_map))
	# # 根据位置构建grraph
	# # graph = OrderedDict()
	# # print('index2codon_map: ', index2codon_map)
	# data = []
	# for p, lst in index2codon_map.items():
	# 	vst = [postion2dna_map.get((p, i)) for i, c in enumerate(lst)]
	# 	# print("p, lst: vst", p, lst, vst)
	# 	data.append(vst)
	# 	# print(vst)
	# # print("data: ", data)
	#
	# # graph = {}
	# for i in range(len(data) - 1):
	# 	p1 = data[i]
	# 	p2 = data[i + 1]
	# 	for ip1 in p1:
	# 		graph[ip1] = p2
	# 	# print(p1, "-- ", p2)
	# print("graph: ", graph)
	# all_paths = dfs_paths(0, 58)
	# print(all_paths)





def dfs_paths(start, end, path=None):
	""" 深度优先搜索（DFS）
	使用DFS生成从start到end的所有路径
	:param start: 起点
	:param end: 终点
	:param path: 当前路径，默认为None
	:return: 所有路径的列表
	"""
	# 如果路径为None，则初始化为只包含起点的列表
	if path is None:
		path = [start]
	# 如果当前节点是终点，则将路径添加到结果中
	if start == end:
		return [path]
	# 如果当前节点没有邻居或者已经是死路，则返回空列表
	if start not in graph:
		return []
	# 递归遍历当前节点的所有邻居
	paths = []
	for node in graph[start]:
		# 避免重复访问已经在路径中的节点
		if node not in path:
			# 递归调用dfs_paths，并将当前节点添加到路径中
			new_paths = dfs_paths(node, end, path + [node])
			# 将找到的新路径添加到结果中
			for new_path in new_paths:
				paths.append(new_path)
	return paths


def bfs_paths(start, end):
	""" 广度优先搜索（BFS） """
	# 记录所有路径的集合
	paths = set()
	# 记录当前路径
	current_path = [start]
	# 使用队列来进行BFS
	queue = deque([(start, [start])])

	while queue:
		node, path = queue.popleft()
		# 如果到达终点，将当前路径添加到结果中
		if node == end:
			paths.add(tuple(path))
		else:
			# 遍历当前节点的所有邻居
			for neighbor in graph[node]:
				# 如果邻居节点未被访问过，则将其加入队列并更新当前路径
				if neighbor not in path:
					queue.append((neighbor, path + [neighbor]))

	return list(paths)




# 定义图结构
graph = {
    'A': ['B', 'C'],  # 从A节点可以到达B或C节点
    'B': ['A', 'C'],  # 从B节点可以到达A或C节点
    'C': ['A', 'B']   # 从C节点可以到达A或B节点
}


# 测试函数
start_node = 'A'
end_node = 'C'
all_paths = bfs_paths(start_node, end_node)
# all_paths = dfs_paths(start_node, end_node)

# # 输出所有路径
# for path in all_paths:
# 	print(path)


if __name__ == '__main__':
	print()
	testme()
