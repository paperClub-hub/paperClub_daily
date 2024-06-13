#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2024-05-22 17:02
# @Author   : NING MEI
# @Desc     :

import json
import requests


"""
文心一言：https://qianfan.cloud.baidu.com/

"""
from os.path import abspath, dirname
import sys
_pwd = abspath(dirname(__file__))
sys.path.append(_pwd)
import random
from api_config import *
from openai import OpenAI
from http import HTTPStatus
from typing  import Dict, List
from dashscope import Generation
import sensenova


def ernie_speed8k_api(text: str="介绍一下北京", history: List[List]=None, stream:bool=False):
	"""message中的content总长度和system字段总内容不能超过24000个字符，且不能超过6144 tokens"""

	url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie_speed?access_token=" + get_access_token()
	payload = json.dumps({
		"messages": [
			{
				"role": "user",
				"content": text,
			}
		],
		"stream": stream
	})

	if history:
		payload = {"messages": [], "stream": stream}
		for hit in history:
			hist_query = hit[0]
			hist_answer = hit[1]
			payload['messages'].append({"role": "user", "content": hist_query})
			payload['messages'].append({"role": "assistant", "content": hist_answer})
		payload['messages'].append({"role": "user", "content": text })
		payload = json.dumps(payload)

	headers = {'Content-Type': 'application/json'}

	try:
		response = requests.request("POST", url, headers=headers, data=payload)
		if stream:
			for line in response.iter_lines():
				if line.strip():
					data = json.loads(line[6:])
					feed_data = parser_gpt_answer(data)
					yield {"answer": "data: " + json.dumps({"answer": feed_data}, ensure_ascii=False)}
		else:
			answer = parser_gpt_answer(response.json())
			yield answer

	except Exception as e:
		feed_data = {'answer': f"api error with info: {e}"}
		yield {"answer": "data: " + json.dumps(feed_data, ensure_ascii=False)}

	finally:
		yield {"answer": "data: " + "[DONE]\n\n"}


def ernie_speed128k_api(text:str="介绍一下北京", history: List[List]=None, stream:bool=False):
	""" message中的content总长度和system字段总内容不能超过516096个字符，且不能超过126976 tokens """

	url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-speed-128k?access_token=" + get_access_token()
	payload = json.dumps({
		"messages": [
			{
				"role": "user",
				"content": text,
			}
		],
		"stream": stream
	})

	if history:
		payload = {"messages": [], "stream": stream}
		for hit in history:
			hist_query = hit[0]
			hist_answer = hit[1]
			payload['messages'].append({"role": "user", "content": hist_query})
			payload['messages'].append({"role": "assistant", "content": hist_answer})
		payload['messages'].append({"role": "user", "content": text })
		payload = json.dumps(payload)

	headers = {'Content-Type': 'application/json'}
	try:
		response = requests.request("POST", url, headers=headers, data=payload)
		if stream:
			for line in response.iter_lines():
				if line.strip():
					data = json.loads(line[6:])
					feed_data = parser_gpt_answer(data)
					yield {"answer": "data: " + json.dumps({"answer": feed_data}, ensure_ascii=False)}
		else:
			answer = parser_gpt_answer(response.json())
			yield answer

	except Exception as e:
		feed_data = {'answer': f"api error with info: {e}"}
		yield {"answer": "data: " + json.dumps(feed_data, ensure_ascii=False)}

	finally:
		yield {"answer": "data: " + "[DONE]\n\n"}


	# headers = {'Content-Type': 'application/json'}
	# response = requests.request("POST", url, headers=headers, data=payload)
	# res = response.json()
	# print(res)
	# return res



