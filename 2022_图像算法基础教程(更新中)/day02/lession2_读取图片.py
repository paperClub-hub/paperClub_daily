##!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author: paperClub
"""

########## 1
import cv2
import numpy as np
from urllib import request

# ## 图片

img_zero = np.zeros((3,3), dtype=np.uint8)
print(img_zero)

cv2.namedWindow("img_zero", 0)
cv2.imshow("img_zero", img_zero)

cv2.waitKey(0)



## 读取本地图片
img_path = r'../src/imgs/m1.jpg'
img = cv2.imread(img_path)

cv2.namedWindow("img_show", 0)
cv2.imshow("img_show", img)

cv2.waitKey(0)

print(img.shape)


#### 显示不同 flags 差异：

filename = "../src/imgs/1.jpg"

def cv2flags(filename):

    flags = [0, 1,2,3,4]
    for flag in flags:
        m = cv2.imread(filename, flags=flag)
        cv2.namedWindow(f"flags={flag}", 0)
        cv2.imshow(f"flags={flag}", m)

    cv2.waitKey(0)

# cv2flags(filename)


##### 数组访问

## 读取本地图片
img_path = r'../src/imgs/m1.jpg'
img = cv2.imread(img_path)


img[100:200, 600:800] = [255, 0, 0 ]

cv2.namedWindow("img_show", 0)
cv2.imshow("img_show", img)

cv2.waitKey(0)


def show_url_image(url_path):
    resp = request.urlopen(url_path)
    image = np.asarray(bytearray(resp.read()), dtype="uint8") ### 字节流数组
    img = cv2.imdecode(image, 1)

    cv2.namedWindow("show_url_image", 0)
    cv2.imshow("show_url_image", img)
    cv2.waitKey(0)



# url = "https://www.baidu.com/img/superlogo_c4d7df0a003d3db9b65e9ef0fe6da1ec.png?where=super"
# url = "https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fnimg.ws.126.net%2F%3Furl%3Dhttp%253A%252F%252Fdingyue.ws.126.net%252F2021%252F0519%252F9cce43b4j00qtd2zt001tc000u000gym.jpg%26thumbnail%3D650x2147483647%26quality%3D80%26type%3Djpg&refer=http%3A%2F%2Fnimg.ws.126.net&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=auto?sec=1654813817&t=4c7e437f651f1bed927f835328c1b785"
url = "https://img1.tt98.com/bizhi/20191204/ba00c1f662e1203e4e683748464e902a.jpg"
# show_url_image(url)




##### 读取视频：



def process(image, opt=0):
    dst = None
    if opt == 0:
        dst = cv2.Canny(image, 120, 120)
        dst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    if opt == 1:
        dst = cv2.flip(image, 0)
    if opt == 3:
        dst = cv2.flip(image, 1)
    if opt == 4:
        dst = cv2.flip(image, -1)
    if opt == 5:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, dst = cv2.threshold(~gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        dst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)

    return dst


def show_video(video_path):

    cap = cv2.VideoCapture(video_path)

    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            frame1 = process(frame, opt=0) ###增加视频处理功能
            met = np.hstack((frame, frame1))

            cv2.namedWindow("show_video", 0)
            cv2.imshow("show_video", met)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        else:
            break



video_path = "../src/imgs/you_are_angle.mp4"
show_video(video_path)
