#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @ Date    : 2023/1/5 13:55
# @ Author  : paperClub
# @ Email   : paperclub@163.com
# @ Site    :


from flask import Flask, request, render_template

app = Flask(__name__, template_folder='./templates')


def flask2html(create_time, state, rate):
    with app.app_context():
        template = render_template('home.html', create_time=create_time,state=state,rate=rate)
        with open('result.html', 'tw') as f:
            f.write(str(template))


if __name__ == '__main__':
    flask2html('2022', '合格', '0.28%')