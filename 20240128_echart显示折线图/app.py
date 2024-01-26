#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2024-01-25 18:13
# @Author   : NING MEI
# @Desc     :


import time
import uvicorn
from typing import List, Union
from pydantic import BaseModel
from fastapi import FastAPI, Request
from starlette.responses import Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from collections import OrderedDict, Counter, defaultdict


app = FastAPI()

origins = ["*"]
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
@app.get('/api/comment')
async def GetComment():
	data = [['a', 12], ['b', 15], ['c', 9]]
	return JSONResponse(data)
	# return data


@app.get("/")
async def home(request: Request):
    # 假设这是从数据库或其他地方获取的数据
    data_x = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    data_y = [
		    [220, 182, 191, 234, 290, 330, 310],
		    [150, 232, 201, 154, 190, 330, 410],
		    [320, 332, 301, 334, 390, 330, 320]
	    ]
    data_label = ['Union Ads', 'Video Ads', 'Direct']
    data = {
	    "data_x": data_x,
	    "data_y": data_y,
	    "data_label": data_label,
	    "data_series": [{"name": l, "type": 'line', "data": y} for y, l  in zip(data_y, data_label)]
	}

    return templates.TemplateResponse("index.html", {"request": request, "data": data})

if __name__ == '__main__':
	host = "127.0.0.1"
	uvicorn.run("app:app", reload=True, host=host, port=8080)


