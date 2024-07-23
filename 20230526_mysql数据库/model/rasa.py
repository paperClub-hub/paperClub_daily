#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-05-26 11:15
# @Author   : NING MEI
# @Desc     :


from tortoise.models import Model
from tortoise.fields import IntField, CharField, SmallIntField, DatetimeField, JSONField, FloatField, TextField

class events(Model):
	""" events """

	class Meta:
		table = "events"

	id = IntField(pk=True)
	sender_id = CharField(255, default="", description="")
	type_name = CharField(255, default="", description="")
	timestamp = FloatField(default=0, description="shijian")
	intent_name = CharField(255, default=0, description='')
	action_name = CharField(255, default=0, description='')
	data = TextField(default='', description='')
