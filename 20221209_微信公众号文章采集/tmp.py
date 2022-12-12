#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-11-07 10:35
# @Author   : paperclub
# @Desc     :


import requests
from requests.exceptions import RequestException
from lxml import etree
import csv
import re
import time
from urllib import parse
import time
def get_page(url):
    """
        获取网页的源代码
    :param url:
    :return:
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def timeswitch(chuo):
    tupTime = time.localtime(chuo)  # 秒时间戳
    stadardTime = time.strftime("%Y-%m-%d %H:%M:%s", tupTime)
    return stadardTime

def parse_page(text):
    """
        解析网页源代码
    :param text:
    :return:
    """
    html = etree.HTML(text)

    '''
    movie_name = html.xpath("//*[@id='sogou_vr_11002601_title_0']/text()[1]")
    actor = html.xpath("//p[@class='star']/text()")
    actor = list(map(lambda item: re.sub('\s+', '', item), actor))
    time = html.xpath("//p[@class='releasetime']/text()")
    grade1 = html.xpath("//p[@class='score']/i[@class='integer']/text()")
    grade2 = html.xpath("//p[@class='score']/i[@class='fraction']/text()")
    new = [grade1[i] + grade2[i] for i in range(min(len(grade1), len(grade2)))]
    ranking = html.xpath("///dd/i/text()")
    return zip(ranking, movie_name, actor, time, new)
    '''
    biaotinew = list()
    biaoti = html.xpath("//div[@class='txt-Box']/h3/a")
    for bt in biaoti:
        b = bt.xpath("string(.)")
        biaotinew.append(b)

    wangzhinew = list()
    base_url = 'https://weixin.sogou.com'
    wangzhi = html.xpath("//div[@class='txt-Box']/h3//@href")
    for wz in wangzhi:
        w = "".join(list(base_url)+wangzhi)
        wangzhinew.append(w)

    zhaiyaonew = list()
    zhaiyao = html.xpath("//p[@class='txt-info']")
    for bt in zhaiyao:
        b = bt.xpath("string(.)")
        zhaiyaonew.append(b)

    gzh  = html.xpath("//a[@class='account']/text()")

    lastnew = list()
    shijiannew = list()
    shijian = html.xpath("//div[2]/div/span")
    for bt in shijian:
        b = bt.xpath("string(.)")
        shijiannew.append(b)
    for bp in shijiannew :
        newstr  = re.findall(r"\d+\.?\d*",bp)
        # ['1.45', '5', '6.45', '8.82']
        lastor = ''.join(newstr)
        lastnew.append(timeswitch(int(lastor)))
    # print(lastnew)
    return zip(biaotinew,wangzhinew,zhaiyaonew,gzh,lastnew)


def change_page1(number):
    """
        翻页
    :param number:
    :return:
    """
    base_url ='https://weixin.sogou.com/weixin?oq=&query=python&_sug_type_=1&sut=0&lkt=0%2C0%2C0&s_from=input&ri=1&_sug_=n&type=2&sst0=1604564741184&page='
    url = base_url +str(number)+'&ie=utf8&p=40040108&dp=1&w=01015002&dr=1'
    return url




import time

def main():
    """
    主函数
    :return:
    """
    f = open('message.csv', 'a+', encoding='utf-8-sig', newline="")  # newline取消空行
    csv_writer = csv.writer(f)
    csv_writer.writerow(["文章名称","文章链接地址","摘要","公众号名称","发布时间"])
    f.close()
    for number in range(2):
        url = change_page1(number)
        text = get_page(url)

        print("url: ", url)

        time.sleep(10)
        result = parse_page(text)
        print("result: ", result)
        for a,b,c,d,e in result:
            print("a: ===>  ", a)
