import cv2
import numpy as np
from urllib import request
import warnings


def Canny(cv2_img):
    def callback(a):
        minVal = cv2.getTrackbarPos("minVal", "EdgeCanny")
        maxVal = cv2.getTrackbarPos("maxVal", "EdgeCanny")

        return minVal, maxVal

    #### 参数设置区域
    cv2.namedWindow("EdgeCanny", 0)
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


def url2img(url_path):
    resp = request.urlopen(url_path)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")  ### 字节流数组
    img = cv2.imdecode(image, 1)

    return img

# url_path = 'https://img2.baidu.com/it/u=3906645419,1579173&fm=253&fmt=auto&app=120&f=JPEG?w=889&h=500'
# ori_img = url2img(url_path)
ori_img = cv2.imread(('img/news1.png'))
Canny(ori_img)