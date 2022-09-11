import json
import time
import requests
from parsel import Selector

""" 小红书笔记下载"""

headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8', 'cache-control': 'max-age=0', 'cookie': 'xhsTrackerId=6e426eda-59f5-41ba-c1ee-97875f805953; extra_exp_ids=wx_engage_bar_exp,wx_launch_open_app_duration_clt,wx_launch_open_app_decrement_v2_exp,wx_launch_open_app_decrement_origin,recommend_comment_hide_exp1,recommend_comment_hide_v2_exp3,recommend_comment_hide_v3_origin,supervision_exp,supervision_v2_exp,commentshow_exp1,gif_clt1,ques_clt1; timestamp2=16620196533002ff0da1d75ae224714068fcceba8ecb2f88104951ffca8282a; timestamp2.sig=z0oHP1i6NwsqYEbpEX8hdiNZ1ZO3KDNftPQWyYpeTVA; a1=182f8175457tyi0kj8f3d0tai4hc69d3ei4pdknwv00000394972; smidV2=2022090116073428918fa465d9e938198f428173dc78bb0098f68c04282a7d0; gid=yYJiYyW228dyyYJiYyW243TI2W9v38TVYiqf4Eh89034xU88SKjfqf888qj4jWJ8yWdd2qij; gid.sig=5BAW0ss6BuJHVGl3S9u-hlg69JL6EyV3wHZrTgkJ6cE; gid.sign=2SC06YbMeFwRAs+OgHc+iOMRCq4=; gid.sign.sig=vG57iPUxhDGj5F1gU4CPXDSuFE6biZWoPErIFM05SfA', 'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'same-origin', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}


def get_detail(ni):
    s = requests.session()
    try:
        resp = s.get(f'https://www.xiaohongshu.com/discovery/item/{ni}', headers=headers, timeout=10)
        item = {}
        sel = Selector(resp.text)
        content = [ i.replace('-', '').replace('..', '').replace('...', '').replace('_.', '').\
                        replace('_', '').replace('#', '').strip()
            for i in sel.xpath("//main/div[@class='content']//text()").getall() if i]

        item['id'] = ni
        item['detail_content'] = ''.join(content)
        print(content)
        li.append(item)
    except Exception as e:
        print(e)
        li.append('')
        save_json(ni + '\n')


def save_json(nid):
    with open('notes.json', 'w',encoding='utf-8') as f:
        f.write(json.dumps(nid,ensure_ascii=False))

if __name__ == '__main__':
    li = []
    for i in ['5f25463f0000000001002ec0',
            '61220cb60000000001029e8c',
            '5ed5e60e0000000001002964',
            '5e8298e30000000001005293',
            '5c9f45a2000000000f027130'][:]:
        time.sleep(5)
        get_detail(i)

    save_json(li)