##!/usr/bin/python
# -*- coding: utf-8 -*-


import os,re
import cv2
import glob,h5py
import numpy as np
from tqdm import tqdm
import pandas as pd
from annoy import AnnoyIndex

from extractor import face_records as Records

"""  生成数据库文件 """


def build_feature_db(imgList, dbfile):
    ####### 提取图片特征，创建数据库
    results = []
    for i, imgPath in tqdm(enumerate(imgList)):
        src = cv2.imread(imgPath)
        data = Records(os.path.basename(imgPath), src)
        if data:
            results.extend(data)

    img_names = [x[0] for x in results]
    img_names = [x.encode() for x in img_names]
    bboxes = [x[3] for x in results]
    img_vec = [x[4] for x in results]


    h5f = h5py.File(dbfile, 'w')
    h5f.create_dataset('dataset_1', data=img_names)
    h5f.create_dataset('dataset_2', data=bboxes)
    h5f.create_dataset('dataset_3', data=img_vec)
    h5f.close()


def load_feature_db(dbFile):
    h5f = h5py.File(dbFile, 'r')
    label_id = h5f['dataset_1'][:]
    label_id = [x.decode() for x in label_id]
    bbox = h5f['dataset_2'][:]
    img_vector = h5f['dataset_3'][:]
    h5f.close()

    bbox = [x.tolist() for x in bbox]
    img_vector = [x for x in img_vector]

    df = pd.DataFrame({'img_name': label_id,
                       'xyxy':bbox,
                       "img_vector": img_vector,
                       })

    
    return df


def build_index(db_file, indexFile):
    ntree = 30
    df = load_feature_db(db_file)
    f = len(df['img_vector'][0])  ### 向量长度 512
    t = AnnoyIndex(f, metric='euclidean')
    for i, vector in enumerate(df['img_vector']):
        t.add_item(i, vector)
    _ = t.build(ntree)
    t.save(indexFile)



if __name__ == '__main__':
    
    
    dbfile = "./result/faces.h5"
    indexfile = "./result/faces.ann"
    imgList = glob.glob("./data/*")
    build_feature_db(imgList, dbfile)
    build_index(dbfile, indexfile)
    
