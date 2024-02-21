#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2024-02-21 13:24
# @Author   : NING MEI
# @Desc     :


"""
起点A -》 终点F有多个节点，每个节点都多个选择。请生成可能得全部路径
"""

# 定义路径图结构
graph = {
    'A': ['B', 'C'],  # 从A节点可以到达B或C节点
    'B': ['A', 'C', 'D'],  # 从B节点可以到达A或C节点或D节点
    'C': ['A', 'B', "E"],   # 从C节点可以到达A或B节点或E节点
	'D': ['E', 'B'],  # 从D节点可以到E节点或B节点
	'E': ['C', 'F'],  # 从C节点可以到C节点或F节点
	'F': ['A']   # 从F节点可以到A节点
}


def dfs(start, end, path=None):
	if path is None:
		path = [start]
	if start == end:
		return [path]
	if start not in graph:
		return []
	paths = []
	for node in graph[start]:
		if node not in path:  # 避免重复访问节点
			newpaths = dfs(node, end, path + [node])
			for newpath in newpaths:
				paths.append(newpath)
	return paths


# 测试函数
start_node = 'A'
end_node = 'F'

all_paths = dfs(start_node, end_node)
for path in all_paths:
	print(path)

