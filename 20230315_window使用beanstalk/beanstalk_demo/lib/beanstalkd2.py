#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-03-15 18:01
# @Author   : NING MEI
# @Desc     :



import re
import time

import greenstalk
import asyncio
import traceback
import collections
from ujson import dumps, loads


_client = None
_loop = asyncio.get_event_loop()

TIMESTAMP_RE = re.compile(r"^[\d]{19,}/(\S+)")


class Beanstalkd:
    """ 消息队列服务端（Beanstalkd）
    """
    _connected = False

    def __init__(self, address: greenstalk.Address):
        self.connect(address)

    def connect(self, address: greenstalk.Address):
        if not self._connected:
            global _client
            _client = greenstalk.Client(address)

    def close(self):
        if self.is_connected():
            _client.close()

    def is_connected(self):
        return self._connected

    def _handle(self, tube: str, handler: callable):
        _client.watch(tube)
        if tube != "default":
            _client.ignore("default")
        job = _client.reserve(None)
        if not job:
            return None

        try:
            body_str = str(job.body)
            # print(body_str)
            bs = TIMESTAMP_RE.match(body_str)
            if bs:
                args = []
                kwargs = loads(body_str[20:])
            else:
                args, kwargs = loads(job.body)
            print("开始处理队列任务，参数：", args, kwargs)
            # logger.info(f"开始处理队列任务，参数：{args} {kwargs}")
            result = handler(*args, **kwargs)
            _client.delete(job)
            return result
        except Exception as e:
            traceback.print_exc()
        return None

    async def _async_handle(slef, tube: str, handler: callable):
        _client.watch(tube)
        if tube != "default":
            _client.ignore("default")
        job = _client.reserve(None)
        if not job:
            return None

        try:
            body_str = str(job.body)
            # print(body_str)
            bs = TIMESTAMP_RE.match(body_str)
            if bs:
                args = []
                kwargs = loads(body_str[20:])
            else:
                args, kwargs = loads(job.body)
            # print("开始处理队列任务，参数：", args, kwargs)
            # logger.info(f"开始处理队列任务，参数：{args} {kwargs}")
            result = await handler(*args, **kwargs)
            _client.delete(job)
            return result
        except Exception as e:
            traceback.print_exc()
        return None

    def watch(self, tube: str, handler: callable):
        # print(f"正在监听任务队列，Tube={tube}")
        # logger.info(f"正在监听任务队列，Tube={tube}")
        return self._handle(tube, handler)

    async def async_watch(self, tube: str, handler: callable):
        # print(f"正在监听任务队列，Tube={tube}")
        # logger.info(f"正在监听任务队列，Tube={tube}")
        return await self._async_handle(tube, handler)

    def put(self, tube: str, priority: int = greenstalk.DEFAULT_PRIORITY,
            delay: int = greenstalk.DEFAULT_DELAY, ttr: int = greenstalk.DEFAULT_TTR,
            *, args=[], kwargs={}):
        _client.use(tube)
        body = dumps((args, kwargs))
        return _client.put(body, priority, delay, ttr)

    def put_go(self, tube: str, priority: int = greenstalk.DEFAULT_PRIORITY,
               delay: int = greenstalk.DEFAULT_DELAY, ttr: int = greenstalk.DEFAULT_TTR,
               *, body=""):
        if not body:
            return
        body = f"{time.time_ns()}/{body}"
        _client.use(tube)
        return _client.put(body, priority, delay, ttr)
