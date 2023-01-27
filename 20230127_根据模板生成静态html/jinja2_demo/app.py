#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @ Date    : 2023/1/27 14:46
# @ Author  : paperClub
# @ Email   : paperclub@163.com
# @ Site    :


from jinja2 import Environment, FileSystemLoader


def jinja2html(data, state, rate, create_time):
    env = Environment(loader=FileSystemLoader('./'))
    template = env.get_template('template.html')
    with open("result.html", 'w') as fout:
        html_content = template.render(state=state,
                                       rate=rate,
                                       create_time=create_time,
                                       data=data)
        fout.write(html_content)


if __name__ == "__main__":
    data = []
    result = {'title': 'xxx的研究', 'author': '张三',
              'total_num': "10000", 'dup_num': "28",
              'state': "合格", 'rate': "0.28%",
              'image_path': "img.png"}

    data.append(result)
    jinja2html(data, result.get('state'), result.get('rate'), '2023-01-05 15:33 44')

