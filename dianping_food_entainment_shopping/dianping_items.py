# coding=utf8

__author__ = 'WangJiaWei'

"""
    记录：
        2017-12-13 开始按照规范修改脚本
"""

import re
import time
import json
import logging
import multiprocessing
import requests
from lxml import etree
from faker import Faker
import config

class DianPingItemsEngine(object):
    """作为大众点评"美食，购物，娱乐"的场所抓取脚本的引擎

    负责抓取逻辑

    Attributes:
        self.down 下载器的实例
        self.spider 解析器的实例
        self.pipe 管道的实例
    """

    def __init__(self) -> None:
        super().__init__()
        self.down = DianPingItemsDownloader()
        self.spider = DianPingItemsSpider()
        self.pipe = DianPingItemsPipeline()

    def get_catgory(self):
        """"该模块作为迭代每个市，获取目录分类"""
        # self.pipe.do_clear_category()
        city_list = setting.city_list[setting.provs]
        category_list = setting.category_list
        category_list['data'] = [self.get_category_logic(i.strip().split(setting.blank)) for i in city_list]
        self.pipe.save_category_list(category_list['data'])
        # 清理
        category_list['data'].clear()

    def get_category_logic(self, city):
        response = setting.requests_result
        response = self.down.get_category(response, city[-3])
        data = []
        if response['response'] is not 'bad_requests':
            data = self.spider.get_category(response['response'])
        # 清理内存
        response['response'] = ''
        response['url'] = ''
        response['params'] = ''
        response['status_code'] = ''
        response['error'] = ''
        return data

    def shop_list(self):
        """作为获取餐厅列表的模块

        我打算一次性把url都生成然后去抓取列表
        这里要做一个增量列表更新
        每一次都要迭代一次列表
        """

        f = open(setting.shop_list_file[setting.choice], 'w+')
        f.close()

        start_urls_infos = self.construct_url()
        pool = multiprocessing.Pool(1)
        for info in start_urls_infos:
            # self.shop_list_logic(info)
            # break
            pool.apply_async(self.shop_list_logic, (info, ))
        pool.close()
        pool.join()

    def shop_list_logic(self, info):
        page = 50
        while page > 0:
            response = setting.requests_result
            shop_list = setting.shop_list
            url = info[0] + str(51 - page)
            response = self.down.get_restaurant(url, response)
            if response['response'] is not 'bad_requests':
                shop_list['data'] = self.spider.shop_list(response['response'])
                self.pipe.save_shop_list(shop_list['data'], info) if not shop_list['data'] == [] else ''
            if shop_list['data'] == []:
                break
            page -= 1
            # 清理内存
            response['response'] = ''
            response['url'] = ''
            response['params'] = ''
            response['status_code'] = ''
            response['error'] = ''
            shop_list['data'].clear()

    def construct_url(self):
        """构造请求用的url"""
        urls = []
        url = setting.url_shop_list
        area = setting.city_list[setting.provs]
        cate_file = setting.category_file[setting.choice]

        for city in area:
            for category in open(cate_file, 'r', encoding=setting.encode):
                info = city.strip().split(setting.blank)
                cate = category.strip().split(setting.blank)
                urls.append([url % (info[-3], setting.types[setting.choice], cate[1], info[-2]), cate[0], info])
        return urls

    def shop_info(self):
        """"这里要做的是，完成每个商铺的详细信息获取

        也是要做一个清洗，做一个增量更新
        """
        shop_list = (i.strip().split(setting.blank)
                     for i in open(setting.shop_list_file[setting.choice], 'r', encoding=setting.encode))
        # shop_info_already = self.pipe.get_shop_list_set()
        # pool = multiprocessing.Pool(1)
        for each in shop_list:
            # if each[0] not in shop_list_already:
                print(each)
                self.shop_info_logic(each)
                break
                # pool.apply_async(self.get_info, (each,))
        # pool.close()
        # pool.join()

    def shop_info_logic(self, info):
        response = setting.requests_result
        shop_info = setting.shop_info
        response = self.down.shop_info(info[0], response)
        if response['response'] is not 'bad_requests':
            shop_info = self.spider.shop_info(response['response'], shop_info)
            self.pipe.save_shop_info(shop_info['data'], info, response['url']) if not shop_info['data'] == [] else ''
        # 清理内存
        response['response'] = ''
        response['url'] = ''
        response['params'] = ''
        response['status_code'] = ''
        response['error'] = ''
        shop_info['data'].clear()


