# -*- coding:utf-8 -*-
import os,io
import numpy as np
from PIL import Image
import json,cv2,glob,time
import urllib.request
from milvus import Milvus, IndexType, MetricType, Status
from ensemble_feature_extractor import ensemble_extractor as extractor
from object_feature_extractor import get_image_vector as object_extractor

import warnings
warnings.filterwarnings("ignore")


"""
目的：图片物体检测及物体特征提取，并建立milvus集合； 2021-6-8
milvus == 1.1.1
"""


def milvus_collection_init(collection_name="dhome_visual_search"):
    """
    连接milvus 集合
    :param collection_name: 集合名称
    :return:
    """

    ################## milvus服务参数设置及milvus连接
    ###### milvus文档参考：https://milvus.io/cn/docs/overview.md
    _HOST = '127.0.0.1'
    _PORT = '19530'
    _DIM = 2000  # 向量维度
    _INDEX_FILE_SIZE = 1024  # 单个索引文件最大尺寸

    milvus = Milvus(host=_HOST, port=_PORT)
    server_mgs, connet_status = milvus.server_status(timeout=10)


    if connet_status == "OK":
        print("milvus服务连接成功。")
        ########## 判断集合是否存在，不存在自动建立
        _ids
        tatus, ok = milvus.has_collection(collection_name)
        if not ok:
            print(f"创建集合：{collection_name} ...")
            param = {
                'collection_name': collection_name,
                'dimension': _DIM,
                'index_file_size': _INDEX_FILE_SIZE,  # 可选
                'metric_type': MetricType.L2  # 可选
                }

            milvus.create_collection(param)
            _, is_create = milvus.has_collection(collection_name)

            if is_create:
                print(f"创建成功：{collection_name} ")
            else:
                print(f"创建失败：{collection_name} ！")

        _, collection = milvus.get_collection_info(collection_name)
        _, collection_info = milvus.get_collection_stats(collection_name)
        print(f"  collection: {collection} \n collection_info: {collection_info}")

        return milvus

    else:
        print("milvus服务连接失败 ！")





def bytes_feature_extractor(image_bytes, img_size=224):

    """
    数据流特征提取：客户端数据流特征提取
    :param image_bytes: 图片二进制数据流
    :param img_size:
    :return: array
    """

    if image_bytes is None:
        return []

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert('RGB')
        cv2_bgr = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
        bytes_embedding = extractor(cv2_bgr, img_size)
        del image_bytes, img, cv2_bgr

        return bytes_embedding

    except Exception as e:
        print(e)
        return []



def object_feature_extractor(image_bytes, img_size=224):

    """
    提取图片特征：包括物体检测 + 物体特征提取
    :param image_bytes: 图片二进制数据流
    :param img_size:
    :return: list, [["原图“, 'src', -1, bbox, emb], [[”沙发组合“, "shafazuhe", 0, bbox, emb],... ]]
    """

    if image_bytes is None:
        return [],[]
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert('RGB')
    cv2_bgr = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
    object_embedding = object_extractor(cv2_bgr, img_size)
    del image_bytes, img, cv2_bgr


    return [], object_embedding



def urlImage_object_extractor(urlPath):
    # 网络url读取图像: 物体识别及物体特征提取
    try:
        resp = urllib.request.urlopen(urlPath)
        image_bytes = np.asarray(bytearray(resp.read()), dtype="uint8")
        space_embedding,object_embedding = object_feature_extractor(image_bytes, img_size=224)
        return space_embedding, object_embedding

    except IOError:
        print("can not open url to cv2_mat:{}".format(urlPath))
        return None,None


def localImage_object_extractor(imagePath):
    # 本地读取图像：物体识别及物体特征提取
    try:
        with open(imagePath, 'rb') as fh:
            image_bytes = fh.read()
        space_embedding,object_embedding = object_feature_extractor(image_bytes,img_size=224)
        return space_embedding,object_embedding
    except Exception as e:
        print("please check imagePath:{}".format(imagePath))
        print(e)
        return None,None



