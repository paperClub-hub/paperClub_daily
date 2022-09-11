#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @ Date: 2022-07-20 11:11
# @ Author: NING MEI



import cv2
import numpy as np
import math


def inner_rect(pts):
	# pts为轮廓坐标
	# 列表中存储元素分别为左上角，右上角，右下角和左下角
	# 计算点之间的差值
	# 右上角的点具有最小的差值,
	# 左下角的点具有最大的差值
	rect = np.zeros((4, 2), dtype = "float32")
	# 左上角的点具有最小的和，而右下角的点具有最大的和
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	del pts,s
	return rect




def show_img(img):
	cv2.namedWindow("maks", cv2.WINDOW_NORMAL)
	cv2.imshow('maks', img)
	cv2.waitKey()



def mask_inner_shape(mask_bin):
	""" 最大内接圆  和 最大内接正方形 及 最大内接矩形 """

	## 获取最大内接圆，根据内接圆半径退出正方形边长即可

	area_threshold = 100*100
	h,w = mask_bin.shape
	dist = np.empty((h,w), dtype=np.float32)
	_, thresh = cv2.threshold(mask_bin, 0, 255, cv2.THRESH_BINARY)
	contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	contours = sorted(contours, key=cv2.contourArea, reverse=True)
	filter_contours = list(filter(lambda x: cv2.contourArea(x) > area_threshold, contours))

	## 最大内接圆、最大内接正方形
	for i in range(h):
		for j in range(w):
			dist[i, j] = cv2.pointPolygonTest(filter_contours[0], (j, i), True)
	minVal, maxVal, _, maxDistPt = cv2.minMaxLoc(dist)
	minVal = abs(minVal)
	maxVal = abs(maxVal)
	cx,cy = maxDistPt
	r = np.int(maxVal)
	w = math.sqrt(2 *r*r)
	x1, x2 = int(cx - w/2),  int(cx + w/2)
	y1, y2 = int(cy - w/2), int(cy + w/2)

	c = contours[0] ## 最大轮廓
	rect = inner_rect(c.reshape(c.shape[0], 2))
	xs = sorted([i[0] for i in rect])
	ys = sorted([i[1] for i in rect])
	rect_x1 = int(xs[1])
	rect_x2 = int(xs[2])
	rect_y1 = int(ys[1])
	rect_y2 = int(ys[2])


	result = cv2.cvtColor(mask_bin, cv2.COLOR_GRAY2BGR)
	cv2.rectangle(result, (x1,y1),(x2,y2), (255, 0, 0), 2)
	cv2.rectangle(result, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 0, 255), 4)
	cv2.circle(result, maxDistPt, r, (0, 255, 0), 2, 1, 0)

	show_img(result)



if __name__ == '__main__':
    
	mask = cv2.imread("mask2.png")
	gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
	img = cv2.imread("imgs/gea.jpg")
	mask_inner_shape(gray)

