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
from queue import Queue
from typing import Callable


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


def sub_function(result_queue, duration):
    """模拟耗时任务，duration秒后完成"""
    time.sleep(duration)  # 模拟计算或IO等待
    res = "sub_function运行结果为xxx"
    result_queue.put(('Done', res))

def run_task2(function:Callable, args, timeout):
    """运行函数，并在超时后忽略结果"""
    result_queue = Queue()
    thread = threading.Thread(target=function, args=(result_queue,) + args)
    thread.start()

    thread.join(timeout)  # 等待线程完成或超时
    if thread.is_alive():
        print(f"{function}: 运行超时了!")
        return ('Error', "执行超时")
    else:
        # 获取结果，但注意：如果函数在超时前未完成，这里可能等待它完成
        return result_queue.get()

        # 使用示例


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
    res = run_task1(t) # <class 'NoneType'> None
    # timeout = 3  # 设置超时时间为3秒
    # duration = 4  # 子函数运行超过3秒则提示超时
    # res = run_task2(sub_function, (duration,), timeout)
    print("res: ", type(res), res)

    # # 示例调用
    # cmd = ['python', 'xxx.py']
    # timeout = 3  # 超时时间为3秒
    # result = run_task3(cmd, timeout)
    # print(result)
