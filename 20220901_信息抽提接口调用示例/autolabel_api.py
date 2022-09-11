#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-05 12:00
# @Author   : paperClub
# @Desc     :


from flask import Flask, request, jsonify
from paddlenlp import Taskflow


app = Flask(__name__)

schema = ['空间', '风格属性', '家具物体', '颜色品牌', '特征属性']

ie = Taskflow('information_extraction',
              schema=schema,
              task_path='./best',
              device_id=-1) # cpu device only


def convert(result):
    """ 提取转化 """
    result = result[0]
    formatted_result = []
    for label, ents in result.items():
        for ent in ents:
            formatted_result.append(
                {
                    "label": label,
                    "start_offset": ent['start'],
                    "end_offset": ent['end']
                })

    return formatted_result


@app.route('/uie', methods=['POST'])
def get_result():
    text = request.form['text']
    result = ie(text)
    formatted_result = convert(result)
    print(f"text: {text} 结果：{result}")

    return jsonify(formatted_result)




def demo_requeet_postapi():
    """ 示例：请求flask post api"""
    import json
    import requests
    text = '客厅我们采用了灰色的皮质沙发'
    query_data = {'text': text}
    r = requests.post("http://192.168.0.17:5739/uie", data=query_data)
    print(json.loads(r.text))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5739)

