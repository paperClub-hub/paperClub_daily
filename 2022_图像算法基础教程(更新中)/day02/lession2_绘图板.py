##!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author: paperClub
"""


import cv2
import numpy as np


def demo():
    def callback(x):
        pass

    # 创建图像
    img = np.zeros((300, 512, 3), np.uint8)
    cv2.namedWindow('Board')  ## 创建窗口Board
    switch = 'ON:\nOFF'  ## 开关定义，默认开启（0）

    ## 创建轨迹：
    cv2.createTrackbar(switch, 'Board', 0, 1, callback)
    cv2.createTrackbar('R', 'Board', 180, 255, callback)
    cv2.createTrackbar('G', 'Board', 0, 255, callback)
    cv2.createTrackbar('B', 'Board', 0, 255, callback)

    while True:
        cv2.imshow('Board', img)
        k = cv2.waitKey(1) & 0xFF ### 监听键盘
        if k == 27:
            break
        ### 获取数值
        r = cv2.getTrackbarPos('R', 'Board')
        g = cv2.getTrackbarPos('G', 'Board')
        b = cv2.getTrackbarPos('B', 'Board')
        s = cv2.getTrackbarPos(switch, 'Board')

        ### 判断开关是否关闭
        if s == 0:
            img[:] = [b, g, r]

        else:
            print("绘图功能已关闭")
            img[:] = [255, 255, 255]  ## 转为白色

    cv2.destroyAllWindows()






# demo()


def nothing(x):
    pass


drawing=False # 当鼠标按下时变为 True
mode=True # 如果 mode 为 true 绘制矩形。按下'm' 变成绘制曲线。
X,Y = -1, -1

# 创建回调函数
def draw_circle(event,x,y,flags, param):
    r = cv2.getTrackbarPos('Color-R','Board')
    g = cv2.getTrackbarPos('Color-G','Board')
    b = cv2.getTrackbarPos('Color-B','Board')
    thin = cv2.getTrackbarPos('Size','Board')
    c = cv2.getTrackbarPos('Eraser', 'Board')

    if c == 1:
        color = (255, 255, 255)
    else:
        color = (b,g,r)

    global X,Y,drawing,mode
    if event==cv2.EVENT_LBUTTONDOWN: # 当按下左键是返回起始位置坐标
        drawing=True
        X,Y = x,y
        # 当鼠标左键按下并移动是绘制图形。event 可以查看移动，flag 查看是否按下
    elif event==cv2.EVENT_MOUSEMOVE and flags==cv2.EVENT_FLAG_LBUTTON:
        if drawing==True:
            if mode==True:
                cv2.rectangle(img,(X,Y),(x,y),color,-1)
            else:
                # 绘制圆圈，小圆点连在一起就成了线，thin 代表了笔画的粗细
                cv2.circle(img,(x,y),thin, color,-1)
        # 当鼠标松开停止绘画。
        elif event==cv2.EVENT_LBUTTONUP:
            drawing=False



img=np.zeros((512,512,3),np.uint8)
img[:] = [255,255,255] ### 初始背景颜色

cv2.namedWindow('Board', cv2.WINDOW_NORMAL)
cv2.createTrackbar('Color-R','Board',0,255,nothing)
cv2.createTrackbar('Color-G','Board',0,255,nothing)
cv2.createTrackbar('Color-B','Board',0,255,nothing)
cv2.createTrackbar('Size','Board',0,40,nothing)
cv2.createTrackbar('Eraser','Board',0,1,nothing)
cv2.setMouseCallback('Board',draw_circle)

while True:
    cv2.imshow('Board',img)
    k=cv2.waitKey(1)&0xFF
    if k==ord('m'):
        mode=not mode
    elif k==27:
        break

