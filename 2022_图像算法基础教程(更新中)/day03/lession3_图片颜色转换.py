##!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author: paperClub
"""

####颜色转换：


import cv2

# img_path = "src/imgs/2.jpg"
# img = cv2.imread(img_path)
#
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) ### 灰色
# hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#
# cv2.namedWindow("input", 0)
# cv2.imshow("input", img)
#
# cv2.namedWindow("gray", 0)
# cv2.imshow("gray", gray)
#
# cv2.namedWindow("hsv", 0)
# cv2.imshow("hsv", hsv)
#
# cv2.waitKey(0)


flags = [x for x in dir(cv2) if x.startswith("COLOR_") ]

# print(f"支持的颜色转换：{flags}")


import numpy as np
import argparse
import cv2

image = cv2.imread('src/imgs/jz.jpg')
color = [
    ([0, 70, 70], [70, 255, 255])  # 黄色范围~这个是我自己试验的范围，可根据实际情况自行调整~注意：数值按[b,g,r]排布
]
# 如果color中定义了几种颜色区间，都可以分割出来
for (lower, upper) in color:
    # 创建NumPy数组
    lower = np.array(lower, dtype="uint8")  # 颜色下限
    upper = np.array(upper, dtype="uint8")  # 颜色上限

    # 根据阈值找到对应颜色
    mask = cv2.inRange(image, lower, upper)
    output = cv2.bitwise_and(image, image, mask=mask)

    # 展示图片
    cv2.imshow("images", np.hstack([image, output]))
    cv2.waitKey(0)