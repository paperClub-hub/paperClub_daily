import time
import math
import pymysql
import numpy as np
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

class DB():

	def __init__(self, database: str = 'dh_log'):
		host = '127.0.0.1'
		port = 33061
		user = 'root'
		password = 'FfRyn2b5BKM3MNPz'

		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.coon = self.new_mysql_connections(database)

	def sqlachemy_mysql_connections(self, batabase: str = 'dh_log'):
		""" sqlachemy 链接数据库 """
		engine = create_engine(f'mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{batabase}')
		return engine

	def new_mysql_connections(self, batabase: str = 'dh_log'):
		conn = pymysql.connect(
			host=self.host,
			port=self.port,
			user=self.user,
			password=self.password,
			database=batabase,
		)

		return conn

	def execute(self, sql, database=None):
		""" """
		if not database:
			curser = self.coon.cursor()
		else:
			coon = self.new_mysql_connections(database)
			curser = coon.cursor()

		curser.execute(sql)
		curser.close()
		
		return curser