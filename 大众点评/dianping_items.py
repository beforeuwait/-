# coding=utf8

__author__ = 'WangJiaWei'

"""
    记录：
        2017-12-13 开始按照规范修改脚本
        2017-12-14 继续修改
        2017-12-15 修改bug
        2017-12-19 发现获取页面数据时候，有token
        2017-12-22 更新评论抓取的逻辑
        2017-12-28 迭代，实现动态加载配置文件
        2018-01-04 迭代，获取静态通用token，重写商铺基础数据部分
        2018-01-10 迭代，修改逻辑，将省份并发，该为先后顺序，同时分配高并发
        2018-01-29 正儿八经的开始迭代
                    1. 通过屏蔽cookies里关于client的字段达到突破，性能未测试
                    2. 暂时考虑请求cmt时候不要带cookies
"""

import re
import os
import time
import json
import datetime
import logging
import random
import multiprocessing
from imp import reload
import requests
from lxml import etree
from faker import Faker
try:
    from hdfs3 import HDFileSystem
except:
    pass
import config_area


class DianPingItemsEngine(object):
    """作为大众点评"美食，购物，娱乐"的场所抓取脚本的引擎

    负责抓取逻辑

    Attributes:
        self.down 下载器的实例
        self.spider 解析器的实例
        self.pipe 管道的实例
    """

    def __init__(self, setting):
        self.down = DianPingItemsDownloader(setting)
        self.spider = DianPingItemsSpider(setting)
        self.pipe = DianPingItemsPipeline(setting)
        self.s = setting

    def get_catgory(self):
        """"该模块作为迭代每个市，获取目录分类"""
        city_list = self.s['city_list'][self.s['provs']]
        category_list = self.s['category_list']
        category_list['data'] = [self.get_category_logic(i.strip().split(self.s['blank'])) for i in city_list]
        self.pipe.save_category_list(category_list['data'])
        # 清理
        category_list['data'].clear()
        return

    def get_category_logic(self, city):
        data = []
        response = self.s['requests_result']
        response = self.down.get_category(response, city[-3])
        self.recording_response(response)
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

        f = open(self.s['shop_list_file'][self.s['choice']], 'w+')
        f.close()
        start_urls_infos = self.construct_url()
        # 当前并发量不够，单进程跑数据
        pool = multiprocessing.Pool(4)
        for info in start_urls_infos:
            # self.shop_list_logic(info)
            pool.apply_async(self.shop_list_logic, (info, ))
        pool.close()
        pool.join()

    def shop_list_logic(self, info):
        page = 50
        while page > 0:
            response = self.s['requests_result']
            shop_list = self.s['shop_list']
            url = info[0] + str(51 - page)
            response = self.down.get_restaurant(url, response)
            self.recording_response(response)
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
        return

    def construct_url(self):
        """构造请求用的url"""
        urls = []
        url = self.s['url_shop_list']
        area = self.s['city_list'][self.s['provs']]
        cate_file = self.s['category_file'][self.s['choice']]

        for city in area:
            for category in open(cate_file, 'r', encoding=self.s['encode']):
                info = city.strip().split(self.s['blank'])
                cate = category.strip().split(self.s['blank'])
                urls.append(
                    [url % (info[-3], self.s['types'][self.s['choice']], cate[1], info[-2]), cate[0], info]
                )
        return urls

    def shop_info(self):
        """"这里要做的是，完成每个商铺的详细信息获取

        也是要做一个清洗，做一个增量更新
        """
        shop_list = (i.strip().split(self.s['blank'])
                     for i in open(self.s['shop_list_file'][self.s['choice']], 'r', encoding=self.s['encode'])
                     )
        shop_exists = set(i.strip() for i in open(self.s['shop_exists'][self.s['choice']], 'r', encoding=self.s['encode'])
                          )
        pool = multiprocessing.Pool(4)
        for each in shop_list:
            if each[0] not in shop_exists:
                # self.shop_info_logic(each)
                pool.apply_async(self.shop_info_logic, (each,))
        pool.close()
        pool.join()

    def shop_info_logic(self, info):
        response = self.s['requests_result']
        shop_info = self.s['shop_info']
        response = self.down.shop_info(info[0], response)
        self.recording_response(response)
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

    def update_comments(self, min_date, max_date):
        """这里是作为评论天更新的存在
        这里要用到多进程
        评论页面的内容存在一开始日期随机，因此要通过阅读后几页的方式
        在这里不关心到底有多少的评论，有评论就抓取，无评论就跳过。 按照日期来过滤
        对于新增加的店铺实现全部评论抓取
        """
        f = open(self.s['shop_cmt_file'][self.s['choice']], 'w+')
        f.close()
        shop_list = (i.strip().split(self.s['blank'])
                     for i in open(self.s['shop_list_file'][self.s['choice']], 'r', encoding=self.s['encode'])
                     )
        pool = multiprocessing.Pool(10)
        for shop in shop_list:
            pool.apply_async(self.update_comments_logic, (shop, min_date, max_date))
            # self.update_comments_logic(shop, min_date, max_date)
        pool.close()
        pool.join()

    def update_comments_logic(self, shop, min_date, max_date):
        """获取评论的逻辑"""
        page, next_page = 1, True
        while next_page:
            response = self.s['requests_result']
            shop_cmt = self.s['shop_cmt']
            response = self.down.update_comment(shop[0], str(page), response)
            self.recording_response(response)
            if response['response'] is not 'bad_requests':
                shop_cmt = self.spider.update_comment(response['response'], shop_cmt)
                next_page = self.pipe.save_shop_cmt(shop_cmt['data'], shop, min_date, max_date) if (
                    not shop_cmt['data'] == []) else False
            page += 1
            # 清理内存
            response['response'] = ''
            response['url'] = ''
            response['params'] = ''
            response['status_code'] = ''
            response['error'] = ''
            shop_cmt['data'].clear()

    def recording_response(self, response):
        """"做记录写入日志

        暂时作为开发人员用来读取每次请求状态

        :param response: 返回的响应
        """
        if response['response'] is 'bad_requests':
            logging.debug('请求无效，返回"bad_requests"')
        elif response['error'] is not '':
            logging.warning('%s, url: %s, params: %s' % (response['error'], response['url'], response['params']))
        else:
            logging.debug('请求成功, url: %s, params: %s' % (response['url'], response['params']))
        return


