import sys
sys.path.append("../utils")
from imgload import *
import cv2
from PIL import Image
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw,ImageFont

import numpy as np
import os




def hsv(cv2_img, S, L, V, MAX):
    """ HSV 调整 """
    cv2_img = cv2_img.astype(np.float32)
    cv2_img = cv2_img / 255.0
    HSV = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)
    HSV2 = np.copy(HSV)
    HSV2[:, :, 1] = (1.0 + V / float(MAX)) * HSV2[:, :, 1] ## 明度
    HSV2[:, :, 1][HSV2[:, :, 1] > 1] = 1
    HSV2[:, :, 2] = (1.0 + S / float(MAX)) * HSV2[:, :, 2]  ### 饱和度
    HSV2[:, :, 2][HSV2[:, :, 2] > 1] = 1
    
    adjImg = cv2.cvtColor(HSV2, cv2.COLOR_HSV2BGR)
    adjImg = adjImg * 255.0
    adjImg = adjImg.astype(np.uint8)
    
    del cv2_img, HSV, HSV2
    return adjImg
    

def hsl(cv2_img, S, L, V, MAX):
    """ HSL 饱和度调整 """
    cv2_img = cv2_img.astype(np.float32)
    cv2_img = cv2_img / 255.0
    HLS = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HLS)
    HLS2 = np.copy(HLS)
    HLS2[:, :, 1] = (1.0 + L / float(MAX)) * HLS2[:, :, 1] ## 明度
    HLS2[:, :, 1][HLS2[:, :, 1] > 1] = 1
    HLS2[:, :, 2] = (1.0 + S / float(MAX)) * HLS2[:, :, 2]  ### 饱和度
    HLS2[:, :, 2][HLS2[:, :, 2] > 1] = 1
    
    adjImg = cv2.cvtColor(HLS2, cv2.COLOR_HLS2BGR)
    adjImg = adjImg * 255.0
    adjImg = adjImg.astype(np.uint8)
    
    del cv2_img, HLS, HLS2
    return adjImg

def rgb(cv2_img, increment):
    rgb_img = cv2_img.copy()
    rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    img = rgb_img * 1.0
    min = img.min(axis=2)
    max = img.max(axis=2)
    adjImg = rgb_img.copy()
    
    #获取HSL空间的饱和度和亮度
    delta = (max - min) / 255.0
    value = (max + min) / 255.0
    L = value/2.0
    
    # 判断：s = L<0.5 ? s1 : s2
    mask_1 = L < 0.5
    s1 = delta/(value)
    s2 = delta/(2 - value)
    s = s1 * mask_1 + s2 * (1 - mask_1)
    
    # 增量大于0，饱和度指数增强
    if increment > 0 :
        # alpha = increment+s > 1 ? alpha_1 : alpha_2
        temp = increment + s
        mask_2 = temp >  1
        alpha_1 = s
        alpha_2 = s * 0 + 1 - increment
        alpha = alpha_1 * mask_2 + alpha_2 * (1 - mask_2)
        
        alpha = 1/alpha -1 
        adjImg[:, :, 0] = img[:, :, 0] + (img[:, :, 0] - L * 255.0) * alpha
        adjImg[:, :, 1] = img[:, :, 1] + (img[:, :, 1] - L * 255.0) * alpha
        adjImg[:, :, 2] = img[:, :, 2] + (img[:, :, 2] - L * 255.0) * alpha
        
    # 增量小于0，饱和度线性衰减
    else:
        alpha = increment
        adjImg[:, :, 0] = img[:, :, 0] + (img[:, :, 0] - L * 255.0) * alpha
        adjImg[:, :, 1] = img[:, :, 1] + (img[:, :, 1] - L * 255.0) * alpha
        adjImg[:, :, 2] = img[:, :, 2] + (img[:, :, 2] - L * 255.0) * alpha
    
    adjImg = adjImg/255.0
    
    # RGB颜色上下限处理(小于0取0，大于1取1)
    mask_3 = adjImg  < 0 
    mask_4 = adjImg  > 1
    adjImg = adjImg * (1-mask_3)
    adjImg = adjImg * (1-mask_4) + mask_4
    adjImg = (adjImg * 255.0).astype(np.uint8)
    adjImg = cv2.cvtColor(adjImg, cv2.COLOR_RGB2BGR)
    
    del cv2_img, rgb_img
    return adjImg

