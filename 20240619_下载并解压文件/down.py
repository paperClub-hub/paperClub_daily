#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2024-06-19 14:19
# @Author   : NING MEI

import os
import sys
import tarfile
import requests
from tqdm import tqdm


def download_with_progressbar(url, save_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        total_size_in_bytes = int(response.headers.get('content-length', 1))
        block_size = 1024  # 1 Kibibyte
        progress_bar = tqdm(
            total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open(save_path, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
    else:
        logger.error("Something went wrong while downloading models")
        sys.exit(0)


def maybe_download(model_storage_directory, url):
    # using custom model
    tar_file_name_list = ['.pdiparams', '.pdiparams.info', '.pdmodel']

    assert url.endswith('.tar'), 'Only supports tar compressed package'
    tmp_path = os.path.join(model_storage_directory, url.split('/')[-1])
    print('download {} to {}'.format(url, tmp_path))
    os.makedirs(model_storage_directory, exist_ok=True)
    download_with_progressbar(url, tmp_path)
    with tarfile.open(tmp_path, 'r') as tarObj:
        for member in tarObj.getmembers():
            filename = None
            for tar_file_name in tar_file_name_list:
                if member.name.endswith(tar_file_name):
                    filename = 'inference' + tar_file_name
            if filename is None:
                continue
            file = tarObj.extractfile(member)
            with open(os.path.join(model_storage_directory, filename),'wb') as f:
                f.write(file.read())
    # os.remove(tmp_path)


if __name__ == '__main__':
    url = 'https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_det_infer.tar'

    save_path = "./"
    maybe_download(save_path, url)