def batch_records_insert(batch_imgs, batch_ids, collection_name):
    """
    分批提取和插入集合
    :param batch_imgs: 待提取图像列表
    :param batch_ids: 对应图片id列表
    :param collection_name: 索引存储的milvus集合名称
    :return:
    """

    def object_vectors_record(urlimgPath, imgId ):
        """
        读取url图像，进行物体识别及物体特征提取，并将数据转化为方便milvus使用的格式。
        :param imgPath: url图像 或 本地图片
        :param imgId: 图编编号
        :return: 两个list, 如： [[emb1],[emb2], ...],  [[img_id,原始图,src,-1,bbox], [img_id,橱柜, chugui, 0, bbox],...]
        """

        is_url_img = True
        if is_url_img:
            _, data = urlImage_object_extractor(urlimgPath) ### 网络图像
        else:
            _, data = localImage_object_extractor(urlimgPath) ### 本地图像

        embs, records = [], [] #### 存储特征向量, 物体检测信息
        if len(data)>0:
            embs.append(data[0][4])
            records.append([imgId] + data[0][:4])

        if len(data)>1:
            for ele  in data[1]:
                embs.append(ele[4])
                records.append([imgId] + ele[:4])

        return embs, records


    ########## 批处理
    def get_batch_data(imglist, idlist):

        """
        分批提取特征
        :param imglist: 待提取图像列表
        :param idlist: 对应图片id列表
        :return:
        """
        object_vectors, object_records = [], []
        for imgPath,imgId  in zip(imglist, idlist):
            embs, records = object_vectors_record(imgPath, imgId)
            object_vectors.extend(embs)
            object_records.extend(records)

        return object_vectors, object_records


    ######## 特征批插入milvus, 多次运行会重复插入！！！
    def embs_insert(collection_name, object_vectors, object_records):
        """
        批插入milvus
        :param collection_name: 集合名称
        :param object_vectors: 批向量名称
        :param object_records: 批物体检测信息
        :return: dict,
        """
        emb_insert_dict = {}

        batch_insert_status, batch_insert_ids = MILVUS.insert(collection_name=collection_name, records=object_vectors)
        if batch_insert_status.OK():
            MILVUS.flush([collection_name]) #### 数据写入磁盘
            print(f"input: {len(object_vectors)}, Insert successed: {len(batch_insert_ids)}")
            emb_insert_dict = dict([id, im_id]  for id, im_id in zip(batch_insert_ids, object_records))
            return 1, emb_insert_dict

        else:
            print("Insert failed: {}".format(len(object_vectors)))
            return 0, emb_insert_dict


    ############ 获取批处理向量及物体检测信息， 然后进行批量插入
    object_vectors, object_records = get_batch_data(batch_imgs, batch_ids)
    ### imgs_insert_dict: {insert_id1: ["img_id", '原始图','src',-1,bbox], insert_id2: ["img_id", '装饰柜','zhuangshigui',0,bbox]}
    insert_status, imgs_insert_dict = embs_insert(collection_name, object_vectors, object_records)

    return insert_status, imgs_insert_dict





def add_items_to_milvus(imglist, imgids, collection_name):
    ##### 新增图片特征
    MILVUS.load_collection(collection_name=collection_name)
    _, info = MILVUS.get_collection_stats(collection_name)

    print(f"info: {info}")

    insert_status, imgs_insert_dict = batch_records_insert(imglist, imgids, collection_name)
    _, info2 = MILVUS.get_collection_stats(collection_name)

    print(f"info2: {info2}")

    return insert_status, imgs_insert_dict



def delete_items_from_milvus(insert_milvus_ids, collection_name):

    ##### 删除 insert_milvus_ids= [1623076239970570000,1623076239970570001,1623076239970570002, ... ]

    MILVUS.load_collection(collection_name=collection_name)
    _, info = MILVUS.get_collection_stats(collection_name)

    print(f"info: {info}")

    MILVUS.delete_entity_by_id(collection_name=collection_name, id_array=insert_milvus_ids)
    MILVUS.flush([collection_name])
    _, info3 = MILVUS.get_collection_stats(collection_name)

    print(f"info3: {info3}")


def get_insert_milvus_ids(collection_name):
    ##### 获取全部插入编号
    def _get_segmentIds(collection_name):
        "获取分区编号list"
        segment_ids = []
        _, segment_info = MILVUS.get_collection_stats(collection_name)
        if segment_info.get('partitions')[0].get('segments'):
            segment_ids = [x.get("name") for x in segment_info.get('partitions')[0].get('segments')]

        return segment_ids


    def _segment2insertId(segmet_id):
        "根据分区编号，获得id列表"

        _, insert_ids = MILVUS.list_id_in_segment(collection_name =collection_name, segment_name=segmet_id)
        return insert_ids

    ##### 文件分区编号列表
    milvus_insert_ids = []
    segment_ids = _get_segmentIds(collection_name)
    if segment_ids:
        milvus_insert_ids = list(map(_segment2insertId, segment_ids))
        milvus_insert_ids = [id for ids in milvus_insert_ids for id in ids]

    return milvus_insert_ids




