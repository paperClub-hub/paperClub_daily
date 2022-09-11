
import time
from PIL import Image
import os
import cv2
import requests as req
import pandas as pd
from threading import Thread
import glob
import asyncio
import  requests



def get_urls():
    """ 获取图片链接 """
    down_urls = []
    projects =  pd.read_csv("./project.csv", sep='\t', names=['project_id', 'tags', 'urls', 'media_ids'])
    for line in projects.itertuples():
        urls = eval(line[3])
        media_ids = eval(line[4])
        infos = [(url,id) for url,id in zip(urls, media_ids)]
        down_urls.extend(infos)

    return down_urls


async def download_image(url_data):
    
    (img_url, media_id) = url_data ## (url, img_id)
    save_file = os.path.join(ImageDir, f"{media_id}.jpg")

    if not os.path.exists(save_file):
        loop = asyncio.get_event_loop()
        # 创建线程的Future对象
        future = loop.run_in_executor(None,requests.get,img_url)
        response = await future
        print(f"{media_id}: 下载完成")
        
        with open(save_file,mode="wb") as file_object:
            file_object.write(response.content)
    else:
        pass



def DownImages(url_infos):
    """ 开启协程， 下载图片 """

    tasks = [download_image(url) for url in url_infos]
    # 创建事件循环
    loop = asyncio.get_event_loop()
    # 开启协程
    loop.run_until_complete(asyncio.wait(tasks))



def CheckImages():
    """ 检查图片 """
    errIds = []
    ImageDir, file_type = '.jpg'
    imgs = glob.glob(ImageDir + "/*" + file_type)
    for imgfile in imgs:
        try:
            src = cv2.imread(imgfile)
            gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        except Exception as ee:
            print(f"失败：{imgfile}, {ee}")
            id = os.path.splitext(os.path.basename(imgfile))[0]
            errIds.append(id)
            os.remove(imgfile)
    errIds = list(map(int, errIds))

    return errIds

ImgUrls = []
ImageDir = './images'
if not ImgUrls:
    ImgUrls = get_urls()

start = time.time()

DownImages(ImgUrls) ### 下载图片

print(f"耗时1： {time.time() - start}")

errIds = CheckImages() ### 检查图片
if len(errIds) > 0:
    URLS = list(filter(lambda x: x[1] in errIds, ImgUrls)) ### 再次
    DownImages(URLS)

print(f"总耗时： {time.time() - start}")