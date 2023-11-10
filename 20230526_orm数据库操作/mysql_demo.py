import json
import pymysql


class MYSQL:
	def __init__(self, host: str = '192.168.0.17',
	             port: int = 33061,
	             user: str = "root",
	             password: str = 'FfRyn2b5BKM3MNPz',
	             database: str = "spider"):

		# mysql数据库初始化
		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.mydb = self.new_mysql_connections(database)

	def new_mysql_connections(self, database: str = "spider"):
		# 连接mysql数据库
		mydb = None
		try:
			mydb = pymysql.connect(
				host=self.host,
				port=self.port,
				user=self.user,
				password=self.password,
				database=database)
		except Exception as error:
			print(f"mysql连接失败：{error}")

		return mydb

	def execute(self, sql, database: str = None):
		""" 查询sql及执行 """

		if not database:
			curser = self.mydb.cursor()
		else:
			coon = self.new_mysql_connections(database)
			curser = coon.cursor()

		try:
			curser.execute(sql)
			curser.close()
			return curser.fetchall()

		except Exception as error:
			print(f"sql执行失败：{error}")
			return tuple([])


# 连接数据库
mydb = MYSQL()
sql = "SELECT COUNT(*) FROM project"
sql = "SELECT source,url,title,cover,IF(publishers = '[]',`authors`,publishers),content FROM spider.project WHERE source = 'archdaily中文' ORDER BY RAND() LIMIT 500"
res = mydb.execute(sql)

for i, row in enumerate(res):
	if i > 10:
		break

	print(res)



