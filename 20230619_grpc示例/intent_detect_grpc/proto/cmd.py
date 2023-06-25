#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-06-21 17:24
# @Author   : NING MEI
# @Desc     :


"""  生成 proto buf"""
import os

cmd = "python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./intent.proto"

os.system(cmd)