def ernie_lite_8k_0308_api(text:str="介绍一下北京", history: List[List]=None, stream:bool=False):
	"""message中的content总长度和system字段总内容不能超过24000个字符，且不能超过6144 tokens"""

	url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-lite-8k?access_token=" + get_access_token()

	payload = json.dumps({
		"messages": [
			{
				"role": "user",
				"content": text
			}
		],
		"stream": stream
	})

	if history:
		payload = {"messages": [], "stream": stream}
		for hit in history:
			hist_query = hit[0]
			hist_answer = hit[1]
			payload['messages'].append({"role": "user", "content": hist_query})
			payload['messages'].append({"role": "assistant", "content": hist_answer})
		payload['messages'].append({"role": "user", "content": text })
		payload = json.dumps(payload)

	headers = {'Content-Type': 'application/json'}

	try:
		response = requests.request("POST", url, headers=headers, data=payload)
		if stream:
			for line in response.iter_lines():
				if line.strip():
					data = json.loads(line[6:])
					feed_data = parser_gpt_answer(data)
					yield {"answer": "data: " + json.dumps({"answer": feed_data}, ensure_ascii=False)}
		else:
			answer = parser_gpt_answer(response.json())
			yield answer

	except Exception as e:
		feed_data = {'answer': f"api error with info: {e}"}
		yield {"answer": "data: " + json.dumps(feed_data, ensure_ascii=False)}

	finally:
		yield {"answer": "data: " + "[DONE]\n\n"}



def ernie_speed_appbuilder_api(text:str= "介绍一下北京", history: List[List]=None, stream:bool=False):
	""" message中的content长度和system字段总内容不能超过11200个字符，且不能超过7168 tokens """
	url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ai_apaas?access_token=" + get_access_token()

	payload = json.dumps({
		"messages": [
			{
				"role": "user",
				"content": text,
			}
		],
		"stream": stream
	})

	if history:
		payload = {"messages": [], "stream": stream}
		for hit in history:
			hist_query = hit[0]
			hist_answer = hit[1]
			payload['messages'].append({"role": "user", "content": hist_query})
			payload['messages'].append({"role": "assistant", "content": hist_answer})
		payload['messages'].append({"role": "user", "content": text })
		payload = json.dumps(payload)

	headers = {'Content-Type': 'application/json'}
	# response = requests.request("POST", url, headers=headers, data=payload)
	# res = response.json()
	try:
		response = requests.request("POST", url, headers=headers, data=payload)
		if stream:
			for line in response.iter_lines():
				if line.strip():
					data = json.loads(line[6:])
					feed_data = parser_gpt_answer(data)
					yield {"answer": "data: " + json.dumps({"answer": feed_data}, ensure_ascii=False)}
		else:
			answer = parser_gpt_answer(response.json())
			yield answer

	except Exception as e:
		feed_data = {'answer': f"api error with info: {e}"}
		yield {"answer": "data: " + json.dumps(feed_data, ensure_ascii=False)}

	finally:
		yield {"answer": "data: " + "[DONE]\n\n"}



def ernie_yi_34b_chat_api(text:str= "介绍一下北京", history: List[List]=None, stream:bool=False):
	""" message中的content总长度不能超过8000 个字符 """
	url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/yi_34b_chat?access_token=" + get_access_token()
	payload = json.dumps({
		"messages": [
			{
				"role": "user",
				"content": text,
			}
		],
		"stream": stream
	})

	if history:
		payload = {"messages": [], "stream": stream}
		for hit in history:
			hist_query = hit[0]
			hist_answer = hit[1]
			payload['messages'].append({"role": "user", "content": hist_query})
			payload['messages'].append({"role": "assistant", "content": hist_answer})
		payload['messages'].append({"role": "user", "content": text })
		payload = json.dumps(payload)

	headers = {'Content-Type': 'application/json'}
	# response = requests.request("POST", url, headers=headers, data=payload)
	# res = response.json()
	# return res
	try:
		response = requests.request("POST", url, headers=headers, data=payload)
		if stream:
			for line in response.iter_lines():
				if line.strip():
					data = json.loads(line[6:])
					feed_data = parser_gpt_answer(data)
					yield {"answer": "data: " + json.dumps({"answer": feed_data}, ensure_ascii=False)}
		else:
			answer = parser_gpt_answer(response.json())
			yield answer

	except Exception as e:
		feed_data = {'answer': f"api error with info: {e}"}
		yield {"answer": "data: " + json.dumps(feed_data, ensure_ascii=False)}

	finally:
		yield {"answer": "data: " + "[DONE]\n\n"}


