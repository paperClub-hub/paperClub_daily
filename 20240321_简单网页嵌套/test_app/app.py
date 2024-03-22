from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# 设置静态文件目录，这样FastAPI就知道去哪里找HTML文件
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_home():
	# 返回首页内容
	with open("static/home.html", "r", encoding="utf-8") as file:
		html_content = file.read()
	return HTMLResponse(content=html_content)


@app.get("/detail")
async def read_detail():
	# 返回详情页内容
	with open("static/index.html", "r", encoding="utf-8") as file:
		html_content = file.read()
	return HTMLResponse(content=html_content)


if __name__ == "__main__":
	import uvicorn

	uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)