def saturationAdjust(cv2_img):
    
    #### 图像颜色饱和度 调整
    
    def callback(a):
        S = cv2.getTrackbarPos("S", "SatuAdj")
        V = cv2.getTrackbarPos("V", "SatuAdj")
        L = cv2.getTrackbarPos("L", "SatuAdj")
        I = (1 + cv2.getTrackbarPos("I", "SatuAdj"))/100.0
        MAX = cv2.getTrackbarPos("Max", "SatuAdj") + 1
        return S, V, L, I, MAX
    
    
    cv2.namedWindow("SatuAdj", 0)
    cv2.createTrackbar('S', 'SatuAdj', 10, 100, callback)
    cv2.createTrackbar('V', 'SatuAdj', 10, 100, callback)
    cv2.createTrackbar('L', 'SatuAdj', 10, 100, callback)
    cv2.createTrackbar('I', 'SatuAdj', -100, 100, callback)
    cv2.createTrackbar('Max', 'SatuAdj', 60, 360, callback)
    
    ####视图区域
    input_img = cv2_img.copy()
    while True:
        S, V, L, I, MAX = callback(0)
        hsv_img = hsv(input_img.copy(), S, L, V, MAX)
        hsl_img = hsl(input_img.copy(), S, L, V, MAX)
        rgb_img = rgb(input_img.copy(), I)
        mat_img = np.hstack((input_img, hsv_img, hsl_img, rgb_img))
        text = f"Max:{MAX},S:{S}, V:{V}, L:{L}"
        cv2.putText(mat_img, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        cv2.imshow("SatuAdj", mat_img)
        cv2.waitKey(1)
        


def img2str(cv2_img, text = '加油', n = 10, to_cv2=True):
    cv2_img = cv2_img[:, :, (2, 1, 0)]
    h, w, _ = cv2_img.shape
    pil_img_draw = Image.new("RGB", [h, w], color="white")
    draeobj = ImageDraw.Draw(pil_img_draw)
    
    font = ImageFont.truetype('./font/simhei.ttf',size=n-1)
    for i in range(0, h, n):
        for j in range(0,w, n):
            draeobj.ink = cv2_img[i][j][0] + cv2_img[i][j][1]*256 + cv2_img[i][j][2]*256*256
            num = int(j/n)%len(text)
            ttext = text[num]
            draeobj.text([j,i], ttext, font=font)

    if to_cv2:
        return cv2.cvtColor(np.asarray(pil_img_draw),cv2.COLOR_RGB2BGR)
    
    return pil_img_draw


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
            text = "你好！"
            img_str = img2str(frame, text=text, to_cv2=True)
            mat = img_str
            # cv2.imshow('frame', mat)
            if is_save:
                out.write(mat)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    out.release()


def video_save(cap, save_path, is_show=False):
    """ 视频保存 """
    fps = 10.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') ### 保存格式
    out = cv2.VideoWriter(save_path, fourcc, fps, (width, height))

    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            # frame = cv2.flip(frame,0)
            frame = img2str(frame, True)
            out.write(frame)
            if is_show:
                cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    # cap.release()
    out.release()



url_path = 'https://tse3-mm.cn.bing.net/th/id/OIP-C.2k-XK9e1-elc-Hyz2PO7tAHaNK?w=187&h=333&c=7&r=0&o=5&dpr=1.35&pid=1.7'
url_path = 'https://img0.baidu.com/it/u=3374258436,4257368831&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=354'

ori_img = url2img(url_path)

# url_path= 'https://uploadfile.huiyi8.com/2015/1120/20151120035805807.jpg'
# ori_img = url2img(url_path)
# saturationAdjust(ori_img)
    
# pil = img2str(ori_img, to_cv2=False)
# plt.imshow(pil)
# plt.show()

video_path = './2.mp4'
save_path = "./1-1.mp4"
capture = cv2.VideoCapture(video_path)
video_show(capture, save_path, True)