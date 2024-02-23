#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @ Date    : 2024/2/22 21:53
# @ Author  : paperClub
# @ Email   : paperclub@163.com
# @ Site    :

import os
import math
import time
import json
import itertools
import numpy as np
import pandas as pd
from glob import glob
from typing import List, Dict
from collections import deque
from functools import reduce
from orderedset import OrderedSet
from collections import defaultdict, Counter, OrderedDict

""" 序列生成 """


def get_aa_from_sequeces(sequences):
	dna2aa_map = {'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L', 'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
	              'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M', 'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
	              'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S', 'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
	              'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T', 'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
	              'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*', 'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
	              'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K', 'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
	              'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W', 'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
	              'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R', 'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'}

	def dna2aa(dna: str, codon_dict: Dict):
		"""密码子转氨基酸"""
		return codon_dict.get(dna.upper())

	def seq2codons(seq: str):
		"""强制序列转密码子"""
		seq = seq.upper().replace("U", "T")
		triple = len(seq) % 3
		if triple > 0:
			seq = seq[: -triple]

		codons, kmer_len, gap = [], 3, 3
		for j in range(0, (len(seq) - kmer_len) + 1, gap):
			token = seq[j: j + kmer_len]
			codons.append(token)

		return codons

	data = []
	for i, seq in enumerate(sequences):
		codons = seq2codons(seq)
		aa_seq = "".join([dna2aa(d, dna2aa_map) for d in codons])
		data.append(aa_seq)

	return data


def gen_combineation(seq_lst: List):
	""" 基于迭代器的生成 """
	res = []
	coms = list(itertools.product(*seq_lst))
	for item in coms:
		item = list(item)
		res.append(item)

	return res


def gen_candicates_with_bfs(seq_lst: List):
	""" 基于广度搜索算法BFS进行的候选序列
	seq_lst 列表元素
	Args:
		seq_lst: 如[['A1', 'B1', 'C1'], ['A2', 'B2'], ['A3'], ['A4', 'B4'], ['A5']]
	Returns:

	"""

	def encoder(seq_lst):
		res, dic = [], {}
		num = 0
		for item in seq_lst:
			pv = [str(i + num) for i in range(len(item))]
			res.append(pv)
			for i, p in enumerate(pv):
				dic[p] = item[i]
			# print(pv, item)
			num += len(item)

		return res, dic

	def get_graph(seq_lst: List):
		""" 创建graph """
		N_starts = seq_lst[0]
		N_ends = seq_lst[-1]
		my_graph = OrderedDict()

		for i in range(len(seq_lst) - 1):
			nodes1 = seq_lst[i]
			nodes2 = seq_lst[i + 1]
			# 创建graph图
			for s in nodes1:
				my_graph[s] = nodes2

			# 处理最后一个
			if i == (len(seq_lst) - 2):
				last_nodes = nodes2
				for l in last_nodes:
					my_graph[l] = nodes1

		return my_graph, N_starts, N_ends

	def bfs(start, end):
		""" 广度优先搜索（BFS）"""
		# 记录所有路径的集合
		paths = set()
		# 记录当前路径
		current_path = [start]
		# 使用队列来进行BFS
		queue = deque([(start, [start])])

		while queue:
			# 左侧删除元素，剩余元素
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

	# 生成序列
	data = []
	counter_lst = [len(n) for n in seq_lst]
	max_num = reduce(lambda x, y: x * y, counter_lst)

	seq_lst_encode, dic = encoder(seq_lst)
	graph, start_nodes, end_nodes = get_graph(seq_lst_encode)
	for start_node in start_nodes:
		for end_node in end_nodes:
			all_paths = bfs(start_node, end_node)
			for p in all_paths:
				# print(p)
				if len(p) != len(seq_lst):
					continue

				seq = [dic.get(id) for id in p]
				data.append(seq)

	del start_nodes, end_nodes, seq_lst

	print(f"max_num: {max_num}, data: {len(data)}")

	return data


def beam_search(nodes, topk=1):
	# log-likelihood可以相加
	# 起点 - 第一个点
	paths = {'A': math.log(nodes[0]['A']), 'B': math.log(nodes[0]['B']), 'C': math.log(nodes[0]['C'])}
	print("paths: ", paths)

	calculations = []
	for l in range(1, len(nodes)):
		# 拷贝当前路径
		paths_ = paths.copy()
		paths = {}
		nows = {}
		cur_cal = 0
		for i in nodes[l].keys():
			# 计算到达节点i的所有路径
			for j in paths_.keys():
				nows[j + i] = paths_[j] + math.log(nodes[l][i])
				cur_cal += 1
		calculations.append(cur_cal)
		# 选择topk条路径
		indices = np.argpartition(list(nows.values()), -topk)[-topk:]
		# 保存topk路径
		for k in indices:
			paths[list(nows.keys())[k]] = list(nows.values())[k]

	print(f'calculation number {calculations}')
	return paths


# nodes = [{'A':0.1, 'B':0.3, 'C':0.6}, {'A':0.2, 'B':0.4, 'C':0.4}, {'A':0.6, 'B':0.2, 'C':0.2},
#          {'A': 0.3, 'B': 0.3, 'C': 0.4}]
#
# print(beam_search(nodes, topk=2))

if __name__ == '__main__':
	print()
	# seq_lst = [['GGT', 'GGC', 'GGA', 'GGG'], ['AAA', 'AAG'], ['GCT', 'GCC', 'GCA', 'GCG'],
	#            ['TTA', 'TTG', 'CTT', 'CTC', 'CTA', 'CTG'], ['ATT', 'ATC', 'ATA'], ['ACT', 'ACC', 'ACA', 'ACG'],
	#            ['GGT', 'GGC', 'GGA', 'GGG'], ['GAC'], ['TAA', 'TAG', 'TGA'], ['GAT', 'GAC'], ['TAC'],
	#            ['GTT', 'GTC', 'GTA', 'GTG'], ['TTT', 'TTC'], ['TTA', 'TTG', 'CTT', 'CTC', 'CTA', 'CTG'],
	#            ['GGT', 'GGC', 'GGA', 'GGG'], ['AAT', 'AAC'], ['TGG'], ['AAT'], ['AAC'], ['CCA'], ['TAC'], ['CAG']]
	# seq_lst = seq_lst[: 4]
	seq_lst = [
		['a1', 'a2', 'a3'],
		['b1', 'b2'],
		['c1', 'c2', 'c3', 'c4']
	]

# g1 = gen_combineation(seq_lst)
# print(g1)

# g2 = gen_candicates_with_bfs(seq_lst)
# print(g2)