class DianPingItemsDownloader(object):
    """作为下载器的存在

    """

    def __init__(self, setting):
        self.session = requests.session()
        self.s = setting

    def do_get_requests(self, *args):
        retry = 30
        response = args[2]
        while retry > 0:
            try:
                args[1]['User-Agent'] = Faker().user_agent()
                # 休息 0-1之间的随机数
                time.sleep(random.random())
                if len(args) == 3:
                    # res = self.session.get(args[0],
                    res = requests.get(args[0],
                                        headers=args[1],
                                        cookies=self.s['cookies'],
                                        proxies=self.s['proxies'],
                                        allow_redirects=True,
                                        timeout=30)
                else:
                    # res = self.session.get(args[0],
                    res = requests.get(args[0],
                                           headers=args[1],
                                           cookies=self.s['cookies'],
                                           params=args[3],
                                           proxies=self.s['proxies'],
                                           allow_redirects=True,
                                           timeout=30
                                           )
                response['status_code'] = res.status_code
                response['url'] = res.url
                if repr(res.status_code).startswith('2'):
                    self.session.cookies.update(res.cookies)
                    response['response'] = res.content.decode(self.s['encode'])
                    break
                else:
                    # 但凡遇到403，如果是代理的问题则切换ip
                    args[1]['Proxy-Switch-Ip'] = 'yes'
                    print(datetime.datetime.today().strftime('%Y-%m-%d %H-%M-%s'), '出现: ', res.status_code)
            except Exception as e:
                args[1]['Proxy-Switch-Ip'] = 'yes'
                response['error'] = e
            retry -= 1
        return response

    def get_category(self, response, city_id):
        url = self.s['categroy_url'] % (city_id, self.s['types'][self.s['choice']])
        headers = self.s['headers']
        response = self.do_get_requests(url, headers, response)
        return response

    def get_restaurant(self, url, response):
        headers = self.s['headers']
        response = self.do_get_requests(url, headers, response)
        return response

    def shop_info(self, id, response):
        headers = self.s['headers_xml']
        url = self.s['url_info']
        params = self.s['params']
        params['shopId'] = id
        params['_nr_force'] = int(time.time() * 1000)
        response = self.do_get_requests(url, headers, response, params)
        return response

    def update_comment(self, shopid, page, response):
        url = self.s['cmt_url'] % (shopid, page)
        headers = self.s['headers']
        response = self.do_get_requests(url, headers, response)
        return response

