import pymysql
import pandas as pd
import asyncio
import json
import requests
from threading import Thread
import hashlib
from elasticsearch import Elasticsearch

MYSQL_USER = "root"
MYSQL_PASSWORD = "FfRyn2b5BKM3MNPz"
MYSQL_HOST = "192.168.0.17"
MYSQL_PORT = 33061
MYSQL_CONTENT_ONLINE_DB = "dh_project"
ES_HOST = "http://192.168.0.17:29201"


async def main():
    # for i in range(2):
    for i in range(215):
        # 新建线程
        # await create_thread(i)
        file_path = f"img_emb_{i}.parquet"
        await task(file_path)


# async def create_thread(index: int):
#     file_path = f"img_emb_{index}.parquet"
#     thread = Thread(target=await task(file_path=file_path), name=f"任务线程:{file_path}")
#     thread.start()
#     print(thread.name)


async def find_one_media(cursor, mid: int):
    sql = f"select table_id, file from media where id = {mid}"
    cursor.execute(sql)
    one = cursor.fetchone()
    return one[0], one[1]


async def find_project_title(cursor, pid: int):
    sql = f"select title from project where id = {pid}"
    cursor.execute(sql)
    one = cursor.fetchone()
    return one[0]


def get_vector(title: str, pid: int):
    res = requests.get(f"http://192.168.0.17:9084/emb?query={title}")
    if res.status_code != 200:
        print(f"案例{pid}查询向量失败")
    vector = res.json()
    return vector


# 建立索引
def init_es_index(es, index: str):
    """
    初始化索引
        test_zhuke_ai_all_photo
        _id = "sha1(bucket:file_key)"
    """

    settings_body = {
        "analysis": {
            "normalizer": {"lowercase": {"type": "custom", "filter": ["lowercase"]}}
        }
    }
    mapping_body = {
        "properties": {
            "media_id": {"type": "long"},
            "project_id": {"type": "long"},
            "vector": {
                "type": "dense_vector",
                "dims": 1024,
                "index": True,
                "similarity": "cosine"
            },
            "desc_vector": {
                "type": "dense_vector",
                "dims": 768,
                "index": True,
                "similarity": "cosine"
            },
            "desc_multi": {
                "properties": {
                    "analyzer_ik": {
                        "type": "text",
                        "analyzer": "ik_max_word",
                        "search_analyzer": "ik_smart"
                    },
                    "analyzer_standard": {
                        "type": "text",
                        "analyzer": "standard"
                    }
                }
            }
        }
    }

    es_body = {"mappings": mapping_body, "settings": settings_body}

    try:
        has_index = es.indices.exists(index=index)
        print("has_index:", has_index)
        if not has_index:
            es.indices.create(index=index, body=es_body)
        else:
            es.indices.put_mapping(body=mapping_body, index=index)
    except Exception as e:
        print(e)


def sha1(txt):
    return hashlib.sha1(str(txt).encode('utf-8')).hexdigest() if txt else ''


async def task(file_path: str):
    db = pymysql.Connect(host=MYSQL_HOST, user=MYSQL_USER, port=int(MYSQL_PORT), password=MYSQL_PASSWORD,
                         database=MYSQL_CONTENT_ONLINE_DB)

    cursor = db.cursor()
    # print(file_path)
    df = pd.read_parquet(file_path)

    date_list = []
    # 首次组装数据
    for m in df.itertuples():
        vectors = []
        for i in m.vector:
            vectors.append(i)
        media_id = m.dh_mid

        # 组装media_id, vector
        item = {
            "media_id": media_id,
            "vector": vectors
        }
        date_list.append(item)

        del item
        del vectors
        del m

    del df

    # 再次组装数据
    for date in date_list:
        media_id = date.get("media_id")

        # 查询bucket,project_id,file_key,desc_vector,title
        table_id, file = await find_one_media(cursor=cursor, mid=media_id)
        # print(table_id)
        table = table_id.split(":")[0]
        pid = table_id.split(":")[1]
        if table != "project":
            print(f"案例{pid}数据有问题")
        # print(file)
        file_json = json.loads(file)
        file_key = file_json.get("key")
        bucket = file_json.get("bucket")
        id_str = sha1(f"{bucket}:{file_key}")
        title = await find_project_title(cursor=cursor, pid=pid)
        desc_vector = get_vector(title=title, pid=pid)

        date["project_id"] = pid
        date["desc_vector"] = desc_vector
        date["id_str"] = id_str
        date["title"] = title

        # 写入es
        elasticsearch.index(index=index, id=id_str, document={
            "media_id": media_id,
            "project_id": pid,
            "vector": date["vector"],  # 1024
            "desc_vector": desc_vector,  # 768
            "desc_multi": {
                "analyzer_ik": title,
                "analyzer_standard": title
            },
        })

        del desc_vector, date

    # print(date_list)


if __name__ == '__main__':
    # base_path = "/data/1_qunosen/project/res/text_search_image/zhuke_downs/data/zhimo2zhuke/photo_embeddings20230706/"
    # file_path = "img_emb_0.parquet"
    # 建立索引
    index = "test_zhuke_ai_all_photo"
    elasticsearch = Elasticsearch(ES_HOST)
    init_es_index(elasticsearch, index=index)
    asyncio.run(main())