def demo_imgs_insert_milvus(imglist, batch_size=100, collection_name='dhome_visual_search'):
    """
    分批提取和插入milvus当中，每批图片张数不应过大（< 1000张）
    :param imglist: list, 待进行物体检测和物体特征提取的图片列表
    :param batch_size: int, 每批处理的图片张数
    :param collection_name: 索引存储的milvus集合名称
    :return:
    """

    img_dict_insert = {}
    img_dict_save = "demo_img_dict_insert.json"

    if batch_size > len(imglist):
        batch_size = len(imglist)

    batch_imgslist = [imglist[i:i+batch_size]  for i in range(0, len(imglist), batch_size)]
    print(f"输入图片：{len(batch_imgslist)} 张, batch_size={batch_size}, batch_imgslist: {len(batch_imgslist)}")

    for i,batch_imgs in enumerate(batch_imgslist):
        print(f"正在提取: {len(batch_imgs)}, {i}/{len(batch_imgs)} ... ")

        s = time.time()

        batch_insert_status, batch_insert_dict = batch_records_insert(batch_imgs, batch_imgs, collection_name)
        img_dict_insert.update(batch_insert_dict)

        time_cost = time.time() - s
        if batch_insert_status==1:

            _, batch_info = MILVUS.get_collection_stats(collection_name)
            print(f"batch: {i}/{len(batch_imgslist)} batch_info: {batch_info}, time_cost: {time_cost}")

        else:
            print(f"失败 ！， batch: {i}/{len(batch_imgslist)}")
            break


    print(json.dumps(img_dict_insert, ensure_ascii=False, indent=True), file=open(img_dict_save, "a"))

    return img_dict_insert


def testme():
    s = time.time()
    imagePath= "http://img95.699pic.com/photo/50041/1725.jpg_wh860.jpg"
    space_embedding,object_embedding = urlImage_object_extractor(imagePath)

    print(object_embedding)
    time_cost = time.time() - s

    print("object_embedding: ", len(object_embedding))

    for x in object_embedding:
        print(x)

    testPath = "./00b16bbe0cc710f6_9-7874.jpg"
    space_embedding,object_embedding = localImage_object_extractor(testPath)
    print("object_embedding: ", object_embedding[1][1])

    with open(testPath, 'rb') as f:
        d = bytes_feature_extractor(f.read())

    print("byte_emb: ", d)
    print(f"耗时：{time_cost}")





def test_milvus_insert(imglist):
    s = time.time()
    collection_name="dhome_visual_search"
    batch_size = 200
    img_dict_insert = demo_imgs_insert_milvus(imglist, batch_size, collection_name)

    time_cost = time.time() - s
    print(f"图片：{len(imglist)}, 特征数：{len(img_dict_insert)}， 共耗时：{time_cost}, 每张图平均耗时：{time_cost/len(imglist)}")


MILVUS = None

if MILVUS is None:
    MILVUS = milvus_collection_init(collection_name="dhome_visual_search")




if __name__ == '__main__':
    # testme()

    # imglist = glob.glob("/data/1_qunosen/4_train_set/1_objetct_detection/mvp_class27_set_filtered/tmp_merge/*")
    test_imgpath = "http://img95.699pic.com/photo/50041/1725.jpg_wh860.jpg"
    test_imgid = "0000001"
    # embs, recodes = object_vectors_record(test_imgpath, test_imgid, True)
    #
    # print(embs)
    # print(len(embs), len(recodes))
    # print("recodes: ", recodes)


    # # ######## 清空后重新进行：
    # _, info = MILVUS.get_collection_stats(collection_name="dhome_test_")
    # print(info)
    # MILVUS.drop_collection(collection_name="dhome_test_")
    #
    # _, info = MILVUS.get_collection_stats(collection_name="dhome_test_")
    # print(info)

    # test_milvus_insert(imglist)


    # ########### 网络图测试
    # imglist = [ "http://img95.699pic.com/photo/50041/1725.jpg_wh860.jpg",
    #             "https://img.imolacn.com/d331a28bef698e760b1f17708883742d804a6442.jpg",
    #             "https://img.imolacn.com/dd6ba2a451df5a1b9e65dc70132c42423f13fbba.jpg"
    #             ]
    # imgids = ['0001','0002','0003']

    imglist = ['http://img.imolacn.com/nestciao/5fb343e6c6e769bb345cb49765693d8a0ebb1e3b']
    imgids = ['0004']

    # collection_name="dhome_visual_search"
    collection_name="dhome_test_"
    insert_status, imgs_insert_dict = batch_records_insert(imglist, imgids, collection_name)

    print("imgs_insert_dict: ", imgs_insert_dict)
    _, info2 = MILVUS.get_collection_stats(collection_name)
    print("info2: ", info2)





    # _, info2 = MILVUS.get_collection_stats(collection_name)
    #
    # print("imgs_insert_dict:", imgs_insert_dict)
    # print(f"info2: {info2}")

    # ############ 删除
    # ids = get_insert_milvus_ids(collection_name="dhome_visual_search")
    # _, info = MILVUS.get_collection_stats(collection_name="dhome_visual_search")
    # print(ids[:10])
    # print(f"info: {info}")
    # print(len(ids))
    #
    # # delete_items_from_milvus(ids, collection_name="dhome_visual_search")
    # # _, info2 = MILVUS.get_collection_stats(collection_name="dhome_visual_search")
    # # print(f"删除后info2: {info2}")

    ###### 新增

    # add_items_to_milvus(imglist[:2000], imglist[:2000], collection_name="dhome_visual_search")

    ###### 清除集合
    # MILVUS.drop_collection(collection_name="dhome_visual_search")