def ernie_tiny8k_api(text:str= "介绍一下北京", history: List[List]=None, stream:bool=False):
	"""message中的content总长度和system字段总内容不能超过24000个字符，且不能超过6144 tokens"""

	url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-tiny-8k?access_token=" + get_access_token()
	payload = json.dumps({
		"messages": [
			{
				"role": "user",
				"content": text,
			}
		],
		"stream": stream
	})

	if history:
		payload = {"messages": [], "stream": stream}
		for hit in history:
			hist_query = hit[0]
			hist_answer = hit[1]
			payload['messages'].append({"role": "user", "content": hist_query})
			payload['messages'].append({"role": "assistant", "content": hist_answer})
		payload['messages'].append({"role": "user", "content": text })
		payload = json.dumps(payload)

	headers = {'Content-Type': 'application/json'}
	try:
		response = requests.request("POST", url, headers=headers, data=payload)
		if stream:
			for line in response.iter_lines():
				if line.strip():
					data = json.loads(line[6:])
					feed_data = parser_gpt_answer(data)
					yield {"answer": "data: " + json.dumps({"answer": feed_data}, ensure_ascii=False)}
		else:
			answer = parser_gpt_answer(response.json())
			yield answer

	except Exception as e:
		feed_data = {'answer': f"api error with info: {e}"}
		yield {"answer": "data: " + json.dumps(feed_data, ensure_ascii=False)}

	finally:
		yield {"answer": "data: " + "[DONE]\n\n"}



def ali_qwen_api(text:str="介绍一下北京", model_name:str = "qwen-turbo", history: List[List]=None, stream:bool=False):
	"""
	qwen-turbo: 模型支持8k tokens上下文，为了保证正常的使用和输出，API限定用户输入为6k tokens。免费token额度400万
	qwen-plus: 模型支持32k tokens上下文，为了保证正常的使用和输出，API限定用户输入为30k tokens。免费token额度400万
	"""
	# model_name = "qwen-turbo"
	# model_name = "qwen-plus"
	# model_name = "qwen-1.8b-chat"
	messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
	if history:
		for hit in history:
			hist_query = hit[0]
			hist_answer = hit[1]
			messages.append({"role": "user", "content": hist_query})
			messages.append({"role": "assistant", "content": hist_answer})
	messages.append({"role": "user", "content": text})


	try:
		response = Generation.call(model=model_name,
		                           messages=messages,
		                           seed=random.randint(1, 10000),
		                           result_format='message',
		                           stream=stream,
		                           parameters={"top_p": 0.8, "temperature": 1.0}
		                           )

		if stream:
			feed_datas = []
			for res in response:
				if res.status_code == HTTPStatus.OK:
					answer = res.output.choices[0]['message']['content']
					feed_datas.append(answer)
					yield {"answer": "data: " + json.dumps({"answer": answer}, ensure_ascii=False)}
		else:
			if response.status_code == HTTPStatus.OK:
				answer = response.output.choices[0]['message']['content']
				yield {"answer": "data: " + json.dumps({"answer": answer}, ensure_ascii=False)}

	except Exception as e:
		feed_data = {'answer': f"api error with info: {e}"}
		yield {"answer": "data: " + json.dumps(feed_data, ensure_ascii=False)}

	finally:
		yield {"answer": "data: " + "[DONE]\n\n"}



def qianwen_others_api(text: str= "介绍一下北京", model_name:str = "moonshot-v1-128k", history: List[List]=None, stream:bool=False):
	"""千问其他模型"""
	messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
	if history:
		for hit in history:
			hist_query = hit[0]
			hist_answer = hit[1]
			messages.append({"role": "user", "content": hist_query})
			messages.append({"role": "assistant", "content": hist_answer})

	messages.append({"role": "user", "content": text})


	try:
		response = Generation.call(
			model=model_name,
			messages=messages,
			stream=stream,
		)

		if stream:
			for res in response:
				if res.status_code == HTTPStatus.OK:
					answer = res.output.choices[0]['message']['content']
					yield {"answer": "data: " + json.dumps({"answer": answer}, ensure_ascii=False)}
		else:
			if response.status_code == HTTPStatus.OK:
				answer = response.output.choices[0]['message']['content']
				yield {"answer": "data: " + json.dumps({"answer": answer}, ensure_ascii=False)}

	except Exception as e:
		feed_data = {'answer': f"api error with info: {e}"}
		yield {"answer": "data: " + json.dumps(feed_data, ensure_ascii=False)}

	finally:
		yield {"answer": "data: " + "[DONE]\n\n"}



