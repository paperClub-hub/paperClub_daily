# -*- coding:utf-8 -*-

import pickle
import torch
import json
import torchtext
from sentence_transformers import util

""" pinage recall: 
    拼趣 board + pin 
"""

### 配置文件
data_pkl = '/data/1_qunosen/2022/dhome/data/data.pkl'
h_item_pkl = '/data/1_qunosen/2022/dhome/text/pinsage/checkpoint/h_item_all.pkl'
json_path = '/data/1_qunosen/2022/dhome/text/pinsage/checkpoint/index_to_pinsin.json'


def load_data():
    """ 加载数据 """
    with open(data_pkl, 'rb') as f:
        dataset = pickle.load(f)
    
    with open(h_item_pkl, 'rb') as h:
        h_item = torch.cuda.FloatTensor(pickle.load(h)).cpu()
    
    with open(json_path, 'r') as jf:
        jdata  = json.loads(jf.read())
        

    return dataset,  h_item, jdata



### 加载graph, 数据转换
dataset, h_item, jdata = load_data()

g = dataset['train_graph']
nid_dict = {cid.item(): nid.item() for cid, nid in zip(g.ndata['image_id']['image'], g.ndata['image_id']['image'])}
nid_iid_dict = {nid.item(): iid.item() for iid, nid in zip(g.ndata['image_id']['image'], g.ndata['image_id']['image'])}
category_dict = {iid:cid for cid,iid in dataset['image_category'].items()}



def item_to_node(items, category_dict, nid_dict):
    """
    item id（真实media_id） 转 node id 
    @param items: node id list
    @param category_dict: {real item id: item category id}
    @param id_dict: { item category id: node id}
    """
    cids = [category_dict[i] for i in items]
    nids = [nid_dict[i] for i in cids]
    return nids


def node_to_item(nodes, id_dict, category_dict):
    """
    node id 转 item id
    @param nodes: node id list
    @param id_dict: {node id: item category id}
    @param category_dict: {item category id: real item id}
    """
    ids = [id_dict[i] for i in nodes]
    ids = [category_dict[i] for i in ids]
    return ids


def recall_node_to_item(topk):
    """ 通过节点获取 召回 index """
    res = []
    for node in topk:
        topk_i = node_to_item(node, nid_iid_dict, dataset['image_category'])
        res.append(topk_i)
    
    return res

def recall(query:list = [ 6388555, 6388556], args_k = 10):

    """ 召回：
        query： 真实media_id list
    """
    print("query:", query)
    try:
        
        nodes = query
        h_nodes = h_item[nodes]
        # dist = h_nodes @ h_item.t()
        # topk = dist.topk(args_k)[1].cpu().numpy().tolist() ### 索引

        cos_scores = util.cos_sim(h_nodes, h_item)[0]
        topk = [torch.topk(cos_scores, k=args_k)[1].cpu().numpy().tolist()]
        

        topk = recall_node_to_item(topk)
    except Exception as ee:
        print(f"召回失败{query} : {ee}")
        topk = []
    
    
    return topk
