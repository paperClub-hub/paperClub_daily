

import pandas as pd
from collections import defaultdict
from py2neo import Graph,Node,Relationship,NodeMatcher, Subgraph




def init_neo4j():
    try:
        url = 'http://192.168.0.113:7474'
        # url = 'http://localhost:7474'
        graph = Graph(url,auth=("neo4j", "admin"))
        return graph
    except Exception as error:
        print(f"NinMEI neo4j connected with error: {error}")


NEO4J = None
if NEO4J is None:
    NEO4J = init_neo4j()



def to_neo4j(relations, text_id='text01'):
    # 文章编号
    article = NEO4J.nodes.match(text_id, name=text_id).first()
    if article is None:
        article = Node(text_id, name=text_id)
        NEO4J.create(article)

    # 创建节点和关系
    node_lis, rel_lis = [], []
    for label, vs in relations.items():
        vs = [[v[0], v[0]] if len(v) == 1 else v for v in vs]
        snodes = [v[0] for v in vs]  # 起点
        enodes = [v[-1] for v in vs]  # 终点

        for i, (snode,enode) in enumerate(zip(snodes, enodes)):
            if snode == enode: continue

            node1 = NEO4J.nodes.match(snode, name=snode).first()
            node2 = NEO4J.nodes.match(enode, name=enode).first()
            if node1 is None:
                node1 = Node(snode, name=snode)
                node_lis.append(node1)
                NEO4J.create(Subgraph([node1]))

            if node2 is None:
                node2 = Node(enode, name=enode)
                node_lis.append(node2)

                NEO4J.create(Subgraph([node2]))

            if node1 and node2:
                rel_a = Relationship(node1, label, node2)
                rel_b = Relationship(article, '包括', node1)
                rel_c = Relationship(article, '包括', node2)

                rel_lis.append(rel_a)
                rel_lis.append(rel_b)
                rel_lis.append(rel_c)


        rs = Subgraph(relationships=rel_lis)
        NEO4J.create(rs)


relations = {'场所类': [['客厅'], ['装修', '客厅'], ['卧室']],
 '风格类': [['简约风格'], ['北欧风格'], ['卧室', '北欧风格'], ['客厅', '现代简约风格']],
 '面积': [['88平米'], ['17平米'], ['卧室', '17平米'], ['客厅', '88平米'], ['4w+', '88平米']],
 '费用': [['4w'], ['卧室', '4w'], ['客厅', '4w+']]}

NEO4J.delete_all() # 清空数据库
to_neo4j(relations, 'text01')