def parser_gpt_answer(res: Dict):
	""""""
	if "result" in res: # 百度
		answer = res.get('result')
		total_tokens = res.get("usage", {}).get("total_tokens")
	else: # 阿里
		answer = res.get("output", {}).get("choices", [{}])[0].get('message', {}).get("content")
		total_tokens = res.get("usage", {}).get("total_tokens")

	return answer



def moonshot(text:str="介绍一下北京", history: List[List]=None, stream:bool=False):
	""" 已安装 pip install --upgrade 'openai>=1.0'
	"""
	model_name = 'moonshot-v1-8k' # moonshot-v1-32k, moonshot-v1-128k
	client = MiMiClient()
	messages = [{"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。"}]
	if history:
		for hit in history:
			hist_query = hit[0]
			hist_answer = hit[1]
			messages.append({"role": "user", "content": hist_query})
			messages.append({"role": "assistant", "content": hist_answer})

	messages.append({"role": "user", "content": text})
	response = client.chat.completions.create(
		model=model_name,
		messages=messages,
		temperature=0.3,
		stream=stream,
	)

	try:
		if stream:
			feed_datas = []
			for idx, chunk in enumerate(response):
				chunk_message = chunk.choices[0].delta.content
				if not chunk_message:
					continue
				feed_datas.append(chunk_message)  # save the message
				yield {"answer": "data: " + json.dumps({"answer": chunk_message}, ensure_ascii=False)}
		else:
			result = response.choices[0].message.content
			yield {"answer": "data: " + json.dumps({"answer": result}, ensure_ascii=False)}

	except Exception as e:
		feed_data = {'answer': f"api error with info: {e}"}
		yield {"answer": "data: " + json.dumps(feed_data, ensure_ascii=False)}

	finally:
		yield {"answer": "data: " + "[DONE]\n\n"}


def baichuan_api(text:str="介绍一下北京", history: List[List]=None, stream:bool=False):
	"""百川大模型"""
	model_name = "Baichuan2-Turbo"
	model_name = "Baichuan4"
	client = BaichuanClient()
	messages = []
	if history:
		for hit in history:
			hist_query = hit[0]
			hist_answer = hit[1]
			messages.append({"role": "user", "content": hist_query})
			messages.append({"role": "assistant", "content": hist_answer})

	messages.append({"role": "user", "content": text})
	response = client.chat.completions.create(model=model_name,messages=messages,stream=stream, temperature=0.3 )
	try:
		if stream:
			for idx, chunk in enumerate(response):
				chunk_message = chunk.choices[0].delta.content
				if not chunk_message:
					continue
				yield {"answer": "data: " + json.dumps({"answer": chunk_message}, ensure_ascii=False)}
		else:
			result = response.choices[0].message.content
			yield {"answer": "data: " + json.dumps({"answer": result}, ensure_ascii=False)}

	except Exception as e:
		feed_data = {'answer': f"api error with info: {e}"}
		yield {"answer": "data: " + json.dumps(feed_data, ensure_ascii=False)}

	finally:
		yield {"answer": "data: " + "[DONE]\n\n"}


def hunyuan_api(text: str="介绍一下北京", history: List[List]=None, stream:bool=False):
	"""腾讯混元模型"""
	client, req = HunYuanClient()
	params = {"Messages": [], "Stream": stream}
	if history:
		for hit in history:
			hist_query = hit[0]
			hist_answer = hit[1]
			params['Messages'].append({"Role": "user", "Content": hist_query})
			params['Messages'].append({"Role": "assistant", "Content": hist_answer})

	params['Messages'].append({"Role": "user", "Content": text})
	# print("params: ", params)
	req.from_json_string(json.dumps(params))
	try:
		resp = client.ChatPro(req)
		if stream:
			for line in resp:
				answer = json.loads(line.get('data')).get("Choices", [{}])[0].get("Delta", {}).get("Content", '')
				yield {"answer": "data: " + json.dumps({"answer": answer}, ensure_ascii=False)}
			else:
				result = resp.get('Choices', [{}])[0].get("Message", {}).get("Content", "")
				# print("result: ", result)
				yield {"answer": "data: " + json.dumps({"answer": result}, ensure_ascii=False)}

	except Exception as e:
		feed_data = {'answer': f"api error with info: {e}"}
		yield {"answer": "data: " + json.dumps(feed_data, ensure_ascii=False)}

	finally:
		yield {"answer": "data: " + "[DONE]\n\n"}



