#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-05-25 10:51
# @Author   : NING MEI
# @Desc     :


""" 模拟链接数据库 """

""" tortoise学习可参考官网 """

from tortoise import Tortoise, run_async
from tortoise.contrib.fastapi import register_tortoise


async def new_mysql_connection(host, port, user, pwd):
    """初始化MySQL链接"""
    config = {
        "connections": {
            "spider": f"mysql://{user}:{pwd}@{host}:{port}/spider",
        },
        "apps": {
            "spider": {
                "models": ["spider"], # 'spider' 表示 ‘./spider.py’，'app.model.spider' 表示 './app/model/spider.py'
                "default_connection": "spider",
            },
        },
    }
    await Tortoise.init(config)



mysql_user = 'root'
mysql_password = 'FfRyn2b5BKM3MNPz'
mysql_host = '192.168.0.17'
mysql_port = '33061'

# 链接数据库


# 查询字段

async def test_mysql():
    from tqdm.auto import tqdm
    from tortoise import Tortoise
    # from app.model import spider
    import pandas as pd
    import spider
    import math

    # 17环境mysql服务器
    await new_mysql_connection(host=mysql_host, port=mysql_port, user=mysql_user, pwd=mysql_password)

    # 链接 spider库, zhimo_project表, 查询top10000案例：
    # SELECT id FROM spider.zhimo_project WHERE has_detail = 1 AND filter_items != '' AND publish_time IS NOT NULL ORDER BY view_num DESC LIMIT 10000;

    # project_ids = await spider.zhimo_project.filter(has_detail=1).order_by("-view_num").values_list("id", flat=True)
    project_ids = await spider.zhimo_project.filter(has_detail=1).filter(filter_items__not='').filter(publish_time__not='').order_by("-view_num").values_list("id", flat=True)
    print(len(project_ids))

    # 获取top10000案例对应图片url和图片大小及案例编号
    new_width = 336
    resized_img = False
    zhimo_project_medias = []
    for i, project_id in tqdm(enumerate(project_ids)):

        if i > 10:
            break

        zhimo_project_detail = await spider.zhimo_project_detail.get_or_none(id=project_id)
        if not zhimo_project_detail:
            continue

        if not zhimo_project_detail.info:
            continue

        zhimo_contents = zhimo_project_detail.info.get("contents", [])
        zhimo_detailContents = zhimo_project_detail.info.get("detailContents", [])

        if zhimo_contents:
            for item in zhimo_contents:
                if item.get("imgUrl", '') and item.get("id"):
                    url = item.get("imgUrl")
                    width = item.get("width", 0)
                    height = item.get("height", 0)
                    if not any([width, height]):
                        continue

                    if resized_img:
                        new_height = int(math.ceil(new_width * height / width))
                        url = f"{url}?x-oss-process=image/auto-orient,1/resize,m_fill,w_{new_width},h_{new_height},limit_0"

                    zhimo_project_medias.append({
                        "url": url,
                        "caption": {"project_id": project_id, "media_id": item.get("id"),
                                    "width": width,"height": height}
                    })

        if zhimo_detailContents:
            for item in zhimo_detailContents:
                # print(item)
                if item.get("imgUrl", '') and item.get("id"):
                    url = item.get("imgUrl")
                    width = item.get("width", 0)
                    height = item.get("height", 0)
                    if not any([width, height]):
                        continue

                    if resized_img:
                        new_height = int(math.ceil(new_width * height / width))
                        url = f"{url}?x-oss-process=image/auto-orient,1/resize,m_fill,w_{new_width},h_{new_height},limit_0"

                    zhimo_project_medias.append({
                        "url": url,
                        "caption": {"project_id": project_id, "media_id": item.get("id"),
                                    "width": width,"height": height}
                    })

    zhimo_project_medias = pd.DataFrame(zhimo_project_medias)
    print(zhimo_project_medias)


if __name__ == '__main__':
    run_async(test_mysql())