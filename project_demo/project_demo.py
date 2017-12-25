# coding=utf8

__author__ = 'wangjiawei'
"""
作为项目的demo
主要是为了梳理流程
"""

import config

class DemoEngine(object):
    """
    这个是引擎，作为负责总体逻辑的存在
    1. 通过发起请求，拿到response后
    2. 交给spider去解析，拿到data_list后
    3. 交给pipeline去做持久化
    4. 分离原则，降低耦合
    5. spider，downloader 是不具备思维的
    6. pipeline实际上是一个开关
    """

    def __init__(self):
        self.down = DemoDownloader()
        self.spider = DemoSpider()
        self.pipe = DemoPipeline()

    def demo_execute(self):
        """
        这里相当于模块的调度模块
        之所以把逻辑模块和调度模块分开
        仍然是为了满足分离原则，体现灵活性
        在这里可以把 列表，信息，评论整合到一起
        再相应调度相应的逻辑部分
        """
        start_urls = []
        for url in start_urls:
            self.demo_execute_logic(url)

    def demo_execute_logic(self, url):
        """
        该模块的执行逻辑部分
        * 仍旧是强调分离原则
        * 逻辑模块就是一套流程
        * 判断流程就自行添加
        """
        # response, data_list 都是来自配置文件
        response = setting.response
        data_list = setting.data_list
        # 发起请求
        response = self.down.do_requests(url)
        # 数据解析
        data_list = self.spider.do_parse(response)
        # 持久化
        self.pipe.save_data(data_list)

class DemoDownloader(object):


    def do_requests(self):
        pass


class DemoSpider(object):

    def do_parse(self, html):
        pass


class DemoPipeline(object):

    def save_data(self, data_list):
        pass


class setting:
    """
    配置文件，作为从config.py里讲该脚本需要的参数提取并封装到setting这个类里
    使用过程中也要考虑数据结构的问题
    """
    response = config.RESPONSE
    data_list = config.DATA_LIST


if __name__ == '__main__':
    de = DemoEngine()
    de.demo_execute()