def sensecore_api(text: str="介绍一下北京", model_name="SenseChat-Turbo", stream = True):
	"""商汤日日新模型"""
	resp = sensenova.ChatSession.create(system_prompt=[{"role": "system", "content": "You are a translation expert."}])
	session_id = resp["session_id"]
	resp = sensenova.ChatConversation.create(
		action="next",
		content=text,
		model=model_name,
		session_id=session_id,
		stream=stream,
		know_ids=[],
		knowledge_config={
			"control_level": "normal",
			"knowledge_base_result": True,
			"knowledge_base_configs": []
		},
		max_new_tokens=4096
	)

	try:
		if not stream:
			resp = [resp]

		for part in resp:
			if stream:
				delta = part["data"]["delta"]
				yield {"answer": "data: " + json.dumps({"answer": delta}, ensure_ascii=False)}
			else:
				delta = part["data"]["message"]
				yield {"answer": "data: " + json.dumps({"answer": delta}, ensure_ascii=False)}

	except Exception as e:
		feed_data = {'answer': f"api error with info: {e}"}
		yield {"answer": "data: " + json.dumps(feed_data, ensure_ascii=False)}

	finally:
		yield {"answer": "data: " + "[DONE]\n\n"}



if __name__ == '__main__':
	print("------------------------------------------ GPT ")
	history = [['陕西的省会城市是哪个？', '西安']]
	text = "江苏呢？四川呢？"
	# # res = ernie_speed8k_api(text=text, history=history, stream=True)
	# # res = ernie_speed128k_api(text=text, history=history, stream=True)
	# # res = ernie_lite_8k_0308_api(text=text, history=history, stream=False)
	# # res = ernie_speed_appbuilder_api(text=text, history=history, stream=False)
	# # res = ernie_yi_34b_chat_api(text=text, history=history, stream=True)
	# res = ernie_tiny8k_api(text=text, history=None, stream=True)
	# res = ali_qwen_api(text=text, history=None, stream=True)
	# # res = ali_qwen_api2(text, history=None, stream=False)
	#
	# res = baichuan_api(text='江苏呢？', history=[["河南的省的省会城市是哪个？", "郑州"]], stream=True)
	# res = hunyuan_api(text='江苏呢？', history=[["河南的省的省会城市是哪个？", "郑州"]], stream=True)
	result = ""

	# model_name = 'qwen1.5-72b-chat'
	# res = ali_qwen_api(text='江苏呢？', model_name=model_name, history=[['河南的省会城市哪个？', '郑州']], stream=True)
	model_name = 'moonshot-v1-32k'
	model_name = 'moonshot-v1-128k'
	model_name = 'yi-large'
	res = qianwen_others_api(text, model_name=model_name, history=None, stream=True)
	# res = ali_qwen_api(text, model_name='qwen-max')
	# res = sensecore_api(text)
	for answer_result in res:
		print("answer_result: ", answer_result)
		response = {"result": answer_result['answer']}
		# print("response: ", response)
		answer = answer_result['answer'][6:]
		if not answer.startswith('[DONE]'):
			answer = json.loads(answer).get("answer")
			feed_answer = "data: " + json.dumps({"answer": answer})
			response.update({"result": feed_answer })
			history[-1][-1] = answer
			# print("answer: ", answer)
			# result +=answer
			result = answer
		data = response.get("result")[6: ]
		# asw = json.loads(data) if not data.startswith('[DONE]') else {}
		# print(f"asw: {asw} ")
	print(result)

