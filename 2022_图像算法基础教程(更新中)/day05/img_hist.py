import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import axes3d
from urllib import request
import warnings



def url2img(url_path):
    resp = request.urlopen(url_path)
    image = np.asarray(bytearray(resp.read()), dtype="uint8") ### 字节流数组
    img = cv2.imdecode(image, 1)
    
    return img


def get_pixvalue(cv2_img):  # 单张图片的信息
    h, w, c = cv2_img.shape
    img_b = cv2_img[:, :, 0].astype(np.int16)
    img_g = cv2_img[:, :, 1].astype(np.int16)
    img_r = cv2_img[:, :, 2].astype(np.int16)
    img_sum = img_b + img_g + img_r
    return h, w, img_sum, img_b, img_g, img_r


def piexlDifvalue(imgArrs):  # 两张三通道图片的每个像素的差

    img_inf = []
    for img in imgArrs:
        h, w, img_sum, img_b, img_g, img_r = get_pixvalue(img)
        img_inf.append([h, w, img_sum, img_b, img_g, img_r])

    if img_inf[0][:2] == img_inf[1][:2]:
        return img_inf[0][0], img_inf[0][1], abs(img_inf[0][2] - img_inf[1][2])

    else:
        print('size is not the same!!')
        exit(0)
        return None


def showPiexlDist(imgArrs):
    # print(arg)
    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection='3d')
    
    h, w, img_sum = piexlDifvalue(imgArrs)
    
    x = np.arange(0, w, 1)
    y = np.arange(0, h, 1)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros(Y.shape, dtype=np.uint16)  # 新建一个元素全为0单shape和X,Y都一样的z
    for i in range(Y.shape[0]):
        for j in range(Y.shape[1]):
            Z[i][j] = img_sum[i][j]

    ax1.plot_surface(X, Y, Z, rstride=1, cstride=1,
                     cmap=plt.get_cmap('rainbow'))
    # 绘制等高线，这个映射必须是等高线方向有差值,cmap/cm = color map
    # ax1.contourf(X, Y, Z, zdir='z', offset=-2, cmap=plt.get_cmap('rainbow'))
    plt.show()


def get_and(cv2_img, blur_size = 10, kernel_size = 10, valMin = 127):
    gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.blur(gray, (blur_size, blur_size))
    k=np.ones((kernel_size, kernel_size),np.uint8)
    _, th = cv2.threshold(gray, valMin, 255, cv2.THRESH_OTSU)
    open = cv2.morphologyEx( th, cv2.MORPH_OPEN, k)
    and_img = cv2.bitwise_and(cv2_img, cv2_img, mask=open)
    
    return and_img


import numpy as np

def hist2d(cv2_img):
    
    def callback(val):
        global hist_scale
        hist_scale = val
    
    hsv_map = np.zeros((180, 256, 3), np.uint8)
    h, s = np.indices(hsv_map.shape[:2])
    hsv_map[:,:,0] = h
    hsv_map[:,:,1] = s
    hsv_map[:,:,2] = 255
    hsv_map = cv2.cvtColor(hsv_map, cv2.COLOR_HSV2BGR)
    hist_scale = 10
    
    cv2.namedWindow("hist2d", 0)
    cv2.namedWindow("ori_img", 0)
    cv2.createTrackbar('scale', 'hist2d', hist_scale, 32, callback)
    
    while True:
        text = f"val:{hist_scale}"
        frame = cv2_img.copy()
        small = cv2.pyrDown(frame)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv2.putText(hsv, text, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 25), 1)
        dark = hsv[:,:,2] < 32
        hsv[dark] = 0
        h = cv2.calcHist( [hsv], [0, 1], None, [180, 256], [0, 180, 0, 256] )
        h = np.clip(h*0.005*hist_scale, 0, 1)
        vis = hsv_map*h[:,:,np.newaxis] / 255.0
        
        cv2.imshow('ori_img', ori_img)
        cv2.imshow('hist2d', vis)
        cv2.waitKey(1)
        



url_path = 'https://tse3-mm.cn.bing.net/th/id/OIP-C.2k-XK9e1-elc-Hyz2PO7tAHaNK?w=187&h=333&c=7&r=0&o=5&dpr=1.35&pid=1.7'
# url_path = 'https://tse1-mm.cn.bing.net/th/id/R-C.eca409afb379667803e5c7b863b62269?rik=xHhWbH%2fwZDD5fg&riu=http%3a%2f%2fqimg.hxnews.com%2f2017%2f1226%2f1514251867325.jpg&ehk=xZUsr9BPCeTJVlHScwTF73NV5Psqdghnj8li8smG%2fW8%3d&risl=&pid=ImgRaw&r=0'
# url_path= 'https://uploadfile.huiyi8.com/2015/1120/20151120035805807.jpg'

ori_img = url2img(url_path)
# # ori_img = cv2.imread('img/3.jpg')
# ori_img = cv2.resize(ori_img, None, fx=0.1, fy=0.1)

# bg_img = get_and(ori_img, blur_size = 3, kernel_size = 1, valMin = 127)
# showPiexlDist((bg_img, ori_img))


# cv2.namedWindow("bg_img", 0)
# cv2.imshow("bg_img", bg_img)
# cv2.waitKey(0)

hist2d(ori_img)