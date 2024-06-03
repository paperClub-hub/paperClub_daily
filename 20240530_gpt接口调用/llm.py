#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2024-05-30 16:14
# @Author   : NING MEI
# @Desc     :

from typing import Union, List, Dict
from extractor import get_extract
from pydantic import BaseModel
from fastapi import FastAPI


class Item(BaseModel):
	doc: Union[str, List]
	threshold: float = 0.5
	dic: Dict = {}

app = FastAPI()
@app.post("/doc_uie")
async def info_extract(parms: Item):
	""" 文本信息抽提 """
	doc = parms.doc
	threshold = parms.threshold
	if isinstance(doc, list):
		doc = doc[0]

	res = {}
	try:
		res = get_extract(context=doc)
		print("doc: ", len(doc), "result: ", res)

	except Exception as error:
		print(f"error: {error}")

	return res


if __name__ == '__main__':
	ip = "0.0.0.0"
	port = 9912
	import uvicorn
	uvicorn.run(app='llm:app', host=ip, port=port, reload=False)