class DianPingItemsSpider(object):

    def __init__(self, setting):
        self.s = setting

    def get_category(self, html):
        selector = None
        data = []
        try:
            selector = etree.HTML(html)
        except:
            pass
        if selector is not None:
            parse = self.s['cate_list_parse']
            category_list = selector.xpath(parse['list'])
            if category_list:
                for cate in category_list:
                    id = cate.xpath(parse['id'])[0].split('/')[-1]
                    type = cate.xpath(parse['type'])[0]
                    data.append([type, id])
        return data

    def shop_list(self, html):
        data = []
        selector = None
        try:
            selector = etree.HTML(html)
        except:
            # 报错，写入文本
            data = []
            path = os.path.join(os.path.abspath(self.s['provs']), 'list_error.txt')
            with open(path, 'w+', encoding=self.s['encode']) as f:
                f.write(html)

        if selector is not None:
            parse = self.s['shop_list_parse']
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

    def update_comment(self, html, shop_cmt):
        parse = self.s['shop_cmt_parse']
        selector = None
        try:
            selector = etree.HTML(html)
        except:
            path = os.path.join(os.path.abspath(self.s['provs']), 'cmt_error.txt')
            with open(path, 'w+', encoding='utf8') as f:
                f.write(html)

        if selector is not None:
            data = selector.xpath(parse['data'])
            if data:
                for each in data:
                    user = each.xpath(parse['user'])[0] if each.xpath(parse['user']) else ''
                    contribution = each.xpath(parse['contribution'])[0] if each.xpath(parse['contribution']) else ''
                    attitute = each.xpath(parse['attitute'])[0] if each.xpath(parse['attitute']) else ''
                    score = ','.join(each.xpath(parse['score'])) if each.xpath(parse['score']) else ''
                    content = each.xpath(parse['content'])[0] if each.xpath(parse['content']) else ''
                    date = each.xpath(parse['date'])[0] if each.xpath(parse['date']) else '2001-01-01'
                    fav = ''
                    if each.xpath(parse['fav']):
                        fav = ','.join(each.xpath(parse['fav']))
                    imgs = ''
                    try:
                        if each.xpath(parse['imgs']):
                            imgs = ','.join(each.xpath(parse['imgs']))
                    except:
                        pass
                    shop_cmt['data'].append([user, contribution, attitute, score, content, date, fav, imgs])

        return shop_cmt



class DianPingItemsPipeline(object):
    """作为管道的存在

    """

    def __init__(self, setting):
        self.s = setting

    def save_category_list(self, cate_list):
        cate = []
        for i in cate_list:
            for each in i:
                cate.append((each[0], each[1]))
        # 去重
        cate_set = set(cate)
        text = ''
        for i in cate_set:
            text += self.s['blank'].join([i[0], i[1]]) + '\n'
        with open(self.s['category_file'][self.s['choice']], 'w+', encoding=self.s['encode']) as f:
            f.write(text)

    def save_shop_list(self, data, info):
        content = ''
        for each in data:
            txt = [info[1], info[2][0], info[2][1], info[2][2], info[2][3], info[2][4], info[2][5], info[2][6], info[2][7]]
            text = self.s['blank'].join(txt)
            text = re.sub('\r|\n| ', '', text)
            if not each[0] is '&':
                shop_id = each[0].split('/')[-1]
                content += self.s['blank'].join([shop_id, each[1], text]) + '\n'
        with open(self.s['shop_list_file'][self.s['choice']], 'a', encoding=self.s['encode']) as f:
            f.write(content)

    def save_shop_info(self, data, info, url):
        shop = self.s['data_style'][self.s['choice']]
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
        if self.s['choice'] is 'food':
            shop['人均消费'] = data[4]

        with open(self.s['shop_info_file'][self.s['choice']], 'a', encoding=self.s['encode']) as f:
            text = self.s['blank'].join([shop[i] for i in self.s['data_style_l'][self.s['choice']]])
            text = re.sub('\r|\n| |&|None', '', text) + '\n'
            f.write(text)
        # 保存这家店的ID
        with open(self.s['shop_exists'][self.s['choice']], 'a', encoding=self.s['encode']) as p:
            p.write(info[0] + '\n')

    def save_shop_cmt(self, data, info, min_date, max_date):
        result = True
        text = ''
        for each in data:
            # each[5] 清洗后的日期
            each[2] = self.clear_star(each[2])
            each[5] = self.clear_date(each[5])
            if each[5] < max_date and each[5] >= min_date:
                txt = [info[0], info[1], info[2]]
                txt.extend(each)
                text += re.sub('\r|\n| ', '', self.s['blank'].join(txt)) + '\n'
                result = True
            else:
                result = False
        with open(self.s['shop_cmt_file'][self.s['choice']], 'a', encoding=self.s['encode']) as f:
            f.write(text)
        # 写入历史文件
        with open(self.s['shop_cmt_history_file'][self.s['choice']], 'a', encoding=self.s['encode']) as f:
            f.write(text)
        return result

    def clear_star(self, info):
        score = re.findall('\d\d', info)[0] if re.findall('\d\d', info) else 10
        attitute = ''
        if score == '50':
            attitute = '非常好'
        elif score == '40':
            attitute = '好评'
        elif score == '30':
            attitute = '中评'
        else:
            attitute = '差评'
        return attitute

    def clear_date(self, date_temp):
        date_temp = '20' + re.findall('\d\d-\d\d-\d\d', date_temp)[0] if (
                re.findall('\d\d-\d\d-\d\d', date_temp)) else '17-01-01'
        return date_temp


