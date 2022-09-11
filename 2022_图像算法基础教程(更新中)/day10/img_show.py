import sys

from pytools import one
sys.path.append("../utils")
from imgload import *
import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import math


def cv2_imread1(img_path, loadType=1):
    
    src = cv2.imread(img_path, loadType)
    
    return src


def cv2_imread2(img_path, loadType=1):
    """ 读取中文路径图像 """
    src = cv2.imdecode(np.fromfile(img_path, np.uint8),loadType)
    
    return src


def test():
    """ 显示图像 """
    src1 = cv2_imread1("./imgs/butterfly.jpg")
    src2 = cv2_imread2("./imgs/快乐的小鱼儿.jpg")

    img_zoom(src1)
    # cv2.namedWindow("show_img", 0)
    # cv2.imshow("show_img", src2)
    # cv2.waitKey(0)


def img_zoom(cv2_img=None):
    
    if cv2_img.any():
        img = cv2_img
        if img is None:
            sys.exit(1)

    else:
        sz = 4096
        print('generating %dx%d procedural image ...' % (sz, sz))
        img = np.zeros((sz, sz), np.uint8)
        track = np.cumsum(np.random.rand(500000, 2)-0.5, axis=0)
        track = np.int32(track*10 + (sz/2, sz/2))
        cv2.polylines(img, [track], 0, 255, 1, cv2.LINE_AA)


    down = img
    for _i in range(2):
        # down = cv2.pyrDown(down)
        down = cv2.pyrUp(down)

    def onmouse(event, x, y, flags, param):
        h, _w = img.shape[:2]
        h1, _w1 = down.shape[:2]
        x, y = 1.0*x*h/h1, 1.0*y*h/h1
        zoom = cv2.getRectSubPix(img, (600, 400), (x+0.5, y+0.5))
        cv2.imshow('zoom', zoom)

    cv2.namedWindow('ori_img', 0)
    cv2.imshow('ori_img', down)
    cv2.setMouseCallback('ori_img', onmouse)
    cv2.waitKey()
    print('Done')

# test()

url_path = "https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fpic.616pic.com%2Fys_bnew_img%2F00%2F11%2F20%2FI63Iw13JbX.jpg&refer=http%3A%2F%2Fpic.616pic.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=auto?sec=1656992820&t=243f94cb54847b4d8894bea5a0e56389"

ori_img = url2img(url_path)

img_zoom(ori_img)

    
    