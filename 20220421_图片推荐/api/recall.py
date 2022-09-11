# -*- coding:utf-8 -*-

import pickle
import torch
import json
import torchtext


""" pinage recall: 
    图片空间分类 + 图片特征 
"""

### 配置文件
data_pkl = '/data/1_qunosen/2022/pinsage/dhome2/data.pkl'
h_item_pkl = '/data/1_qunosen/2022/pinsage/dhome2/h_item.pkl'
img_dir = "/data/1_qunosen/2022/paddlerec/TwoToweRS-master/data/dHome/demo/imgs"
img_json = "/data/1_qunosen/2022/paddlerec/TwoToweRS-master/data/dHome/demo/imgs.json" 


def load_data():
    """ 加载数据 """
    with open(data_pkl, 'rb') as f:
        dataset = pickle.load(f)
        data_dict = {
                'graph': dataset['train-graph'],
                'val_matrix': dataset['val-matrix'],
                'test_matrix': dataset['test-matrix'],
                'testset': dataset['testset'],
                'item_texts': dataset['item-texts'],
                'item_images': dataset['item-images'],
                'user_ntype': dataset['user-type'],
                'item_ntype': dataset['item-type'],
                'user_to_item_etype': dataset['user-to-item-type'],
                'timestamp': dataset['timestamp-edge-column'],
                'user_category': dataset['user-category'],
                'item_category': dataset['item-category'],
            }
    
    with open(h_item_pkl, 'rb') as h:
        h_item = torch.cuda.FloatTensor(pickle.load(h)).cpu()
    with open(img_json, 'r') as jf:
        jdata  = json.loads(jf.read())
        jdata = {x["meadia_id"]: " ".join([x['space'],x['style']]) for x in jdata}
    data_dict = prepare_dataset(data_dict, None)

    return dataset, data_dict, h_item, jdata



def prepare_dataset(data_dict, args):
    g = data_dict['graph']
    item_texts = data_dict['item_texts']
    user_ntype = data_dict['user_ntype']
    item_ntype = data_dict['item_ntype']
    item_images = data_dict['item_images']
    # 分配人、物节点编号（同 df 索引）
    g.nodes[user_ntype].data['id'] = torch.arange(g.number_of_nodes(user_ntype))
    g.nodes[item_ntype].data['id'] = torch.arange(g.number_of_nodes(item_ntype))
    data_dict['graph'] = g

    # 增加文本集
    if item_texts is None:
        data_dict['textset'] = None
    else:
        fields = {}
        examples = []
        for key, texts in item_texts.items():
            fields[key] = torchtext.data.Field(include_lengths=True, lower=True, batch_first=True)
        for i in range(g.number_of_nodes(item_ntype)):
            example = torchtext.data.Example.fromlist(
                [item_texts[key][i] for key in item_texts.keys()],
                [(key, fields[key]) for key in item_texts.keys()])
            examples.append(example)
        textset = torchtext.data.Dataset(examples, fields)
        for key, field in fields.items():
            field.build_vocab(getattr(textset, key))
        data_dict['textset'] = textset
    
    # 图片特征
    if item_images is None:
        data_dict['img_vector'] = None
    else:
        data_dict['img_vector'] = item_images

    return data_dict


### 加载graph, 数据转换
dataset, data_dict, h_item, jdata = load_data()
g = data_dict['graph']
nid_dict = {cid.item(): nid.item() for cid, nid in zip(g.ndata['media_id']['media'], g.ndata['id']['media'])}
nid_iid_dict = {nid.item(): iid.item() for iid, nid in zip(g.ndata['media_id']['media'], g.ndata['id']['media'])}
category_dict = {iid:cid for cid,iid in data_dict['item_category'].items()}



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
        topk_i = node_to_item(node, nid_iid_dict, data_dict['item_category'])
        res.append(topk_i)
    
    return res

def recall(query:list = [ 6388555, 6388556], args_k = 5):

    """ 召回：
        query： 真实media_id list
    """

    try:
        nodes = item_to_node(query, category_dict, nid_dict)
        h_nodes = h_item[nodes]
        dist = h_nodes @ h_item.t()
        topk = dist.topk(args_k)[1].cpu().numpy().tolist() ### 索引
        topk = recall_node_to_item(topk)
    except Exception as ee:
        print(f"召回失败{query} : {ee}")
        topk = []
    
    
    return topk

