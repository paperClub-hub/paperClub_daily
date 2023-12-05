#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-10-30 14:52
# @Author   : NING MEI
# @Desc     :


import os
import sys
import time
import subprocess
from sklearn.svm import SVC
from sklearn.datasets import load_iris
from sklearn.model_selection import GridSearchCV



def grid_search(experiment_id_list, gpu_list, task_command='run_expid.py'):
    """ """
    gpu_list = list(gpu_list)
    idle_queue = list(range(len(gpu_list)))
    processes = dict()

    while len(experiment_id_list) > 0:
        # 多显卡执行
        if len(idle_queue) > 0:
            # 删除第一项
            idle_idx = idle_queue.pop(0)
            gpu_id = gpu_list[idle_idx]
            expid = experiment_id_list.pop(0)
            config = "test_config"
            cmd = "python -u {} --config {} --expid {} --gpu {}".format(task_command, config, expid, gpu_id)
            p = subprocess.Popen(cmd.split())
            processes[idle_idx] = p

        else:
            print("检查进程：")
            time.sleep(3)
            for idle_idx, p in processes.items():
                # 检查子进程是否已终止
                print(f"检查子进程，pid: {p.pid}, 状态：{p.returncode}, 是否结束：{p.poll()}, 报错：{p.stderr} ")
                if p.poll() is not None:  # 释放显卡
                    idle_queue.append(idle_idx)

    # 等待子进程结束
    returncodes = [p.wait() for p in processes.values()]
    print("returncodes: ", returncodes)


def grid_search_by_sklearn():
    """ """
    # 加载数据集
    iris = load_iris()

    param_grid = {
        'C': [0.1, 1, 10],
        'gamma': [0.01, 0.1, 1],
    }

    svm = SVC()
    # 创建 GridSearchCV 对象，禁用交叉验证
    grid_search = GridSearchCV(svm, param_grid, cv=None)
    # 在数据集上拟合 GridSearchCV 模型
    grid_search.fit(iris.data, iris.target)

    # 输出最佳超参数配置
    print("Best parameters: ", grid_search.best_params_)

if __name__ == '__main__':

    gpu_list = [-1]
    # experiment_id_list = ['base', 'opti_1']
    # grid_search(experiment_id_list, gpu_list, task_command='testme.py')
    grid_search_by_sklearn()