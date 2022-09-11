#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-05 15:47
# @Author   : paperClub
# @Desc     :


from fastapi import FastAPI
import uvicorn
from label import *
from pydantic import BaseModel
from paddlenlp import Taskflow

"""
用于 doccano 自动打标，参考：
    https://github.com/doccano/doccano/issues/1417

"""

app = FastAPI()
SCHEMA = ['空间', '风格属性', '家具物体', '颜色品牌', '特征属性']

ie = Taskflow('information_extraction',
              schema=SCHEMA,
              task_path='./MODELS/IE',
              device_id=0) # -1 for cpu


def demo_requests_postapi():
    """ fastapi post请求示例 """
    import json
    import requests

    text = '客厅我们采用了灰色的皮质沙发'
    query_data = {'text': text}
    r = requests.post("http://127.0.0.1:5739", data=json.dumps(query_data))
    dat = json.loads(r.text)
    print(dat)




def get_tags(text: str='客厅装修', debug = False, is_original = False):
    """ 提取各类标签， 用于自动化打标 """

    def format(result):
        """ 统一为doccano格式数据格式 """
        formatted_result  = []
        for label, ents in result.items():
            for ent in ents:
                formatted_result.append(
                    {
                        "label": label,
                        "start_offset": ent['start'],
                        "end_offset": ent['end']
                    })
        del result
        return formatted_result


    def convert(orgin_res: list, is_ie = True):
        """ 转化 """

        l2s_dict = {  # 转为ie标签结果
            "STYLE": "风格", "SPACE": "空间", "LOSPACE": "空间", "OBJECT": "物体",
            "SHAPE": "形状", "COLOR": "色彩", "MATERIAL": "组分", "PATTERN": "纹理",
            "FEATURE": "特征", "BRAND": "品牌", "PROPTY": "布局", }

        result = orgin_res[0]
        if is_ie:
            formatted = format(result)
        else:
            res = {}
            for k, vs in result.items():
                if k in l2s_dict:
                    res[l2s_dict.get(k)] = vs
            formatted = format(res)

        return formatted

    org_res_ie = ie(text)
    org_res_pred = predict(text)

    if is_original:
        res_ie = org_res_ie
        res_pred = org_res_pred
    else:
        res_ie = convert(org_res_ie, is_ie=True)
        res_pred = convert(org_res_pred, is_ie=False)

    if debug:
        print(f"org_res_ie:   {org_res_ie}   \n --> res_ie:    {res_ie}  ")
        print(f"org_res_pred: {org_res_pred} \n --> res_pred: {res_pred} ")

    for res in res_pred:
        if res not in res_ie:
            res_ie.append(res)

    if is_original == False:
        res_ie = sorted(res_ie, key=lambda x: x.get('label'))

    return res_ie




class TextToAnnotate(BaseModel):
    text: str


@app.post("/")
async def auto_annotate(doc: TextToAnnotate):
    """ 自动标注 """

    result = get_tags(doc.text, debug=True)
    print(f"query: {doc.text}")

    return result


def test():
    text = '客厅装修'
    text = '厨房的格局维持了原状，为保持与其他区域的统一，重新定制了一副与墙裙同色的烤漆门套。#厨房 #定制'
    res = get_tags(text, debug=True)
    print(res)


if __name__=="__main__":
    test()
    uvicorn.run("auto_annotate:app", host='0.0.0.0', port=5739, reload=True)

