# coding=utf8

__author__ = 'WangJiaWei'
"""
日志：
    2017-12-11： 开始开发正式版

"""

import re
import time
import json
import logging
import requests
from faker import Faker
from lxml import etree
import config

class LinkIpEngine(object):
    """作为linkip的引擎模块

    一是 登录逻辑
    二是 抓取逻辑
    """

    def __init__(self):
        self.down = LinkIpDownloader()
        self.spider = LinkIpSpider()
        self.pipe = LinkIpPipeline()

    def login_system(self):
        """
        登录模块
        """
        # 获取第一个response，主要是拿到jessionid
        home_page = self.down.get_home_page()
        # 处理并获取jessionid
        setting.cookie_dict['Cookies'] = setting.cookies_text % home_page['cookies'].get('JSESSIONID')
        login = self.down.login()

    def get_news_types(self):
        """根据不同的分类，抓取不同的关键词的舆情新闻"""
        self.get_data()
        pass
    def get_data(self):
        """
        这是一个测试
        """
        page, num = 1, 1
        while num <= page:
            response = self.down.get_data(num)
            # 处理cookie，出现新的jessionid则顺势添加
            cookie = response['cookies'].get('JSESSIONID', 'none')
            if cookie is not 'none':
                setting.cookie_dict['Cookies'] = setting.cookies_text % response['cookies'].get('JSESSIONID')
            news_list = setting.news_list
            news_list = self.spider.news_list(response['response'], news_list)
            page = news_list['page']
            if not news_list['list'] == []:
                self.pipe.save_news_list(news_list['list'], '主题')
            #清理
            news_list['list'].clear()
            news_list['page'] = 1
            news_list['json_error'] = False
            num += 1
            break

    def get_info(self):
        """抓取每天舆情的快照
        """
        id_list = (i.strip() for i in open(setting.news_list_ids, 'r', encoding=setting.encode))
        for id in id_list:
            self.get_info_logic(id)
            break

    def get_info_logic(self, id):
        response = self.down.get_info(id)
        if response['response'] is not 'bad_request':
            info = setting.news_info_content
            info = self.spider.news_info_content(response['response'], info)
            self.pipe.save_news_info(id, info)

class LinkIpDownloader(object):
    """sessin 模块

    """
    session = requests.session()

    def GET_request(self, *args):
        ''' GET请求模块 '''
        retry = 10
        response = setting.request_result
        response['url'] = args[0]
        response['params'] = args[2] if (len(args) == 3) else ''
        while retry > 0:
            args[1]['User-Agent'] = Faker().user_agent()
            try:
                if len(args) == 2:
                    res = self.session.get(args[0], headers=args[1], proxies=setting.proxy, timeout=30)
                else:
                    res = self.session.get(args[0], headers=args[1], params=args[2], proxies=setting.proxy, timeout=30)
                # 这里暂时只对 2xx和4xx做处理
                response['status_code'] = res.status_code
                if repr(res.status_code).startswith('2'):
                    response['response'] = res.content.decode(setting.encode)
                    response['cookies'] = res.cookies
                    break
                elif repr(res.status_code).startswith('4'):
                    args[1]['Proxy-Switch-Ip'] = 'yes'
                    continue
                else:
                    # 其他情况，继续请求
                    #
                    # 继续完善后续情况
                    args[1]['Proxy-Switch-Ip'] = 'yes'
                    continue
            except Exception as e:
                response['error'] = e
            retry -= 1
        return response

    def POST_request(self, *args):
        ''' POST请求模块 '''
        retry = 10
        response = setting.request_result
        response['url'] = args[0]
        response['data'] = args[2] if (len(args) == 3) else ''
        while retry > 0:
            args[1]['User-Agent'] = Faker().user_agent()
            try:
                res = self.session.post(args[0], headers=args[1], data=args[2], cookies=setting.cookie_dict, proxies=setting.proxy, timeout=30)
                # 这里暂时只对 2xx和4xx做处理
                response['status_code'] = res.status_code
                if repr(res.status_code).startswith('2'):
                    response['response'] = res.content.decode(setting.encode)
                    response['cookies'] = res.cookies
                    break
                elif repr(res.status_code).startswith('4'):
                    args[1]['Proxy-Switch-Ip'] = 'yes'
                    continue
                else:
                    # 其他情况，继续请求
                    #
                    # 继续完善后续情况
                    args[1]['Proxy-Switch-Ip'] = 'yes'
                    continue
            except Exception as e:
                response['error'] = e
            retry -= 1
        return response

    def get_home_page(self):
        url = setting.url_home
        headers = setting.headers
        response = self.GET_request(url, headers)
        return response

    def login(self):
        url = setting.url_login
        headers = setting.headers
        data = setting.login_data
        response = self.POST_request(url, headers, data)
        return response

    def get_data(self, num):
        url = setting.url_data
        headers = setting.headers_xml
        data = setting.request_data
        data['currPage'] = num
        response = self.POST_request(url, headers, data)
        return response

    def get_info(self, id):
        url = setting.url_yq % id
        headers = setting.headers
        response = self.GET_request(url, headers)
        return response