class DianPingItemsSchedule(object):
    """简易的调度

    每次更新抓取时，当前日期没最大抓取日期，并在本次结束后写入文档里
    """

    def execute(self, setting, min_date, max_date, n):
        dpie = DianPingItemsEngine(setting)
        # 分类不必要每次都拿
        #
        # 同时，更新了策略，每一次迭代，并不重新获取列表了
        # dpie.get_catgory()
        if n == 1:
            dpie.shop_list()
            dpie.shop_info()
        dpie.update_comments(min_date, max_date)
        del dpie

    def main(self):
        # count存在的意思在于，只有第一次获取分类后，就不再花请求去获取分类
        #
        # 2018-01-10 这里做了逻辑处理，将日期的处理从execute提出，放入main函数里，涉及到共用的原因
        n = 1
        while True:
            max_date = datetime.datetime.today().strftime('%Y-%m-%d')
            for prov in config_area.PROVS_LIST:
                setting = self.reload_config(prov)
                min_date = open(setting['start_date'][setting['choice']], 'r', encoding=setting['encode']).read()
                self.do_clear_logging(setting)
                self.execute(setting, min_date, max_date, n)
                self.load_2_hdfs(setting)
                with open(setting['start_date'][setting['choice']], 'w+', encoding=setting['encode']) as f:
                    f.write(max_date)
                n += 1

    def do_clear_logging(self, setting):
        """将日志清理模块封装"""
        f = open(setting['requests_log'] % setting['provs'], 'w+')
        f.close()

    def load_2_hdfs(self, setting):
        shop_list = setting['shop_list_file'][setting['choice']]
        shop_info = setting['shop_info_file'][setting['choice']]
        shop_cmt = setting['shop_cmt_file'][setting['choice']]
        hdfs_shop_list = setting['hdfs'] % (os.path.split(shop_list)[1])
        hdfs_shop_info = setting['hdfs'] % (os.path.split(shop_info)[1])
        hdfs_shop_cmt = setting['hdfs'] % (os.path.split(shop_cmt)[1])
        try:
            hdfs = HDFileSystem(host='192.168.100.178', port=8020)
            hdfs.put(shop_list, hdfs_shop_list)
            hdfs.put(shop_info, hdfs_shop_info)
            hdfs.put(shop_cmt, hdfs_shop_cmt)
        except Exception as e:
            logging.warning('集群挂了:', e)

    def reload_config(self, prov):
        """
        作为动态的配置文件的导入
        """
        config = open('config.ini', 'r', encoding='utf8').read()
        with open('config.py', 'w', encoding='utf8') as f:
            f.write('PROVS=\'%s\'' % prov + '\n' + config)
        import config
        reload(config)
        setting = {
            'choice': config.CHOICE,
            'city_list': config.CITY_LIST,
            'provs': config.PROVS,
            'categroy_url': config.CATEGORY_URL,
            'cookies': config.COOKIES,
            'proxies': config.PROXIES,
            'blank': config.BLANK,
            'encode': config.ENCODEING,
            'requests_result': config.REQUESTS_RESULT,
            'types': config.TYPES,
            'headers': config.HEADERS,
            'headers_xml': config.HEADERS_XML,
            'category_list': config.CATEGORY_LIST,
            'cate_list_parse': config.CATEGORY_LIST_PARSE,
            'category_file': config.CATEGORY_FILE,
            'url_shop_list': config.SHOP_URL,
            'shop_list': config.SHOP_LIST,
            'shop_list_parse': config.SHOP_LIST_PARSE,
            'shop_list_file': config.SHOP_LIST_FILE,
            'url_info': config.INFO_URL,
            'params': config.PARAMS,
            'shop_info': config.SHOP_INFO,
            'data_style': config.DATA_STYLE,
            'data_style_l': config.DATA_STYLE_L,
            'shop_info_file': config.SHOP_INFO_FILE,
            'shop_exists': config.SHOP_ALREADY_EXISTS,
            'cmt_url': config.CMT_URL,
            'shop_cmt': config.SHOP_CMT,
            'shop_cmt_parse': config.SHOP_CMT_PARSE,
            'shop_cmt_file': config.SHOP_CMT_FILE,
            'shop_cmt_history_file': config.SHOP_CMT_HISTORY_FILE,
            'start_date': config.START_DATE_FILE,
            'hdfs': config.HDFS,
            'requests_log': config.REQUESTS_LOG,
        }
        return setting


if __name__ == '__main__':
    dpis = DianPingItemsSchedule()
    dpis.main()