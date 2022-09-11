#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-05 15:47
# @Author   : NING MEI
# @Desc     :


from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from paddlenlp import Taskflow



app = FastAPI()
schema = ['空间', '风格属性', '家具物体', '颜色品牌', '特征属性']

ie = Taskflow('information_extraction',
              schema=schema,
              task_path='./best',
              device_id=-1) # cpu


def convert(result):
    """ 提取转化 """
    result = result[0]
    formatted_result = []
    for label, ents in result.items():
        for ent in ents:
            formatted_result.append(
                {
                    "label": label,
                    "start_offset": ent['start'],
                    "end_offset": ent['end']
                })

    return formatted_result


class TextToAnnotate(BaseModel):
    text: str


@app.post("/")
async def auto_annotate(doc: TextToAnnotate):

    result = ie(doc.text)
    formatted_result = convert(result)
    print(doc.text)
    print(result)

    return formatted_result



def demo_requests_postapi():
    """ fastapi post请求示例 """
    import json
    import requests

    text = '客厅我们采用了灰色的皮质沙发'
    query_data = {'text': text}
    r = requests.post("http://0.0.0.0:5739", data=json.dumps(query_data))
    dat = json.loads(r.text)
    print(dat)


if __name__=="__main__":
    uvicorn.run("auto_annotate:app", host='0.0.0.0', port=5739, reload=True)

