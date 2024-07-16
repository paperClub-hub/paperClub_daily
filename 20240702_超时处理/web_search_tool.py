#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte: Pycharm
# @Date    : 2024/6/28 0028 13:17
# @Author  : Administrator
# @Desc    :

""" 联网搜索，方法基于duckduckgo_search，获取的是DuckDuckGo的搜索结果，
需要外网VPN，底层方法是使用pyreqwest_impersonate做模拟浏览器请求，并对结果进行解析

"""

import os
import re
import time
import sys
import logging
from datetime import datetime
from os.path import exists,join
from multiprocessing import Process, Queue
# 防止: daemonic processes are not allowed to have children
# from billiard import Process, Queue
from typing import Dict, List, Optional, Callable
from langchain_core.pydantic_v1 import BaseModel, Extra, root_validator
from langchain.docstore.document import Document
from langchain.tools import  StructuredTool
from langchain.pydantic_v1 import BaseModel, Field
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_community.document_transformers import Html2TextTransformer
from concurrent_log_handler import ConcurrentRotatingFileHandler

global PROXY
PROXY = "http://192.168.110.221:7890"
# PROXY = "http://192.168.31.211:7890"
# PROXY = "http://127.0.0.1:7890"

# 修改：langchain_community.document_loaders import AsyncHtmlLoader
class DuckDuckGoSearchAPIWrapper(BaseModel):
    """Wrapper for DuckDuckGo Search API.
    Free and does not require any setup.
    """
    region: Optional[str] = "wt-wt"
    """
    See https://pypi.org/project/duckduckgo-search/#regions
    """
    safesearch: str = "moderate"
    """
    Options: strict, moderate, off
    """
    time: Optional[str] = "y"
    """
    Options: d, w, m, y
    """
    max_results: int = 5
    backend: str = "api"
    """
    Options: api, html, lite
    """
    source: str = "text"
    """
    Options: text, news
    """
    global PROXY
    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that python package exists in environment."""
        try:
            from duckduckgo_search import DDGS  # noqa: F401
        except ImportError:
            raise ImportError(
                "Could not import duckduckgo-search python package. "
                "Please install it with `pip install -U duckduckgo-search`."
            )
        return values

    def _ddgs_text(
        self, query: str, max_results: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Run query through DuckDuckGo text search and return results."""
        from duckduckgo_search import DDGS

        with DDGS(proxy=PROXY, timeout=2) as ddgs:
            ddgs_gen = ddgs.text(
                query,
                region=self.region,
                safesearch=self.safesearch,
                timelimit=self.time,
                max_results=max_results or self.max_results,
                backend=self.backend,
            )
            if ddgs_gen:
                return [r for r in ddgs_gen]
        return []

    def _ddgs_news(
        self, query: str, max_results: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Run query through DuckDuckGo news search and return results."""
        from duckduckgo_search import DDGS
        with DDGS(proxy=PROXY, timeout=2) as ddgs:
            ddgs_gen = ddgs.news(
                query,
                region=self.region,
                safesearch=self.safesearch,
                timelimit=self.time,
                max_results=max_results or self.max_results,
            )
            if ddgs_gen:
                return [r for r in ddgs_gen]
        return []

    def _ddgs_img(self, query: str, max_results: Optional[int])->List[Dict[str, str]]:
        from duckduckgo_search import DDGS
        with DDGS(proxy=PROXY, timeout=2) as ddgs:
            results = ddgs.images(
                keywords=query,
                region="wt-wt",
                safesearch="off",
                size=None,
                color="Monochrome",
                type_image=None,
                layout=None,
                license_image=None,
                max_results=max_results,
            )
            return results

    def _ddgs_videos(self, query: str, max_results: Optional[int])->List[Dict[str, str]]:
        from duckduckgo_search import DDGS
        with DDGS(proxy=PROXY, timeout=2) as ddgs:
            results = ddgs.videos(
                keywords=query,
                region="wt-wt",
                safesearch="off",
                timelimit="w",
                resolution="high",
                duration="medium",
                max_results=max_results,
            )
            return results


    def run(self, query: str) -> str:
        """Run query through DuckDuckGo and return concatenated results."""
        if self.source == "text":
            results = self._ddgs_text(query)
        elif self.source == "news":
            results = self._ddgs_news(query)
        else:
            results = []

        if not results:
            return "No good DuckDuckGo Search Result was found"
        return " ".join(r["body"] for r in results)

    def results(
        self, query: str, max_results: int, source: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Run query through DuckDuckGo and return metadata.

        Args:
            query: The query to search for.
            max_results: The number of results to return.
            source: The source to look from.

        Returns:
            A list of dictionaries with the following keys:
                snippet - The description of the result.
                title - The title of the result.
                link - The link to the result.
        """
        source = source or self.source
        if source == "text":
            results = [
                {"snippet": r["body"], "title": r["title"], "link": r["href"]}
                for r in self._ddgs_text(query, max_results=max_results)
            ]
        elif source == "news":
            results = [
                {
                    "snippet": r["body"],
                    "title": r["title"],
                    "link": r["url"],
                    "date": r["date"],
                    "source": r["source"],
                }
                for r in self._ddgs_news(query, max_results=max_results)
            ]
        elif source == "image":
            results = [
                {
                    "snippet": r["image"],
                    "title": r["title"],
                    "link": r["url"],
                    "date": '',
                    "source": r["source"],
                }
                for r in self._ddgs_img(query, max_results=max_results)
            ]

            return results

        elif source == "video":
            results = [
                {
                    "snippet": r["description"],
                    "title": r["title"],
                    "link": r["content"],
                    "date": r["published"],
                    "source": r["publisher"],
                }
                for r in self._ddgs_videos(query, max_results=max_results)
            ]
            return results
        else:
            results = []

        if results is None:
            results = [{"Result": "No good DuckDuckGo Search Result was found"}]

        return results

api_wrapper = DuckDuckGoSearchAPIWrapper(time = None, max_results = 3, backend = "lite")
html2text = Html2TextTransformer()


# ----------------------------- 日志模块
debuge_log_folder = './logs/debug_logs'
if not exists(debuge_log_folder):
    os.makedirs(debuge_log_folder)

save_docs_dir = join(debuge_log_folder, "tmp_webdocs")
if not exists(save_docs_dir):
    os.makedirs(save_docs_dir)

web_search_debug = logging.getLogger('web_search_debug')
web_search_debug.setLevel(logging.INFO)
debug_handler = ConcurrentRotatingFileHandler(join(debuge_log_folder, "web_search_debug.log"), "a", 16 * 1024 * 1024, 5)
formatter = logging.Formatter(f"%(asctime)s - [PID: %(process)d][MainProcess] - [Function: %(funcName)s] - %(levelname)s - %(message)s")
process_type = 'MainProcess' # if 'SANIC_WORKER_NAME' not in os.environ else os.environ['SANIC_WORKER_NAME']
# 创建一个带有自定义字段的格式器
formatter = logging.Formatter(f"%(asctime)s - [PID: %(process)d][{process_type}] - [Function: %(funcName)s] - %(levelname)s - %(message)s")
debug_handler.setFormatter(formatter)
web_search_debug.addHandler(debug_handler)


class WebSearchInput(BaseModel):
    query: str = Field(..., description=f"search query")

def clean(text:str):
    text = re.sub(r'\s+', ' ', text).strip()
    # text = text.replace("\n", '')
    return text

def segment(doc):
    para = re.sub('([。！？\?])([^”’])', r"\1\n\2", doc)
    para = re.sub('([\.;])(\s)', r"\1\n\2", para)  # 英文断句
    para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
    para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
    para = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
    para = para.rstrip()
    return para.split("\n")

def deduplicate_documents(doc):
    paras = segment(doc)
    unique_docs = []
    for p in paras:
        p = clean(p)
        if p and p not in unique_docs:
            unique_docs.append(p)
    return "".join(unique_docs)

def duckduckgo_search(query: str, top_k:int=2, is_parser:bool=False, timeout=3):
    """ 改写搜索结果 """
    doc_score = 0.7
    def search_by_wrapper(query, topk=3):
        urls, result_docs = [], []
        res_wrapper = api_wrapper.results(query, max_results=topk)
        for item in res_wrapper:
            urls.append(item['link'])
            text = item.get('snippet')
            text =  item.get('title') + "。\n" + text #text if text.strip() else item.get('title')
            source = item.get('link')
            if text.strip():
                doc = Document(page_content=text, metadata={"source": source, "file_name": source, "file_id": source,
                                                            "kernel": source, "retrieval_query": query,
                                                            "embed_version": "联网搜索", "score": doc_score })
                result_docs.append(doc)
        return urls, result_docs

    def get_by_asynchtmlloader(result_queue, urls):
        print("任务启动...")
        web_search_debug.info("任务启动...")
        loader = AsyncHtmlLoader(urls)
        docs = loader.load()
        for doc in docs:
            doc.metadata['score'] = doc_score
            doc.metadata["file_name"] = doc.metadata.get("source", '')
            doc.metadata['file_id'] = doc.metadata["file_name"]
            doc.metadata['kernel'] = doc.metadata["file_name"]
            doc.metadata['retrieval_query'] = query
            doc.metadata['embed_version'] = '联网搜索'
            if doc.page_content == '':
                doc.page_content = doc.metadata.get('description', '')
        result = html2text.transform_documents(docs)
        result_queue.put(result)

    def search_by_asynchtmlloader(function:Callable, timeout, *args):
        """限时搜索，防止解析超时"""
        result_queue = Queue()
        p = Process(target=function, args=(result_queue, *args))
        p.start()
        p.join(timeout)
        if p.is_alive():
            print(f"{datetime.now()}: 执行超时({timeout}s), 正在终止...")
            web_search_debug.info(f"{datetime.now()}: 执行超时({timeout}s), 正在终止...")
            p.terminate()
            p.join()
            result = []
        else:
            print("执行完成。")
            web_search_debug.info("执行完成。")
            result = result_queue.get()
        return result

    def time_limit_search(query: str, topk=3, is_parser=False, timeout=3):
        """"""
        urls, result_docs = search_by_wrapper(query, topk=topk)
        print(f"基础搜索，urls: {urls}, docs: {len(result_docs)}")
        web_search_debug.info(f"基础搜索，urls: {urls}, docs: {result_docs}")
        # 限时搜索
        parsed_docs = []
        if is_parser:
            print("准备联网搜索...")
            web_search_debug.info("准备联网搜索...")
            parsed_docs = search_by_asynchtmlloader(get_by_asynchtmlloader, timeout, urls)
        print(f"is_parser: {is_parser}， parsed_docs: {len(parsed_docs)}")
        web_search_debug.info(f"is_parser: {is_parser}， parsed_docs: {parsed_docs}")

        return result_docs, parsed_docs

    # 获取限时搜索结果
    docs, detail_docs = time_limit_search(query, top_k, is_parser, timeout)
    web_search_debug.info(f"联网搜索docs： {docs}")
    web_search_debug.info(f"联网搜索detail_docs： {detail_docs}")
    if not detail_docs:
        detail_docs = docs

    for i, doc in enumerate(detail_docs):
        print("----------------------->>>>> ", doc)
        doc.page_content = deduplicate_documents(doc.page_content)

    web_search_debug.info(f"联网搜索完成，最终结果detail_docs: {detail_docs}")
    return docs, detail_docs



# web_search_tool = StructuredTool.from_function(
#     func=duckduckgo_search,
#     name="duckduckgo_search",
#     description="Search infomation on internet. Useful for when the context can not answer the question. Input should be a search query.",
#     args_schema=WebSearchInput,
#     return_direct=True,
#     # coroutine= ... <- you can specify an async method if desired as well
# )
#
# # tools = [web_search_tool]
# # functions = [convert_to_openai_function(t) for t in tools]
# # print(f"functions:{functions}",flush=True)
# #
# # search_tools = []
# # college_tool = {"type":"function", "function": functions[0]}
# # search_tools.append(college_tool)


if __name__ == '__main__':
    t1 = time.time()
    query = "985大学有哪些?"
    # query = "今天是什么天气？"
    # query = "2024年高考录取分数线"
    query = "985大学有哪些"
    query = "韦小宝是哪人？"
    query = "韦小宝是哪人？"
    query = "高考成绩"
    docs, results = duckduckgo_search(query, is_parser=False)
    print("detail_docs: ", results)
    # t2 = time.time()

    # print("耗时：", t2 - t1)