class LinkIpSpider(object):
    """作为spider的存在
    """

    def news_list(self, html, news_list):
        js_dict = {}
        try:
            js_dict = json.loads(html)
        except Exception as e:
            news_list['error'] = e
        if not js_dict == {}:
            list_element = setting.list_elements
            news_list['page'] = js_dict.get('pageNum', 0)
            result_list = js_dict.get('result', [])
            for result in result_list:
                news_list['list'].append([str(result.get(i, ''))for i in list_element])
        return news_list

    def news_info_content(self, html, info):
        selector = etree.HTML(html)
        parse = setting.info_parse
        info['content'] = selector.xpath(parse['content'])[0].xpath('string(.)')
        info['source'] = selector.xpath(parse['source'])[0] if selector.xpath(parse['source']) else ''
        info['author'] = selector.xpath(parse['author'])[0] if selector.xpath(parse['author']) else ''
        info['time'] = selector.xpath(parse['time'])[0] if selector.xpath(parse['time']) else ''
        return info


class LinkIpPipeline(object):

    def save_news_list(self, news_list, type):
        """作为保存列表的存在

        同时保存一份 id 的列表用来避免重复录入
        :param news_list:
        """
        text = ''
        for news in news_list:
            news.append(type)
            text += setting.blank.join(news) + '\n'
        record_id = ''
        for id in news_list:
            record_id += id[0] + '\n'
        re.sub('\r|\n|', '', text)
        with open(setting.news_list_file, 'a', encoding=setting.encode) as f:
            f.write(text)
        with open(setting.news_list_history_file, 'a', encoding=setting.encode) as f:
            f.write(text)
        with open(setting.news_list_ids, 'a', encoding=setting.encode) as f:
            f.write(record_id)
        return

    def save_news_info(self, id, info):
        text = setting.blank.join([id, info['author'], info['time'], info['source'], info['content']])
        re.sub('\r|\n|', '', text)
        with open(setting.news_info, 'a', encoding=setting.encode) as f:
            f.write(text)

        with open(setting.news_info_history, 'a', encoding=setting.encode) as f:
            f.write(text)

class setting:
    encode = config.ENCODE
    blank = config.BLANK
    url_home = config.URL_HOME
    url_login = config.URL_LOGIN
    request_result = config.REQUESTS_RESULT
    proxy = config.PROXIES
    headers = config.HEADERS
    headers_xml = config.HEADERS_XML
    cookies_text = config.COOKIE_TEXT
    login_data = config.USER_INFO
    request_data = config.REQUEST_DATA
    url_data = config.URL_DATA
    cookie_dict = config.COOKIE_DICT
    news_list = config.NEWS_LIST
    list_elements = config.LIST_ELEMENTS
    news_list_file = config.NEWS_LIST_FILE
    news_list_history_file = config.NEWS_LIST_HISTORY_FILE
    news_list_ids = config.NEWS_LIST_IDS_FILE
    news_list_ids_history = config.NEWS_LIST_IDS_HISTORY_FILE
    news_info = config.NEWS_INFO_FILE
    news_info_history = config.NEWS_INFO_HISTORY_FILE
    url_yq = config.URL_YQ
    news_info_content = config.NEWS_INFO_CONTENT
    info_parse = config.INFO_PARSE

class LinkIpSchedule(object):
    pass

if __name__ == '__main__':
    lie = LinkIpEngine()
    lie.login_system()
    lie.get_info()