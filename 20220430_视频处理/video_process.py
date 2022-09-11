##!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import glob,os
import numpy as np
import argparse

def pad(image, min_height, min_width):
    """ 边填充 """
    h,w,_ = image.shape
    """ 图片边填充 """
    if h < min_height:
        h_pad_top = int((min_height - h) / 2.0)
        h_pad_bottom = min_height - h - h_pad_top
    else:
        h_pad_top = 0
        h_pad_bottom = 0
    if w < min_width:
        w_pad_left = int((min_width - w) / 2.0)
        w_pad_right = min_width - w - w_pad_left
    else:
        w_pad_left = 0
        w_pad_right = 0

    return cv2.copyMakeBorder(image, h_pad_top,
                              h_pad_bottom,
                              w_pad_left, w_pad_right,
                              cv2.BORDER_CONSTANT,
                              value=(255, 255, 255))


def video_show(cap, save_path, is_save=False):
    """ 视频保存 """
    fps = 10.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') ### 保存格式
    out = cv2.VideoWriter(save_path, fourcc, fps, (width, height))

    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            frame1 = process(frame, opt=5)
            frame2 = process(frame, opt=0)
            frame3 = process(frame, opt=1)

            mat1 = np.hstack((frame, frame1))
            mat2 = np.hstack((frame3, frame2))
            mat = np.vstack((mat1, mat2))
            mat = cv2.resize(mat, (width, height))
            cv2.imshow('frame', mat)

            if is_save:
                out.write(mat)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    out.release()



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



if __name__ == '__main__':
    # video_path = './we_are_young.mp4'
    video_path = './hello.mp4'
    save_path = "./save.mp4"
    capture = cv2.VideoCapture(video_path)
    video_show(capture, save_path, True)


