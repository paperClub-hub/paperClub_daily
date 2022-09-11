import imp
import cv2
import os
from PIL import Image
import matplotlib.pyplot as plt
import argparse

from sympy import arg


def pad(image, min_height, min_width):
    
    h, w, _ = image.shape
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
                              value=(255, 255, 255),
                              )



def resize(src, limit_w, limit_h, resize_type=4):
    
    h, w, _ = src.shape
    resized_img =  src
    if resize_type == 0:  ##### 固定高, 宽自适应
        limit_length = limit_h
        H = limit_length
        W = int(w * (limit_length / h))
        resized_img = cv2.resize(src, (W, H), cv2.INTER_AREA)

    elif resize_type == 1:  ##### 固定宽,高自适应
        limit_length = limit_w
        W = limit_length
        H = int(h * (limit_length / w))
        resized_img = cv2.resize(src, (W, H), cv2.INTER_AREA)

    elif resize_type == 2:  ######## 固定最大边长
        limit_length = limit_w
        r = limit_length / max(h, w)
        W = int(r * w)
        H = int(r * h)
        resized_img = cv2.resize(src, (W, H), cv2.INTER_AREA)

    elif resize_type == 3:  ######## 固定最小边长
        limit_length = limit_w
        r = limit_length / min(h, w)
        W = int(r * w)
        H = int(r * h)
        resized_img = cv2.resize(src, (W, H), cv2.INTER_AREA)

    elif resize_type == 4:####### 强制拉伸
        resized_img = cv2.resize(src, (limit_w, limit_h), cv2.INTER_AREA)

    elif resize_type == 5:  ####### 等比例拉伸
        r = max(limit_h, limit_w) / max(h, w)
        W = int(r * w)
        H = int(r * h)
        resized_img =  pad(cv2.resize(src, (W, H), cv2.INTER_AREA), limit_h, limit_w)


    else:
        print(f"输入错误：{resize_type}")


    return resized_img



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", '-i', type=str)
    parser.add_argument("--type", '-t', type=int, choices=[0,1,2,3,4,5], default=5)
    parser.add_argument("--hight", '-mh', type=int, default=480)
    parser.add_argument("--wight", '-mw', type=int)
    parser.add_argument("--out", "-o", type=str)
    
    args = parser.parse_args()
    input_path = args.image
    resize_type = args.type
    hight = args.hight
    wight = args.wight
    save_path = args.out
    if not save_path:
        save_path = os.path.join("./result",  os.path.basename(input_path))
    if not wight:
        wight = hight
    
    src = cv2.imread(input_path)
    resized_img = resize(src, wight, hight, resize_type)
    cv2.imwrite(save_path, resized_img)
    
    print(f"结果：{save_path}")
