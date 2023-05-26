#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-05-26 13:32
# @Author   : NING MEI
# @Desc     :


""" pymysql直接连数据库 """

from config import *
import pymysql
import json


def mysql_init():
	""""""
	db = pymysql.connect(
		host=MYSQL_HOST,
		port=int(MYSQL_PORT),
		user=MYSQL_USER,
		password=MYSQL_PASSWORD,
		database="rasa"
	)
	cursor = db.cursor()

	return db, cursor


conn, cursor = None, None
if cursor is None:
	conn, cursor = mysql_init()

cursor.execute('SELECT * FROM `events`')
result = cursor.fetchall()

for line in result:
	id, sender_id, type_name, timestamp, intent_name, action_name, data = line
	print(json.loads(data))



