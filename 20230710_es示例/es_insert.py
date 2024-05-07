#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2024-03-02 8:43
# @Author   : NING MEI
# @Desc     :






ES_HOST_LOCAL = 'http://es-container-local:9200/'
ES_CLOUD_ID = None
ES_USER = 'zzp'
ES_PASSWORD = '123456'
ES_API_KEY = '123456'
ES_CONNECT_PARAMS = 'aaa'
ES_SIGNATURE = 'qanything/bm25_v240320'



debug_logger = logging.getLogger('debug_logger')

class DOCKER_ES:
	def __init__(self,
	             index_name: List[str] = None,
	             url=ES_HOST_LOCAL, cloud_id=ES_CLOUD_ID,
	             user=ES_USER, password=ES_PASSWORD,
	             api_key=ES_API_KEY,
	             connect_params: Dict[str, Any] = ES_CONNECT_PARAMS
	             ):
		if index_name is None:
			raise ValueError("Please provide `index_name` in str or list.")

		self.index_name = [index.lower() for index in index_name]
		connects = deepcopy(connect_params) if connect_params is not None else {}
		if url:
			connects['hosts'] = url
		elif cloud_id:
			connects['cloud_id'] = cloud_id
		else:
			raise ValueError("Please provide either elasticsearch url or cloud_id.")

		if api_key:
			connects['api_key'] = api_key
		elif user and password:
			connects['basic_auth'] = (user, password)
		self.client = Elasticsearch(**connects, headers={"user-agent": ES_SIGNATURE})

		try:
			debug_logger.info(f"##ES## - success to connect to {self.client.info().body}")
		except Exception as e:
			raise RuntimeError(f"Elasticsearch client initialization failed: {e}\nConnection setup: {connects}")

	def _create_index(self):
		for index_name in self.index_name:
			index_name = index_name.lower()
			if self.client.indices.exists(index=index_name):
				debug_logger.info(f"##ES## - Index {index_name} already exists. Skipping creation.")
			else:
				settings = {
					"index": {
						"similarity": {
							"custom_bm25": {
								"type": "BM25",
								"k1": "1.3",
								"b": "0.6"
							}
						}
					}
				}
				mappings = {
					"properties": {
						'file_id': {
							'type': 'keyword',
							'index': True
						},
						"content": {
							"type": "text",
							"similarity": "custom_bm25",
							"index": True,
							"analyzer": "ik_smart",
							"search_analyzer": "ik_smart",
						}
					}
				}
				debug_logger.info(f"##ES## - Creating index {index_name} with:\nmappings: {mappings}\nsettings: {settings}")
				self.client.indices.create(index=index_name, mappings=mappings, settings=settings)


	def _create_index_custom(self):

		all_indexes = self.show_all_index()
		print(f"all_indexes: ---->>>>>  {len(all_indexes)}, ----->>>> {all_indexes}")
		debug_logger.info("创建ES索引， _create_index_custom ... ")
		for index_name in self.index_name:
			index_name = index_name.lower()
			if self.client.indices.exists(index=index_name):
				debug_logger.info(f" ES索引已经存在， 自动删除：{index_name}")
				print(" 删除ES索引已经存在================================== >>>> ", index_name)
				self.client.indices.delete(index=index_name)

			settings = {
					"index": {
						"similarity": {
							"custom_bm25": {
								"type": "BM25",
								"k1": "1.3",
								"b": "0.6"
							}
						}
					}
				}
			mappings = {
					"properties": {
						'file_id': {
							'type': 'keyword',
							'index': True
						},
						"content": {
							"type": "text", # text
							"similarity": "custom_bm25",
							"index": True,
							"analyzer": "ik_smart",
							"search_analyzer": "ik_smart",
						},
						"keyword": {
							"type": "keyword",
							"similarity": "custom_bm25",
							"index": True,
						}
					}
				}
			print("mappings ------>>>> ", mappings)
			self.client.indices.create(index=index_name, mappings=mappings, settings=settings)


	async def insert_custom(self, data, refresh=False):
		self._create_index_custom()
		ids = [item['metadata']["chunk_id"] for item in data]
		for index_name in self.index_name:
			index_name = index_name.lower()
			actions = []
			for item in data:
				content = item.get('content') # 文本
				words = [x[0] for x in ES.do_by_paddle(content)[-1]]
				if not words:
					words = [ content ]

				# print("words: ----->>>> ", words)

				item['keyword'] = words
				action = {
					"_op_type": "index",
					"_id": item['metadata']["chunk_id"]
				}
				action.update(item)
				actions.append(action)
			# print("actions ---->>>>>>> ", actions)

			documents_written, errors = helpers.bulk(
				client=self.client,
				actions=actions,
				refresh=True,
				index=index_name,
				stats_only=True,
				raise_on_error=False,
			)

			print(" errors -------------->>>>> ", errors)
			print(" documents_written ---------------->>>> ", documents_written)

		print("ids: ", len(ids))


	async def insert(self, data, refresh=False):
		self._create_index()
		ids = [item['metadata']["chunk_id"] for item in data]
		for index_name in self.index_name:
			index_name = index_name.lower()
			actions = []
			for item in data:
				action = {
					"_op_type": "index",
					"_id": item['metadata']["chunk_id"]
				}
				action.update(item)
				actions.append(action)
			try:
				documents_written, errors = helpers.bulk(
					client=self.client,
					actions=actions,
					refresh=False,
					index=index_name,
					stats_only=True,
					raise_on_error=False,
				)
				debug_logger.info(f"##ES## - success to add: {documents_written}\nfail to add to index: {errors}")
				if refresh:
					self.client.indices.refresh(index=index_name)
					debug_logger.info(f"##ES## - finish insert chunks!")
			except Exception as e:
				return f"Error adding texts: {e}"

		return f"success to add chunks: {ids[:5]} ... in index: {self.index_name[:5]} ..."







