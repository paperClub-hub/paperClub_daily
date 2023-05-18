#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-05-17 14:57
# @Author   : NING MEI
# @Desc     :


""" milvus2 索引创建 """


from milvus_db2 import COLLECTION, IMAGE_VECTOR_DIM


from typing import List, Union
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)









if __name__ == '__main__':
	import pandas as pd
	from config import COLLECTION_NAME

	utility.drop_collection(COLLECTION_NAME)
	df = pd.read_parquet("/data/1_qunosen/project/res/img_downs/embs/h14/img2_embs_vith14.parquet")
	img_names = df['img_name'].tolist()[:1000]
	img_embs = df['img_emb'].tolist()[:1000]
