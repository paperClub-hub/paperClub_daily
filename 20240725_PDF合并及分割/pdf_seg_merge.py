#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @ Date    : 2024/7/18 6:31
# @ Author  : paperClub
# @ Email   : paperclub@163.com
# @ Site    :


""" pdf简单拆分及合并： 用于大文件翻译前后处理 """


import os
import time
import argparse
import subprocess
from tqdm import tqdm
from glob import glob
from os.path import exists, abspath, dirname, join


def install_package():
    lib = PyPDF2
    print(f"正在安装: {lib} ")
    try:
        cmd = f"pip install {lib} -i https://mirrors.aliyun.com/pypi/simple"
        exit_status = subprocess.run(cmd, shell=True).returncode
        time.sleep(5)
        if exit_status != 0:  # 检查命令是否成功执行
            print(f"{lib}: 安装失败")
            return False
        else:
            print(f"{lib}: 安装成功")
            return True
    except Exception as e:
        print(f"{lib}: 在安装时发生错误 {e}")
        return False

try:
    import PyPDF2
except:
    install_package()


import PyPDF2
class Pdf:
    def __init__(self):
        self.prefix = "part"
        self.output_folder = join(dirname(abspath(__file__)), "output_parts")
        self.pdf_savefile = f"merged_{int(time.time())}.pdf"

    def segment(self, pdf_path: str, num_pdffiles:int, output_folder:str=None):
        """pdf拆分"""

        if not output_folder:
            output_folder = self.output_folder

        if exists(pdf_path):
            t1 = time.time()
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
                pages_per_file = total_pages // num_pdffiles
                remaining_pages = total_pages % num_pdffiles
                # 确保输出文件夹存在
                if not exists(output_folder):
                    os.makedirs(output_folder)

                for i in tqdm(range(num_pdffiles)):
                    writer = PyPDF2.PdfWriter()
                    start_page = i * pages_per_file
                    end_page = start_page + pages_per_file
                    if i < remaining_pages:
                        end_page += 1

                    for page_num in range(start_page, end_page):
                        writer.add_page(reader.pages[page_num])

                    # 构造输出文件名
                    file_name = f'{self.prefix}_{i + 1}.pdf'
                    output_filename = join(output_folder, file_name)
                    with open(output_filename, 'wb') as out_file:
                        writer.write(out_file)
                        print(f"保存：{output_filename}")

                print(f"分割完成，耗时: {time.time() - t1}")
        else:
            print(f"文件不存在：{pdf_path}")


    def merge(self, pdf_savefile:str=None, output_folder:str=None):
        """
        将多个PDF文件合并为一个PDF文件。

        :param paths: 一个包含PDF文件路径的列表
        :param output: 合并后的PDF文件的输出路径
        """

        if not output_folder:
            output_folder = self.output_folder

        if not pdf_savefile:
            pdf_savefile = self.pdf_savefile

        pdf_writer = PyPDF2.PdfWriter()
        pdf_paths = glob(output_folder + "/*.pdf")
        print("pdf_paths: ", pdf_paths)
        assert len(pdf_paths) > 0, f"无pdf文件：{self.output_folder}"

        # 遍历每个PDF文件
        for i in tqdm(range(len(pdf_paths))):
            pdf_path = join(output_folder, f'{self.prefix}_{i + 1}.pdf')
            print(f"正在添加 {pdf_path} 到合并后的PDF...")
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    pdf_writer.add_page(page)

        # 写入合并后的PDF文件
        with open(pdf_savefile, 'wb') as out_file:
            pdf_writer.write(out_file)


def main():
    parser = argparse.ArgumentParser(description='PDF大文件分割和PDF子文件合成.')
    parser.add_argument('--pdf_path', '-p', type=str, help='Path to the PDF file to be split.')
    parser.add_argument('--num_pdffiles', '-n', type=int, default=10, help='Maximum number of pages per output file.')
    parser.add_argument('--output_folder',  '-o', type=str, default='output_parts', help='Directory to save the split PDF files.')
    parser.add_argument('--merge', '-m', action='store_true', help='启动合并.')
    parser.add_argument('--save_pdf', '-s', default=None, help='合并文件名')
    args = parser.parse_args()

    PDF = Pdf()
    if args.merge:
        PDF.merge(pdf_savefile=args.save_pdf, output_folder=args.output_folder)
    else:
        PDF.segment(pdf_path=args.pdf_path, num_pdffiles=args.num_pdffiles, output_folder=args.output_folder)

if __name__ == '__main__':
    """
    python pdf_seg_merge.py  -p "Diffusion Language Models Are Versatile Protein Learners.pdf"
    """
    main()