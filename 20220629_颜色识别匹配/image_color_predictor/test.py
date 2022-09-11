from logging import debug
import cv2
from color_predictor_3 import predict_color

filename = "/home/user/zs/ImagePredictor/222.jpg"

image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
image = cv2.cvtColor (image, cv2.COLOR_BGR2RGB)

import time

start = time.time()
result = predict_color(image, min_rate=0.15, debug=True)
print(time.time() - start)
print(result)