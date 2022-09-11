#!usr/bin/python


import cv2
import numpy as np
from PIL import Image
from mpl_toolkits.mplot3d import axes3d
from urllib import request
import warnings


def cv2pil(cv2_img):
    """ cv2 img to pil img"""
    img = cv2_img
    if len(cv2_img.shape) == 2:
        img = Image.fromarray(cv2_img)
    
    elif len(cv2_img.shape) == 3:
        img = Image.fromarray(cv2_img[:,:,::-1])
    else:
        print("格式有问题")
    del cv2_img
    return img


def pil2cv(pil_img):
    return cv2.cvtColor(np.asarray(pil_img),cv2.COLOR_RGB2BGR)


def url2img(url_path):
    resp = request.urlopen(url_path)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    img = cv2.imdecode(image, 1)
    del image, resp, url_path
    
    return img

