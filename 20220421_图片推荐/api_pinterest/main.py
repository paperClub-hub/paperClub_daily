# -*- coding:utf-8 -*-

import os,json
import os,base64
import random

from fastapi import FastAPI
from pydantic import BaseModel

from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import Optional
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

singature_path = '/data/1_qunosen/2022/dhome/text/pinsage/checkpoint/signature_info.json'
zero_file = './no_result.jpeg'
zeros_img_stream = base64.b64encode(open(zero_file, 'rb').read()).decode()


def data_format(signatures: list):
    " 数据格式转换"

    data = []
    for signature in signatures:
        res = JDATA.get(signature)
        tags = eval(res["visual_objects"])
        data.append(
                        { "img": file2url(signature), 
                          "tags":  "|".join(list(set(tags))),
                          "sign": signature,
                        }
                    )
        
    return data


@app.get("/sample")
def img_online():
    " 前端显示图片 "
    num = 6
    signatures = random.sample(list(JDATA.keys()), num)
    data = data_format(signatures)
    del signatures
        
    return data


JDATA = []
if not JDATA:
    JDATA = json.loads(open(singature_path, 'r').read())
    

def file2url(sp_id:str):
    "sp_id: singature of pinterest"
    url = f"https://i.pinimg.com/236x/{sp_id[:2]}/{sp_id[2:4]}/{sp_id[4:6]}/{sp_id}.jpg"
    return url



class Item(BaseModel):
    data: list
    

@app.post("/query")
def read_item(params: Item):
    # print("传入params: ", params)

    item_ids = params.data[0]['item_ids']
    print("item_ids:", item_ids)

    result = []

    if len(item_ids) > 0:
        args_k = 5
        for signature in item_ids:
            sign_id = JDATA.get(signature).get('signture_id')
            if sign_id:
                sign_id = int(sign_id) ### singature index 
                recal_ids = RECAL.recall([sign_id], args_k) ## 一维数组
                # print(f"signature: {signature}, 召回：recal_ids: ", recal_ids)
                data = data_format(recal_ids[0])
                result.extend(data)
            
            else:
                print(f"{signature}: 不存在！")
                img_stream = zeros_img_stream
                img_byte64 = "data:image/jepg;base64," + img_stream
                zero = {"img": img_byte64,
                        "tags": "召回失败",
                        }
                
                data = [zero]
                result.extend(data)
                del img_byte64

    else:
        print(f"无输入！")
        img_stream = zeros_img_stream
        img_byte64 = "data:image/jepg;base64," + img_stream
        zero = {"img": img_byte64,
                "tags": "输入参数错误",
                }
        
        data = [zero]
        result.extend(data)
        del img_byte64
    
    
    

    return result

    
    


ip = "0.0.0.0"
port = 9920

if __name__ == '__main__':    
    import uvicorn
    uvicorn.run(app='main2:app', host=ip, port=port, reload=True, debug=True)