class DianPingItemsDownloader(object):
    """作为下载器的存在

    """

    def __init__(self) -> None:
        super().__init__()
        self.session = requests.session()

    def do_get_requests(self, *args):
        retry = 30
        response = args[2]
        while retry > 0:
            try:
                args[1]['User-Agent'] = Faker().user_agent()
                if len(args) == 3:
                    res = self.session.get(args[0],
                                        headers=args[1],
                                        cookies=setting.cookies,
                                        proxies=setting.proxies,
                                        timeout=30)
                else:
                    res = self.session.get(args[0],
                                           headers=args[1],
                                           cookies=setting.cookies,
                                           params=args[3],
                                           proxies=setting.proxies,
                                           timeout=30
                                           )
                response['status_code'] = res.status_code
                response['url'] = res.url
                if repr(res.status_code).startswith('2'):
                    self.session.cookies.update(res.cookies)
                    response['response'] = res.content.decode(setting.encode)
                    break
                else:
                    # 但凡遇到403，如果是代理的问题则切换ip
                    args[1]['Proxy-Switch-Ip'] = 'yes'
                    continue
            except Exception as e:
                args[1]['Proxy-Switch-Ip'] = 'yes'
                response['error'] = e
            retry -= 1
        return response

    def get_category(self, response, city_id):
        url = setting.categroy_url % (city_id, setting.types[setting.choice])
        headers = setting.headers
        response = self.do_get_requests(url, headers, response)
        return response

    def get_restaurant(self, url, response):
        headers = setting.headers
        response = self.do_get_requests(url, headers, response)
        return response

    def shop_info(self, id, response):
        headers = setting.headers_xml
        url = setting.url_info
        params = setting.params
        params['shopId'] = id
        params['_nr_force'] = int(time.time() * 1000)
        response = self.do_get_requests(url, headers, response, params)
        return response

class DianPingItemsSpider(object):

    def get_category(self, html):
        selector = etree.HTML(html)
        parse = setting.cate_list_parse
        category_list = selector.xpath(parse['list'])
        data = []
        if category_list:
            for cate in category_list:
                id = cate.xpath(parse['id'])[0].split('/')[-1]
                type = cate.xpath(parse['type'])[0]
                data.append([type, id])
        return data

    def shop_list(self, html):
        selector = etree.HTML(html)
        data = []
        parse = setting.shop_list_parse
        shop_list = selector.xpath(parse['list'])
        if shop_list:
            for shop in shop_list:
                url = shop.xpath(parse['url'])[0] if shop.xpath(parse['url']) else '&'
                name = shop.xpath(parse['name'])[0] if shop.xpath(parse['name']) else '&'
                data.append([url, name])
        return data

    def shop_info(self, html, shop_info):
        data = shop_info['data']
        try:
            js_dict = json.loads(html)
        except Exception as e:
            js_dict = {}
            shop_info['error'] = e

        if js_dict.get('code', '') == 200:
            msg = js_dict.get('msg', {})
            shopInfo = msg.get('shopInfo', {})
            data.append(str(shopInfo.get('address', '')))   # 地址
            data.append(str(shopInfo.get('crossRoad', '')))  # 周边信息
            data.append(str(shopInfo.get('glat', '')) + ',' + str(shopInfo.get('glng', '')))  # 坐标
            data.append(str(shopInfo.get('businessHours', '')))   # 营业时间
            data.append(str(shopInfo.get('avgPrice', '')))     # 人均消费
            data.append(str(shopInfo.get('phoneNo', '')))  # 联系电话
            data.append(str(shopInfo.get('publicTransit', '')))  # 交通信息
            data.append(str(shopInfo.get('writeUp', '')))   # 简介
        return shop_info


