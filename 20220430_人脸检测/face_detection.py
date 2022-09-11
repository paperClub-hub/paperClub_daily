##!/usr/bin/python
# -*- coding: utf-8 -*-

import common
import numpy as np
import torch
import torch.nn.functional as F
import cv2,os
from model.DBFace import DBFace
DEVICE = torch.device('cpu')

""""
人脸检测：2022-05-02
"""

def nms(objs, iou=0.5):

    if objs is None or len(objs) <= 1:
        return objs

    keep = []
    objs = sorted(objs, key=lambda obj: obj.score, reverse=True)
    flags = [0] * len(objs)
    for index, obj in enumerate(objs):
        if flags[index] != 0:
            continue
        keep.append(obj)
        for j in range(index + 1, len(objs)):
            if flags[j] == 0 and obj.iou(objs[j]) > iou:
                flags[j] = 1

    del objs

    return keep



def load_model():
    dbface = DBFace()
    dbface.eval()
    dbface.load("./model/dbface.pth")
    return dbface



def detect(model, image, threshold=0.3, nms_iou=0.3):

    mean = [0.408, 0.447, 0.47]
    std = [0.289, 0.274, 0.278]

    image = common.pad(image)
    image = ((image / 255.0 - mean) / std).astype(np.float32)
    image = image.transpose(2, 0, 1)

    torch_image = torch.from_numpy(image)[None]
    hm, box, landmark = model(torch_image)
    hm_pool = F.max_pool2d(hm, 3, 1, 1)
    scores, indices = ((hm == hm_pool).float() * hm).view(1, -1).cpu().topk(1000)
    hm_height, hm_width = hm.shape[2:]

    scores = scores.squeeze()
    indices = indices.squeeze()
    ys = list((indices / hm_width).int().data.numpy())
    xs = list((indices % hm_width).int().data.numpy())
    scores = list(scores.data.numpy())
    box = box.cpu().squeeze().data.numpy()
    landmark = landmark.cpu().squeeze().data.numpy()

    objs = []
    stride = 4
    for cx, cy, score in zip(xs, ys, scores):
        if score < threshold:
            break

        x, y, r, b = box[:, cy, cx]
        xyrb = (np.array([cx, cy, cx, cy]) + [-x, -y, r, b]) * stride
        x5y5 = landmark[:, cy, cx]
        x5y5 = (common.exp(x5y5 * 4) + ([cx]*5 + [cy]*5)) * stride
        box_landmark = list(zip(x5y5[:5], x5y5[5:]))
        objs.append(common.BBox(0, xyrb=xyrb, score=score, landmark=box_landmark))
    return nms(objs, iou=nms_iou)




MODEL = None
if MODEL is None:
    MODEL = load_model()


def video_detect(video_path, save_path):
    fps = 10.0
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * 1)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * 2 )
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(save_path, fourcc, fps, (width, height))
    while True:
        _, frame = cap.read()
        frame0 = frame.copy()
        if frame is None:
            break
        objs = detect(MODEL, frame, threshold=0.3, nms_iou=0.3) ### 人脸坐标
        for obj in objs:
            common.drawbbox(frame, obj)

        mat = np.vstack((frame0, frame))
        mat = cv2.resize(mat, (width, height))

        cv2.imshow("FaceDectct", mat)

        out.write(mat)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    out.release()


def image_detect(img_path):
    frame = cv2.imread(img_path)
    objs = detect(MODEL, frame, threshold=0.3, nms_iou=0.3)  ### 人脸坐标
    for obj in objs:
        common.drawbbox(frame, obj)

    cv2.namedWindow("FaceDectct", 0)
    cv2.imshow("FaceDectct", frame)
    cv2.waitKey(0)

    cv2.imwrite(os.path.join("./result", os.path.basename(img_path)), frame)



if __name__ == "__main__":
    # image_demo()
    # video_path = "./we_are_young.mp4"
    video_path = "./you_are_angle.mp4"
    save_path = "detect2.mp4"
    # video_detect(video_path, save_path)

    img_path = "./datas/selfie.jpg"
    image_detect(img_path)

    


    