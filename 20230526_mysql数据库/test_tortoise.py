#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-05-26 10:36
# @Author   : NING MEI
# @Desc     :

""" orm链接数据库 """

import json
from config import *
from tortoise import Tortoise, fields, run_async
from tortoise.models import Model
from tortoise.fields import IntField, FloatField, CharField, TextField, DatetimeField

async def new_local_sqlite3_connection():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['model.db_sqlite3']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()


async def new_local_mysql_connection():
    """ 初始化MySQL链接 spider """
    user = "root"
    pwd = "123456"
    host = "127.0.0.1"
    port = "3306"
    config = {
        "connections": {
            "rasa": f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/rasa",
        },
        "apps": {
            "rasa": {
                "models": ["model.rasa"],
                "default_connection": "rasa",
            },
        },
    }
    await Tortoise.init(config)



class sqlite3_Event(Model):
    """ 创建数据table event """
    id = IntField(pk=True)
    name = TextField()
    datetime = DatetimeField(null=True)

    class Meta:
        table = "event"

    def __str__(self):
        return self.name


async def run_sqlite():
    """ 数据创建及修改 """
    sqlite3_path = "sqlite://model/db_sqlite3" # 生成数据库文件：model/db_sqlte3
    await Tortoise.init(db_url=sqlite3_path, modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()

    event = await sqlite3_Event.create(name="Test")
    await sqlite3_Event.filter(id=event.id).update(name="Updated name")

    print(await sqlite3_Event.filter(name="Updated name").first())
    # >>> Updated name

    await sqlite3_Event(name="Test 2").save()
    print(await sqlite3_Event.all().values_list("id", flat=True))
    # >>> [1, 2]
    print(await sqlite3_Event.all().values("id", "name"))
    # >>> [{'id': 1, 'name': 'Updated name'}, {'id': 2, 'name': 'Test 2'}]




if __name__ == '__main__':


    async def dev():
        from model import rasa
        await new_local_sqlite3_connection()
        await new_local_mysql_connection()
        # item_count = await rasa.events.all().count()
        # print("item_count: ", item_count)

        # data = await rasa.events.all()
        # for line in data:
        #     data = line.data
        #     print(json.loads(data))



    # run_async(dev())
    run_async(run_sqlite())