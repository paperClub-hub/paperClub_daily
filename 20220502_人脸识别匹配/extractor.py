##!/usr/bin/python
# -*- coding: utf-8 -*-

import common
import numpy as np
import torch
import torch.nn.functional as F
import cv2,os
from PIL import Image
from model.DBFace import DBFace
from features import VectorExtractor
from torchvision.transforms import functional as TVF
import argparse

""""
1. 人脸检测：2022-05-02
2. 人脸特征提取：2022-05-04

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
    
    del image, landmark, torch_image, scores, 
    return nms(objs, iou=nms_iou)



def face_detect(image_id, cv2_mat, score_cutoff=0.4, iou_cutoff=0.5, 
                 area_cutoff=1000, max_num_faces=10
                 ):
    """ 人脸检测：
            获取图片人脸位置
            :param image_id: 图片id
            :param cv2_mat: cv2_bgr
            score_cutoff: 人脸置信度下限
            iou_cutoff: iou置信度下限
            area_cutoff: 人脸面积下限
            max_num_faces: 人脸个数上限
            :return: list , [[img_id, [0,0,img_w,img_h], i, [10,10,300,500], ...  ]
    """
    
    data = []
    h,w = cv2_mat.shape[:2]
    objs = detect(MODEL, cv2_mat, threshold=score_cutoff, nms_iou=iou_cutoff)
    for i, obj in enumerate(objs):
        x1, y1, x2, y2 = common.intv(obj.box)
        x1 = 0 if x1 < 0 else x1
        y1 = 0 if y1 < 0 else y1
        x2 = w if x2 > w else x2
        y2 = h if y2 > h else y2
        # score = obj.score
        box = [x1, y1, x2, y2]
        area = (x2-x1)*(y2-y1)

        if area > area_cutoff and len(data) < max_num_faces:
            data.append([image_id, [w,h], i, box])
    
    del cv2_mat
    return  data
    
    
    
def show_detect(cv2_mat):
    """ 人脸检测 + 显示 """
    
    objs = detect(MODEL, cv2_mat, threshold=0.3, nms_iou=0.3)  ### 人脸坐标
    for obj in objs:
        common.drawbbox(cv2_mat, obj)

    cv2.namedWindow("FaceDectct", 0)
    cv2.imshow("FaceDectct", cv2_mat)
    cv2.waitKey(0)


def face_records(image_id, image, score_cutoff=0.4, iou_cutoff=0.5, 
                 area_cutoff=1000, max_num_faces=10):
    """
    图像人脸检测 + 特征提取, 图像为cv2_brg格式
    Args:
        image: cv2_bgr
        score_cutoff: 人脸置信度下限
        iou_cutoff: iou置信度下限
        area_cutoff: 人脸面积下限
        max_num_faces: 人脸个数上限
    Returns: list
    """

    data = []
    face_maps = face_detect(image_id,
                                image,
                                score_cutoff,
                                iou_cutoff,
                                area_cutoff,
                                max_num_faces,
                                )
    
    if face_maps:
        for face_ in face_maps:
            img_id = face_[0]
            img_size = face_[1]
            face_index = face_[2]
            face_box = face_[3]
            [x1,y1,x2,y2] = face_box
            face_crop = image[y1:y2, x1:x2]
            pil_img = Image.fromarray(cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB))
            vec = vector_extractor(pil_img)
            
            if isinstance(vec,np.ndarray):
                data.append([img_id, img_size, face_index, face_box, vec])  ### 图片编号， 原图宽高box，face_index, xyxy, vec

    else:
        print(f"image_id: {image_id} 未检测到人脸!")

    return data


def vector_extractor(pil_img):
    """
    人脸特征提取
    """
    def _process(image_tensor):
        processed_tensor = (image_tensor - 127.5) / 128.0
        return processed_tensor

    try:
        pil_img = pil_img.resize((image_size, image_size))
        img = TVF.to_tensor(np.float32(pil_img))
        img_n = _process(img).to(DEVICE)
        img_embedding = NET(img_n.unsqueeze(0)).cpu().detach().numpy()[0]

    except:
        print("特征提取失败！")
        img_embedding = []

    return img_embedding


image_size = 160
DEVICE = torch.device('cpu')
MODEL = None
if MODEL is None:
    MODEL = load_model()

NET = None
if NET is None:
    NET = VectorExtractor().eval().to(DEVICE)


if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument("--input", '-i', type=str, default="./datas/selfie.jpg")
    parser.add_argument("--type", '-t', choices=['image'], default='image')
    parser.add_argument("--out", "-o", default='./result')

    args = parser.parse_args()
    input_path = args.input
    input_type = args.type
    out_path = args.out
    # show_detect(input_path)
    src = cv2.imread(input_path)
    data = face_records(os.path.basename(input_path), src, score_cutoff=0.2, iou_cutoff=0.2)
    print("data: ",data)
    


    