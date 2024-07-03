#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte: Pycharm
# @Date    : 2024/6/28 0028 13:17
# @Author  : Administrator
# @Desc    :


import os
import time
import threading
import subprocess
from typing import Callable
from multiprocessing import Process, Queue


# --------------------- 基于装饰器的处理方法，只能提示、无法获取返回值
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
def run_task1(hh):
    print('**********测试****************')
    for i in range(3):
        time.sleep(1) # 休眠1秒
        print(f"i={i}, {hh}")



# --------------------- 基于Queue的方法
def sub_function(result_queue, duration):
    """模拟耗时任务，duration秒后完成"""
    time.sleep(duration)  # 模拟计算或IO等待
    res = "sub_function运行结果为xxx" # 执行某个方法，结果加入队列

    # """例如如下方法"""
    # from langchain_community.document_loaders import AsyncHtmlLoader
    # urls = ['https://baike.baidu.com/item/韦小宝/1448539',
    #         'https://zh.wikipedia.org/zh-sg/韋小寶',
    #         'https://www.sohu.com/a/215419865_648199']
    # loader = AsyncHtmlLoader(urls)
    # res = loader.load()

    result_queue.put(('Done', res))


def run_task2(function:Callable, args, timeout):
    """运行函数，并在超时后忽略结果"""
    result_queue = Queue() # 创建一个Queue对象用于进程间通信
    # 创建一个进程来执行传入的函数，将Queue和其他*args、**kwargs作为参数传递
    p = Process(target=function, args=(result_queue, *args))
    p.start()

    p.join(timeout)  # 等待线程完成或超时
    if p.is_alive(): # 判断进程状态
        print(f"{str(function)}: 运行超时了!")
        p.terminate()  # 超时终止进程，
        p.join()  # 确保进程已经终止，超时情况下，我们没有结果
        return ('Error', ["执行超时"])
    else:
        print("完成。")
        return result_queue.get()



# 对上面方法进行改进
from multiprocessing import Process, Queue
from datetime import datetime

def get_wrapper(q, urls):
    loader = AsyncHtmlLoader(urls)
    docs = loader.load()
    for doc in docs:
        if doc.page_content == '':
            doc.page_content = doc.metadata.get('description', '')
    result = html2text.transform_documents(docs)
    q.put(result)  # 将结果放入队列

def run_with_timeout(func, timeout, *args):
    q = Queue()  # 创建一个Queue对象用于进程间通信
    # 创建一个进程来执行传入的函数，将Queue和其他*args、**kwargs作为参数传递
    p = Process(target=func, args=(q, *args))
    p.start()
    p.join(timeout) # 等待进程完成或超时
    if p.is_alive():
        print(f"{datetime.now()} {str(func)}执行已超时({timeout}s)，正在终止进程...")
        p.terminate()  # 超时终止进程，
        p.join()  # 确保进程已经终止，超时情况下，我们没有结果
        result = []
    else:
        print(f"{datetime.now()} {str(func)}执行成功完成")
        result = q.get()  # 从队列中获取结果
    return result


t1 = time.time()
timeout = 10
docs = run_with_timeout(get_wrapper, timeout, urls)
t2 = time.time()
print("耗时：", t2 - t1)
print("dccs: ", docs)


# --------------------- 基于subprocess, 适用调用外部方法

def run_task3(command, timeout):
    # 创建子进程并执行命令
    process = subprocess.Popen(command, shell=True)
    # 等待命令执行完成或超时
    start_time = time.time()
    while process.poll() is None:
        time.sleep(0.1)
        if time.time() - start_time > timeout:
            # 超时终止命令
            process.terminate()
            return "Command timed out"

    # 获取命令执行结果
    return process.returncode




if __name__ == '__main__':
    t = "paperclub"
    # res = run_task1(t) # <class 'NoneType'> None
    timeout = 3  # 设置超时时间为3秒
    duration = 4  # 子函数运行超过3秒则提示超时
    res = run_task2(sub_function, (duration,), timeout)
    print("res: ", type(res), res)

    # # 示例调用
    # cmd = ['python', 'xxx.py']
    # timeout = 3  # 超时时间为3秒
    # result = run_task3(cmd, timeout)
    # print(result)
