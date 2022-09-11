# -*- coding:utf-8 -*-

import os,json
import os,base64
import random

from numpy import zeros_like
from fastapi import FastAPI
from pydantic import BaseModel

from starlette.middleware.cors import CORSMiddleware

import recall as RECAL


app = FastAPI()
origins = ["*",]
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


### 配置文件
img_dir = "/data/1_qunosen/2022/paddlerec/TwoToweRS-master/data/dHome/demo/imgs"
img_json = "/data/1_qunosen/2022/paddlerec/TwoToweRS-master/data/dHome/demo/imgs.json" 
zero_file = '/data/1_qunosen/2022/pinsage/dhome2/recall_demo/no_result.jpeg'
zeros_img_stream = base64.b64encode(open(zero_file, 'rb').read()).decode()

@app.get("/")
def hello():
    return {"Hello recal_test1 !"}

JDATA = []
if not JDATA:
    JDATA = json.loads(open(img_json, 'r').read())
    JDATA = list(filter(lambda x: x['tags']!=['nan'] , JDATA )) ### 过滤tags为nan


@app.get("/sample")
def img_online():
    num = 12
    data = random.sample(JDATA, num)
    for x in data:
        x['tags'] = "|".join(x['tags'])
        imgfile = os.path.join(img_dir,f"{x['meadia_id']}.jpg")
        with open(imgfile, 'rb') as f:
            x['img'] =  "data:image/jepg;base64," + base64.b64encode(f.read()).decode() ###转化为数据流， 适应html 显示图片
    
    return data



class Item(BaseModel):
    data: list


@app.post("/query")
def recalRes(params: Item):
    """ 召回结果"""
    query_dict = params.data[0]
    media_ids = query_dict.get('media_ids', [])
    
    if media_ids:
        media_ids = list(map(int, media_ids))
        recal_ids = RECAL.recall(media_ids) ### [[8695956, 8001012], [8688428, 8695967, 9068725]]

        recall_res =  []
        if recal_ids:
            for i,ids in enumerate(recal_ids):
                ids =  list(map(str, ids))
                exist_ids = list(filter( lambda x: x['meadia_id'] in ids, JDATA ))
                if exist_ids:
                    for item in exist_ids:
                        query_id = media_ids[i]
                        media_id = item['meadia_id']
                        img_path = os.path.join(img_dir, f"{media_id}.jpg")
                        img_stream  = base64.b64encode(open(img_path, 'rb').read()).decode()
                        img_byte64 = "data:image/jepg;base64," + img_stream
                        item['img'] = img_byte64
                        item['tags'] = str(query_id) + "召回：" + " ".join(item['tags'])
                        recall_res.append(item)

        else:
            item = {}
            img_stream = zeros_img_stream
            img_byte64 = "data:image/jepg;base64," + img_stream
            item['img'] = img_byte64
            item['tags'] = str(media_ids) + '：召回为空, 图片特征不存在、请换一张试试！'
            item["space"] =  "",
            item["style"] = "",
            recall_res.append(item)
    else:
        item = {}
        print("无查询media_id !")
        img_stream  =  zeros_img_stream
        img_byte64 = "data:image/jepg;base64," + img_stream
        item['img'] = img_byte64
        item['tags'] = str(media_ids) + '：失败，图片id不存在！'
        item["space"] =  "",
        item["style"] = "",
        recall_res.append(item)

    
    return recall_res


ip = "0.0.0.0"
port = 9909

if __name__ == '__main__':

    # imgs = {'media_ids': ['9068816', '7892594']}
    # res = recalRes(imgs)
    # print("res: ", res)
    
    import uvicorn
    uvicorn.run(app='main:app', host=ip, port=port, reload=True, debug=True)

