#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-03-15 15:23
# @Author   : NING MEI
# @Desc     :


import greenstalk


class BeanStalk:
    def __init__(self, address, encoding='utf-8', use='default', watch='default'):
        self.conn = greenstalk.Client(address=address, encoding=encoding, use=use, watch=watch)

    def producer(self, body, priority=65536, delay=0, ttr=60, tube='default'):
        """
        生产者
        :param body: job 类型为bytes或者str
        :param priority: 优先级 0-2^32 0优先级最大
        :param delay: 延迟
        :param ttr: time-to-run 超时重发
        :param tube: 使用哪个管道 默认default
        :return: job id
        """
        self.use(tube)
        return self.conn.put(body, priority, delay, ttr)

    def consumer(self, timeout=None):
        """
        消费者
        :param timeout: 一直处于阻塞状态 将等待多长时间来接收这个job。如果这个reserve的timeout时间到了，它将返回TimedOutError
        :return: Job类型
        """
        return self.conn.reserve(timeout)

    def use(self, tube='default'):
        """
        使用哪个管道
        :param tube: 管道名称 str
        :return: None
        """
        self.conn.use(tube)

    def delete(self, job):
        """
        删除一个job
        :param job: job或者jobId
        :return: None
        """
        self.conn.delete(job)

    def relase(self, job, priority=65536, delay=0):
        """
        将一个被消费的任务重新加入队列
        :param job: 任务
        :param priority: 优先级
        :param delay: 延迟
        :return: None
        """
        self.conn.release(job, priority, delay)

    def bury(self, job, priority=65536):
        """
        将job放到一个特殊的FIFO队列中，之后不能被reserve命令获取，但可以用kick命令扔回工作队列中，之后就能被消费了（相当于“逻辑删除”）
        :param job: 任务
        :param priority: 优先级
        :return: None
        """
        self.conn.bury(job, priority)

    def kick(self, bound):
        """
        :param bound: 最大kick的任务数
        :return: 返回受影响任务的数量
        """
        return self.conn.kick(bound)

    def kick_job(self, job):
        """
        把delayed 或者 buried 的任务加到ready队列
        :param job: job或者id
        :return: None
        """
        self.conn.kick_job(job)

    def touch(self, job):
        """
        让任务重新计算任务超时重发ttr时间,相当于给任务延长寿命
        :param job: 任务
        :return: None
        """
        self.conn.touch(job)

    def watch(self, tube):
        """
        watch一个管道，影响的是消费者操作 当监控多个tube时，只要有一个tube有数据到来，reserve会返回
        watch和use是两个独立的动作，use一个tube不代表watching它了，反之watch一个tube也不代表using它
        :param tube: 管道
        :return: 返回监听管道的数量
        """
        return self.conn.watch(tube)

    def ignore(self, tube):
        """
        取消对管道的监听
        :param tube: 管道
        :return: 返回监听管道的数量
        """
        return self.conn.ignore(tube)

    def peek(self, jobid):
        """
        查看job的信息
        :param jobid:
        :return: 返回job类型
        """
        return self.conn.peek(jobid)

    def peek_ready(self):
        """
        获取当前管道下一个处于ready状态的任务
        :return: Job
        """
        return self.conn.peek_ready()

    def peek_delayed(self):
        """
        获取当前管道下一个处于delay状态的任务
        :return: Job
        """
        return self.conn.peek_delayed()

    def peek_buried(self):
        """
        获取当前管道最早处于buried状态的任务
        :return: Job
        """
        return self.conn.peek_buried()

    def stats_job(self, job):
        """
        查看任务的状态 job有四种状态
        ready，需要立即处理的任务，当延时 (delayed) 任务到期后会自动成为当前任务；
        delayed，延迟执行的任务, 当消费者处理任务后，可以用将消息再次放回 delayed 队列延迟执行；
        reserved，已经被消费者获取, 正在执行的任务，Beanstalkd 负责检查任务是否在 TTR(time-to-run) 内完成；
        buried，保留的任务: 任务不会被执行，也不会消失，除非有人把它 "踢" 回队列；
        :param job: job id
        :return: dict
        """
        return self.conn.stats_job(job)

    def stats_tube(self, tube):
        """
        查看管道的状态
        :param tube: 管道名称
        :return: dict
        """
        return self.conn.stats_tube(tube)

    def stats(self):
        """
        返回系统的状态
        :return: dict
        """
        return self.conn.stats()

    def tubes(self):
        """
        返回所有的管道名称
        :return list
        """
        return self.conn.tubes()

    def using(self):
        """
        返回正在使用的管道名称
        :return: str 管道名称
        """
        return self.conn.using()

    def watching(self):
        """
        返回正在使用的管道名称
        :return: list 管道名称列表
        """
        return self.conn.watching()

    def pause_tube(self, tube, delay):
        """
        暂停一个管道，delay期间的job无法使用
        :param tube: str 管道名称
        :param delay: 延迟
        :return: None
        """
        self.conn.pause_tube(tube, delay)
