#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-10-17 8:55
# @Author   : NING MEI
# @Desc     :


import os
import LAC
import time
import jieba
import re, json
import pandas as pd
from pprint import pprint
from typing import List, Dict
from paddlenlp import Taskflow
from typing import Dict, List, Union
from collections import defaultdict
import requests
from bs4 import BeautifulSoup




def get_desc(url):
    """ 获取建E文本描述 """

    result = {}
    headers = {
        "User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; Tablet PC 2.0; wbx 1.0.0; wbxapp 1.0.0; Zoom 3.6.0)",
        "X-Amzn-Trace-Id": "Root=1-628b672d-4d6de7f34d15a77960784504"
    }

    time.sleep(1)
    resp = requests.get(url, headers=headers, timeout=3)
    if resp.status_code == 200:
        data = resp.text
        soup = BeautifulSoup(data, 'html.parser')

        title_name = re.findall('<h1 class="tit">(.*?)</h1>', data)
        tags = soup.find(name='div', class_='labels-box').text.split()
        tags = ",".join(tags)
        desc = soup.find(name='div', class_='cont', id='container').get_text()
        result.update({
            "id": os.path.splitext(os.path.basename(url))[0],
            "name": title_name,
            "tags": tags,
            "desc": desc
        })

    resp.close()

    del resp

    return result



class je_parser():

    def __init__(self) -> None:

        self.configs = self._load_json("./je_config.json")  # 全部配置信息
        self.project_templates = self.configs.get('project_templates')
        baser_ie_schema = ['户型', '面积', '装修风格']
        base_ie_model = Taskflow(task='information_extraction', schema=list(self.project_templates.keys()))
        fine_ie_model = Taskflow(task='information_extraction', schema=baser_ie_schema,
                                 task_path="/data/1_qunosen/project/key_pharse/uie/checkpoint/uie_mdoels/20220907/best2_0.719")
        self.base_ie_model = base_ie_model
        self.fine_ie_model = fine_ie_model

    def _load_json(self, file_path: str):
        return json.load(open(file_path, 'r'))


    def _uie_postprocess(self, target_res, threshold: float = None, reform: bool = True):
        """ uie 抽提结果过滤处理 """

        target_res = target_res[0]
        if target_res:
            if reform:  # 用于生成实体及关系三元组
                ners = defaultdict(list)  # 实体
                relations = []  # 关系三元组
                for k, kv in target_res.items():
                    items = list(filter(lambda x: x.get('probability') > threshold, kv)) if threshold else kv
                    ners[k].extend([item.get('text') for item in items])
                    rel_items = list(filter(lambda x: 'relations' in x, items))
                    if rel_items:
                        for item in rel_items:
                            node = item.get("text")
                            edges = item.get("relations")
                            for attri, _edge_values in edges.items():
                                edge_values = list(filter(lambda ev: ev.get("probability") > threshold,
                                                          _edge_values)) if threshold else _edge_values
                                if edge_values:
                                    edge_values = [ev.get('text') for ev in edge_values]
                                    relations.append((node, attri, edge_values))

                result = [{"ner": dict(ners), "triplets": list(set(relations))}]

                return result

            else:  # 保存格式不变
                result = defaultdict(list)
                for k, kv in target_res.items():
                    items = list(filter(lambda x: x.get('probability') > threshold, kv)) if threshold else kv
                    if items:
                        for item in items:
                            item_relations_dict = defaultdict(list)
                            if "relations" in item:
                                item_relations = item.get('relations')
                                for rk, rv in item_relations.items():
                                    relations = list(
                                        filter(lambda r: r.get('probability') > threshold, rv)) if threshold else rv
                                    if relations:
                                        for relation in relations:
                                            item_relations_dict[rk].append(
                                                {'text': relation['text'], 'probability': relation['probability']})
                            if item_relations_dict:
                                added_item = {"text": item['text'],
                                              "probability": item['probability'],
                                              'relations': dict(item_relations_dict)}
                                if added_item not in result[k]: result[k].append(added_item)

                            else:
                                added_item = {"text": item['text'], "probability": item['probability']}
                                if added_item not in result[k]: result[k].append(added_item)

                return [dict(result)]

        else:
            return target_res


    def extract_case_info(self, text: str) -> Dict:
        """ 项目信息抽提 """

        res = defaultdict(list)
        texts = [t for t in text.split('\n') if t]
        for line in texts:
            key = ''
            vaule = []
            for k, v in self.project_templates.items():
                if (k in line and ("｜" in line or "丨" in line or "|" in line)) or \
                        (k in line and (":" in line or "：" in line)) or \
                        (k in line and ("/" in line)) or \
                        (len(list(filter(lambda x: x in line, v))) > 0 and (
                                "｜" in line or "丨" in line or "|" in line)) or \
                        (len(list(filter(lambda x: x in line, v))) > 0 and (":" in line or "：" in line)) or \
                        (len(list(filter(lambda x: x in line, v))) > 0 and ("/" in line)):

                    key = k

                    if "：" in line:
                        vaule = line.split("：")[-1].strip()
                    elif ":" in line:
                        vaule = line.split(":")[-1].strip()
                    elif "｜" in line:
                        vaule = line.split("｜")[-1].strip()
                    elif "丨" in line:
                        vaule = line.split("丨")[-1].strip()
                    elif "|" in line:
                        vaule = line.split('|')[-1].strip()
                    elif "/" in line:
                        vaule = line.split('/')[-1].strip()

            if key and vaule:
                # res[key].append(vaule)
                vaule = vaule.strip().replace("?", "")
                if len(vaule) < 30: res[key].append(vaule)

        if not res:
            res = self._ie_case_info(text)

        return dict(res)

    def _ie_case_info(self, text: str, threshold: float = 0.35):
        """ uie提取项目信息 """

        res = defaultdict(list)
        self.base_ie_model.set_schema(schema=list(self.project_templates.keys()))
        info = self._uie_postprocess(self.base_ie_model(text), threshold=threshold, reform=False)[0]
        if info:
            for k, v in info.items():
                vs = [x.get("text") for x in v]
                res[k].extend(vs)

        return res


def je_raw_data():
    """ 建议网数据 """
    # jdat = json.load(open('./je/je_texts.json', 'r'))
    jdat = json.load(open("./je/all_js_texts.json", 'r'))
    if 'RECORDS' in jdat:
        for item in jdat.get('RECORDS'):

            if '_id' in item: del item['_id']
            if 'fav_num' in item: del item['fav_num']
            if 'signature' in item: del item['signature']
            if 'view_num' in item: del item['view_num']
            if 'photos_key_json' in item: del item['photos_key_json']
            if 'photos' in item: del item['photos']
            if 'singnature_key' in item: del item['singnature_key']
            if 'singnature_key' in item: del item['singnature_key']
            if 'map_photos_key' in item: del item['map_photos_key']
            if 'area' in item: del item['area']

        return jdat.get('RECORDS')

    else:
        return jdat


je_data = je_raw_data()
doc = je_data[6]
print(doc['id'])
text = doc['desc']

JE = je_parser()
res = JE.extract_case_info(text)
print(res)


# for i, item in enumerate(je_data):
#     text = item.get('desc')
#     id = item.get('id')
#
#     print(id)
#     res = JE.extract_case_info(text)
#     print(res)
#     print("*********************")
#
#     if i > 10:
#         break