if __name__ == '__main__':
	print()

	query = "IMOLA 屈红森"
	query = "imola"
	query = "屈红森2024年工作汇报"
	kb_id = "KB88720f733d87425abb24f0379c6dfa87"
	es_inedx = f'zzp++{kb_id}'  # EMB-ES测试
	es_inedx = f'zzp++{kb_id}++custom'
	# ES = DOCKER_ES(index_name=[es_inedx])
	ES = DOCKER_ES(index_name=[es_inedx])
	# ES._create_index_custom()


	def test_insert(force_build=True, is_insert=True):
		""""""
		index_name = 'zzp++KB88720f733d87425abb24f0379c6dfa87++custom'
		index_name = index_name.lower()

		#  -------------------------------- 创建索引
		if ES.client.indices.exists(index=index_name):
			print(f"----------------------------------》》》 已存在 {index_name}")
			if force_build:
				print("-------------------->>> 准备删除: ", index_name)
				res = ES.client.indices.delete(index=index_name)
				print("已存在，准备删除 res: ", res)
		else:
			print(f" ----------------------------------》》》 不存在，准备创建: {index_name}")

			settings = {
				"index": {
					"similarity": {
						"custom_bm25": {
							"type": "BM25",
							"k1": "1.3",
							"b": "0.6"
						}
					}
				}
			}

			mappings = {
				"properties": {
					'file_id': {
						'type': 'keyword',
						'index': True
					},
					"content": {
						"type": "text",  # text
						"similarity": "custom_bm25",
						"index": True,
						"analyzer": "ik_smart",
						"search_analyzer": "ik_smart",
					},
					"keyword": {
						"type": "keyword",
						"similarity": "custom_bm25",
						"index": True,
					}
				}
			}
			res = ES.client.indices.create(index=index_name, mappings=mappings, settings=settings)
			print(" ----------》》》》 不存在，准备创建res: ", res)

		#  -------------------------------- 插入数据
		insert_data = [{'_op_type': 'index',
		                '_id': '0d24274bf199420ba43678921b61159f_0',
		                'file_id': '0d24274bf199420ba43678921b61159f',
		                'content': './苏州科技公司晁国轶年终个人总结',
		                'metadata': {'file_name': '2024年会个人总结-晁国轶.pptx',
		                             'file_path': '2024年会个人总结-晁国轶.pptx',
		                             'chunk_id': '0d24274bf199420ba43678921b61159f_0',
		                             'timestamp': '202405061618'},
		                'keyword': ['苏州', '科技公司', '晁国轶', '年终']},
		               {'_op_type': 'index',
		                '_id': '0d24274bf199420ba43678921b61159f_1',
		                'file_id': '0d24274bf199420ba43678921b61159f',
		                'content': "IMOLA's Decision-Making Conference",
		                'metadata': {'file_name': '2024年会个人总结-晁国轶.pptx',
		                             'file_path': './2024年会个人总结-晁国轶.pptx',
		                             'chunk_id': '0d24274bf199420ba43678921b61159f_1',
		                             'timestamp': '202405061618'},
		                'keyword': ['IMOLA']},
		               {'_op_type': 'index',
		                '_id': '0d24274bf199420ba43678921b61159f_10',
		                'file_id': '0d24274bf199420ba43678921b61159f',
		                'content': '工作内容回顾',
		                'metadata': {'file_name': '2024年会个人总结-晁国轶.pptx',
		                             'file_path': './2024年会个人总结-晁国轶.pptx',
		                             'chunk_id': '0d24274bf199420ba43678921b61159f_10',
		                             'timestamp': '202405061618'},
		                'keyword': ['工作']}]


		if is_insert:
			print(" -------------》》》》》》 准备插入： ", index_name)
			documents_written, errors = helpers.bulk(
				client=ES.client,
				actions=insert_data,
				refresh=True,
				index=index_name,
				stats_only=True,
				raise_on_error=False,
			)

			print(" -------------》》》》》》 插入documents_written： ", documents_written)
			print("-------------》》》》》》 插入errors: ", errors)

		else:
			print(" -------------》》》》》》 开始搜索： ", index_name)
			count = 0
			_res  = ES.client.cat.indices(format="json")
			info = [d for d  in _res if d.get('index') == index_name] or {}
			if info:
				count = info[0].get('docs.count')
			print("索引文档数量: --------------------->>>>  ", count)

			query = "工作"
			query = "微信"
			query_body = {
				"query": {
					"match": {
						"content": {
							"query": query,
						}
					}
				},
			}
			query_body = {
				"query": {
					"match": {
						"keyword": {
							"query": query
						}
					}
				}
			}

			res = ES.client.search(index=index_name, **query_body, source=['file_id', 'content', 'metadata'])
			print(" ------------------------------->>>> 搜索res: ", res)





	test_insert(force_build=False, is_insert=False)




