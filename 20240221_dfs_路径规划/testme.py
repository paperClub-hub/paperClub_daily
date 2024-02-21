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

# 测试函数
start_node = 'A'
end_node = 'F'

all_paths = dfs(start_node, end_node)
all_paths = dfs_paths(start_node, end_node)
all_paths = bfs_paths(start_node, end_node)
for path in all_paths:
	print(path)