class DianPingItemsPipeline(object):
    """作为管道的存在

    """
    def save_category_list(self, cate_list):
        cate = []
        for i in cate_list:
            for each in i:
                cate.append((each[0], each[1]))
        # 去重
        cate_set = set(cate)
        text = ''
        f = open(setting.category_file[setting.choice], 'w+', encoding=setting.encode)
        for i in cate_set:
            text += setting.blank.join([i[0], i[1]]) + '\n'
        f.write(text)
        f.close()

    def save_shop_list(self, data, info):
        content = ''
        for each in data:
            txt = [info[1], info[2][0], info[2][1], info[2][2], info[2][3], info[2][4], info[2][5], info[2][6], info[2][7]]
            text = setting.blank.join(txt)
            text = re.sub('\r|\n| ', '', text)
            if not each[0] is '&':
                shop_id = each[0].split('/')[-1]
                content += setting.blank.join([shop_id, each[1], text]) + '\n'
        with open(setting.shop_list_file[setting.choice], 'a', encoding=setting.encode) as f:
            f.write(content)

    def save_shop_info(self, data, info, url):
        shop = {}
        if setting.choice is 'entertainment':
            shop = setting.data_style[setting.choice]
            shop['中文全称'] = info[1]
            shop['所属地区'] = info[8]
            shop['地址'] = data[0]
            shop['地理位置'] = data[2]
            shop['类型'] = info[2]
            shop['营业时间'] = data[3]
            # shop['人均消费'] = data[4]
            shop['咨询电话'] = data[5]
            shop['交通信息'] = data[6]
            shop['周边信息'] = data[1]
            shop['简介'] = data[7]
            shop['国别'] = info[3]
            shop['省自治区全称'] = info[4]
            shop['省自治区简称'] = info[5]
            shop['市州全称'] = info[6]
            shop['市州简称'] = info[7]
            shop['区县全称'] = info[8]
            shop['区县简称'] = info[9]
            shop['地区编码'] = info[10]
            shop['url'] = url

        with open(setting.shop_info_file[setting.choice], 'a', encoding=setting.encode) as f:
            text = setting.blank.join([shop[i] for i in setting.data_style_l[setting.choice]])
            text = re.sub('\r|\n| |&| None', '', text) + '\n'
            f.write(text)
        # 保存这家店的ID
        with open(setting.shop_exists[setting.choice], 'a', encoding=setting.encode) as p:
            p.write(info[0] + '\n')

class setting(object):
    choice = config.CHOICE
    city_list = config.CITY_LIST
    provs = config.PROVS
    categroy_url = config.CATEGORY_URL
    cookies = config.COOKIES
    proxies = config.PROXIES
    blank = config.BLANK
    encode = config.ENCODEING
    requests_result = config.REQUESTS_RESULT
    types = config.TYPES
    headers = config.HEADERS
    headers_xml = config.HEADERS_XML
    category_list =config.CATEGORY_LIST
    cate_list_parse = config.CATEGORY_LIST_PARSE
    category_file = config.CATEGORY_FILE
    url_shop_list = config.SHOP_URL
    shop_list = config.SHOP_LIST
    shop_list_parse = config.SHOP_LIST_PARSE
    shop_list_file = config.SHOP_LIST_FILE
    url_info = config.INFO_URL
    params = config.PARAMS
    shop_info = config.SHOP_INFO
    data_style = config.DATA_STYLE
    data_style_l = config.DATA_STYLE_L
    shop_info_file = config.SHOP_INFO_FILE
    shop_exists = config.SHOP_ALREADY_EXISTS

class DianPingItemsSchedule(object):
    pass


if __name__ == '__main__':
    dpie = DianPingItemsEngine()
    # dpie.shop_list()
    dpie.shop_info()