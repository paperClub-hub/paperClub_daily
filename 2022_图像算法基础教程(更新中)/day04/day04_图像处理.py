##!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author: paperClub
"""

import cv2
import numpy as np
from pip import main
import skimage
from skimage import util
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib
from urllib import request
import warnings
warnings.filterwarnings('ignore')


def img_convert(cv2_img):
    """
        
    """
    if len(cv2_img.shape) == 2:
        return cv2_img
    elif len(cv2_img.shape) == 3 and cv2_img.shape[2] == 3:
        b, g, r = cv2.split(cv2_img)
        return cv2.merge((r, g, b))
    elif len(cv2_img.shape) == 3 and cv2_img.shape[2] == 4:
        b, g, r, a = cv2.split(cv2_img)
        return cv2.merge((r, g, b, a))
    else:
        return cv2_img

def url2img(url_path):
    resp = request.urlopen(url_path)
    image = np.asarray(bytearray(resp.read()), dtype="uint8") ### 字节流数组
    img = cv2.imdecode(image, 1)
    
    return img


def Canny(cv2_img):
    
    def callback(a):
        minVal = cv2.getTrackbarPos("minVal", "EdgeCanny")
        maxVal = cv2.getTrackbarPos("maxVal", "EdgeCanny")
        
        return minVal, maxVal

    #### 参数设置区域
    cv2.namedWindow("EdgeCanny")
    cv2.resizeWindow("EdgeCanny", 640, 240)
    cv2.createTrackbar("minVal", "EdgeCanny", 10, 255, callback)
    cv2.createTrackbar("maxVal", "EdgeCanny", 40, 255, callback)
    

    ####视图区域
    while True:
        gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
        minVal, maxVal = callback(0)
        
        
        # 获得指定颜色范围内的掩码
        edges = cv2.Canny(gray, minVal, maxVal)
        text = f"minVal:{minVal}, maxVal:{maxVal}"

        cv2.putText(edges, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        edges = np.hstack((cv2_img, edges))
        
        # cv2.namedWindow("EdgeCanny", 0)
        cv2.imshow("EdgeCanny", edges)

        cv2.waitKey(1)



url_path = 'https://tse3-mm.cn.bing.net/th/id/OIP-C.2k-XK9e1-elc-Hyz2PO7tAHaNK?w=187&h=333&c=7&r=0&o=5&dpr=1.35&pid=1.7'
ori_img = url2img(url_path)

Canny(ori_img)