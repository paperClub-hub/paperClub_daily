#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @ Date: 2022-07-15 15:26
# @ Author: NING MEI


"""" 多维特征可视化 """

import os
import json
import glob
from typing import Dict
from collections import defaultdict



def load_configs(configs: list):
    root_dir = os.getcwd()

    all_dict = defaultdict(list)

    for cf in configs:
        cf_dict = json.load(open(cf, 'r'))
        info = cf_dict.get("embeddings")[0]
        all_dict["embeddings"].append(info)

    all_dict["modelCheckpointPath"] = "feature_visual"
    save_json = os.path.join(root_dir, "configs.json")

    print(json.dumps(all_dict, indent=True), file=open(save_json, "w"))




config_list = ["sbert/configs.json", "space/configs.json", "pretrain/configs.json"]
load_configs(config_list)
port = 8000
os.system('python -m http.server %s' % port)
