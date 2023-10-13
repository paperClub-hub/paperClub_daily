#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-09-04 14:33
# @Author   : NING MEI
# @Desc     :



""" 应用主程序 """


import time
import uvicorn
import numpy as np
from fastapi import FastAPI, Request
from os.path import abspath, dirname
from starlette.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware

from config import *
# # 导入数据
# if USE_ZHUKE:
# 	from zk_recall import items2candidates, RECALL
# 	from zk_rank import RECALL2RANK
# else:
# 	from zm_recall import items2candidates, items2rank_detail, RECALL
# 	from zm_rank import RECALL2RANK, RECALL2RANK2

from zm_rank import RECALL2RANK, RECALL2RANK2
from zm_recall import items2candidates, items2rank_detail, RECALL, RECALL2

PWD = abspath(dirname(__file__))

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
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"
DETAIL_API_PREFIX = f"http://{SERVER_HOST}:{SERVER_PORT}/detail" # 图片详情接口



# home 搜索-召回 结果展示页
@app.get("/")
async def text_to_image(request: Request,
						text: str='海景房'):

	global CLICK_SEQS, QUERY, TIMESTAMPS, NUM_RECALL, SEARCH_TIMES, CLICK_INDEX, SEARCH_CLICK_DIST, LOG_DICT

	QUERY = text
	SEARCH_TIMES +=1
	print("USE_ZHUKE: ", )


	if len(CLICK_SEQS):
		# 控制历史行为生命周期
		if (SEARCH_TIMES - CLICK_INDEX) > SEARCH_CLICK_DIST:
			CLICK_SEQS = []

	print(f"搜索次数: 点击位置，历史点击: ", SEARCH_TIMES, CLICK_INDEX, CLICK_SEQS)


	# 召回测试
	text_recall_dict, vision_recall_dict = RECALL2(text, topk=NUM_RECALL)

	text_recall_mids = list(map(lambda x: x[0], sorted(text_recall_dict.items(), key=lambda x: x[1], reverse=True)))
	text_recall_scores = list(map(text_recall_dict.get, text_recall_mids))
	vision_recall_mids = list(map(lambda x: x[0], sorted(vision_recall_dict.items(), key=lambda x: x[1], reverse=True)))
	vision_recall_scores = list(map(vision_recall_dict.get, vision_recall_mids))
	candidates = items2candidates(text_recall_mids, text_recall_scores)
	candidates_rank = items2candidates(vision_recall_mids, vision_recall_scores)



	# # 搜索召回
	# recall_dict, weighted_mids = RECALL(text, topk=NUM_RECALL)
	# recall_mids = list(map(lambda x: x[0], sorted(recall_dict.items(), key=lambda x: x[1], reverse=True)))
	# recall_scores = list(map(recall_dict.get, recall_mids))

	# # 召回排序
	# rank_mids, meta_scores, rank_idxes = RECALL2RANK(text, recall_mids, recall_scores, weighted_mids,
	#                                                  CLICK_SEQS, TIMESTAMPS)

	# rank_mids2, meta_scores2, rank_idxes2 = RECALL2RANK2(text, recall_mids, recall_scores, weighted_mids,
	#                                                      CLICK_SEQS, TIMESTAMPS)





	# # 结果展示
	# candidates = items2candidates(recall_mids, recall_scores)
	# candidates_rank = items2candidates(rank_mids, meta_scores, CLICK_SEQS)
	# candidates_detail = items2rank_detail(LOG_DICT, rank_mids2, meta_scores2, CLICK_SEQS)


	print("历史点击: ", CLICK_SEQS)



	return templates.TemplateResponse("home.html", {
		"request": request,
		"detail_api_prefix": DETAIL_API_PREFIX,
		"candidate": candidates,
		"candidate_rank": candidates_rank
		# "candidates_detail": candidates_detail
	})




# 详情页
@app.get("/detail")
async def image_detail(request: Request, mid, url):
	" 点击图片查探详情 "

	global CLICK_SEQS, TIMESTAMPS, MAX_SEQS_LEN, SEARCH_TIMES, CLICK_INDEX

	print("detail  mid: ", mid)
	print("QUERY: ", QUERY)


	if isinstance(mid, str):
		mid = int(mid)

	CLICK_SEQS.insert(0, mid)
	TIMESTAMPS.insert(0, time.time())
	CLICK_INDEX = SEARCH_TIMES # 点击位置

	if len(CLICK_SEQS) > MAX_SEQS_LEN:
		CLICK_SEQS = CLICK_SEQS[: MAX_SEQS_LEN]

	if len(TIMESTAMPS) > MAX_SEQS_LEN:
		TIMESTAMPS = TIMESTAMPS[: MAX_SEQS_LEN]

	# print("url: ", url)
	return templates.TemplateResponse("click.html",
	                                  {"request": request,
	                                   "click_imgid": mid,
	                                   "click_url": url
	                                   })




if __name__ == '__main__':
	from datetime import datetime

	print(datetime.now())

	uvicorn.run('app:app', reload=True, host=SERVER_HOST, port=SERVER_PORT)