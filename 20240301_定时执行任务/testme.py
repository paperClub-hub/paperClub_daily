#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2024-02-27 14:38
# @Author   : NING MEI
# @Desc     :



from datetime import datetime
import schedule
import time


def job(arg1=None, arg2=None):
	date_now = datetime.now()
	print(f"启动: {arg1}, arg2: {arg2}, date_now: {date_now}")


def my_task():
	arg1_value = datetime.now()
	arg2_value = "当前时间："
	time_span = 60
	# 每 xx 秒执行一次
	# schedule.every(time_span).seconds.do(lambda: job(arg1_value, arg2_value))
	# 每天凌晨 00:00执行
	schedule.every().day.at("00:00").do(lambda: job(arg1_value, arg2_value))

	while True:
		schedule.run_pending()
		time.sleep(1)

if __name__ == '__main__':
	my_task()
