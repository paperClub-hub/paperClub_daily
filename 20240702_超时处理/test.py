#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte: Pycharm
# @Date    : 2024/6/28 0028 13:17
# @Author  : Administrator
# @Desc    :


import os
import time
import threading


def time_out(interval, callback=None):
    """ 超时监控装饰器 """
    def decorator(func):
        def wrapper(*args, **kwargs):
            t =threading.Thread(target=func, args=args, kwargs=kwargs)
            t.setDaemon(True)  # 设置主线程技术子线程立刻结束
            t.start()
            t.join(interval)  # 主线程阻塞等待interval秒
            if t.is_alive() and callback:
                return threading.Timer(0, callback).start()  # 立即执行回调函数
            else:
                return
        return wrapper
    return decorator

def callback_func():
    """超时回调函数, 添加处理逻辑"""
    print('相应超时')

@time_out(2, callback_func)
def task(hh):
    print('**********测试****************')
    for i in range(3):
        time.sleep(1) # 休眠1秒
        print(f"i={i}, {hh}")

if __name__ == '__main__':
    task("paperclub")