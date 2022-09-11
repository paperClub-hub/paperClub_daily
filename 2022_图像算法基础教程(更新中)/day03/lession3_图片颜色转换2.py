##!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author: paperClub
"""

#### 调色板


import cv2



import cv2
import numpy as np


def color_bar():
    def callback(x):
        pass
    
    # 创建一副黑色图像
    img = np.zeros((300,512,3),np.uint8)
    cv2.namedWindow('image')

    switch = 'ON\nOFF'
    cv2.createTrackbar(switch, 'image', 0, 1, callback)

    cv2.createTrackbar('R','image', 0, 255, callback)
    cv2.createTrackbar('G','image', 0, 255, callback)
    cv2.createTrackbar('B','image', 0, 255, callback)

    while True:
        cv2.imshow('image',img)
        k = cv2.waitKey(1)&0xFF
        if k == 27:
            break

        r = cv2.getTrackbarPos('R','image')
        g = cv2.getTrackbarPos('G','image')
        b = cv2.getTrackbarPos('B','image')
        s = cv2.getTrackbarPos(switch,'image')

        if s == 0:
            img[:] = 0
            img[:] = [125, 0, 125]
        else:
            img[:] = [b, g, r]
        img[:] = [b, g, r]

    cv2.destroyAllWindows()




# 回调函数必须要写
# 也可以这样写：lambda x: x



def colorRange(src):

    def callback(a):
        h_min = cv2.getTrackbarPos("Hue Min", "ColorBars")
        h_max = cv2.getTrackbarPos("Hue Max", "ColorBars")
        s_min = cv2.getTrackbarPos("Sat Min", "ColorBars")
        s_max = cv2.getTrackbarPos("Sat Max", "ColorBars")
        v_min = cv2.getTrackbarPos("Val Min", "ColorBars")
        v_max = cv2.getTrackbarPos("Val Max", "ColorBars")

        return h_min, h_max, s_min, s_max, v_min, v_max

    #### 参数设置区域
    cv2.namedWindow("ColorBars")
    cv2.resizeWindow("ColorBars", 640, 240)
    cv2.createTrackbar("Hue Min", "ColorBars", 0, 180, callback)
    cv2.createTrackbar("Hue Max", "ColorBars", 40, 180, callback)
    cv2.createTrackbar("Sat Min", "ColorBars", 110, 255, callback)
    cv2.createTrackbar("Sat Max", "ColorBars", 240, 255, callback)
    cv2.createTrackbar("Val Min", "ColorBars", 153, 255, callback)
    cv2.createTrackbar("Val Max", "ColorBars", 255, 255, callback)

    ####视图区域
    while True:

        imgHSV = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        h_min, h_max, s_min, s_max, v_min, v_max = callback(0)
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        
        # 获得指定颜色范围内的掩码
        mask = cv2.inRange(imgHSV, lower, upper)
        text = f"H:{h_min}-{h_max}, S:{s_min}-{s_max}, V:{v_min}-{v_max}"

        imgResult = cv2.bitwise_and(src, src, mask=mask)
        cv2.putText(imgResult, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        imgResult = np.hstack((src, imgResult))
        # cv2.namedWindow("COLOR", 0)
        cv2.imshow("COLOR", imgResult)

        cv2.waitKey(1)









if __name__ == '__main__':



    # color_bar()
    # color_hsv()
    path = './src/imgs/jz.jpg'
    src = cv2.imread(path)
    colorRange(src)
