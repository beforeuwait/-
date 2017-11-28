# coding=utf8
'''
作为3.0版本，满足编目需求的点评网脚本。
流程：
    1. 获取列表，根据分类获取列表,同时每次更新分类
    2. 通过列表去获取店铺的基础数据
    3. 至于特色美食，无法获取，有token
    4. 获取评论，做好天更新

2017-11-24 修改逻辑，跟随网页改版
2017-11-27 修改逻辑，开始开发评论持久更新问题，开发自动提交模块
2017-11-28 进一步修改逻辑，并部署

'''

import config
import requests
import time
import json
import os
import re
import datetime
import multiprocessing
from faker import Faker
from lxml import etree
try:
    from hdfs3 import HDFileSystem
except BaseException:
    pass


class dianpingEntainmentEngine:

    def __init__(self) -> None:
        super().__init__()
        self.down = dianpingEntainmentDownloader()
        self.spider = dianpingEntainmentSpider()
        self.pipe = dianpingEntainmentPipeline()

    def execute_get_catgory(self):
        # 该模块作为迭代每个市，获取目录分类
        self.pipe.do_clear_category()
        city_list = self.pipe.deal_get_city_list()
        category_list = [self.get_category(i) for i in city_list]
        self.pipe.save_category_list(category_list)

    def get_category(self, city_id):
        url = dianpingEntainmentSetting.CATEGORY_URL % city_id
        html = self.down.get_category(url)
        data = self.spider.get_category(
            html) if html is not 'bad_requests' else []
        return data

    def execute_get_shop_list(self):
        # 作为获取餐厅列表的模块
        # 我打算一次性把url都生成然后去抓取列表
        # 这里要做一个增量列表更新
        start_urls = self.pipe.construct_url()
        shop_set = self.pipe.get_shop_list_set()
        pool = multiprocessing.Pool(1)
        for i in start_urls:
            # self.get_shop_list(i, shop_set)
            pool.apply_async(self.get_shop_list, (i, shop_set))
        pool.close()
        pool.join()

    def get_shop_list(self, info, restaurant_set):
        page = 50
        while page > 0:
            url = info[0] + str(51 - page)
            html = self.down.get_restaurant(url)
            data = self.spider.get_restaurant(
                html) if html is not 'bad_requests' else []
            self.pipe.save_shop_list(
                data, info, restaurant_set) if not data == [] else ''
            if data == []:
                break
            page -= 1

    def execute_get_info(self):
        # 这里要做的是，完成每个商铺的详细信息获取
        # 也是要做一个清洗，做一个增量更新
        shop_list = self.pipe.get_shop_list()
        shop_list_already = self.pipe.get_shop_list_set()
        pool = multiprocessing.Pool(1)
        for each in shop_list:
            if each[0] not in shop_list_already:
                # self.get_info(each)
                pool.apply_async(self.get_info, (each,))
        pool.close()
        pool.join()

    def get_info(self, info):
        html, url = self.down.get_info(info[0])
        data = self.spider.get_info(html) if html is not 'bad_requests' else []
        self.pipe.save_shop_info(data, info, url) if not data == [] else ''

    def execute_update_comments(self, min_date, max_date):
        # 这里是作为评论天更新的存在
        # 这里要用到多进程
        # 评论页面的内容存在一开始日期随机，因此要通过阅读后几页的方式
        # 在这里不关心到底有多少的评论，有评论就抓取，无评论就跳过。 按照日期来过滤
        # 对于新增加的店铺实现全部评论抓取
        shop_list = self.pipe.get_shop_list()
        pool = multiprocessing.Pool(1)
        for each in shop_list:
            pool.apply_async(self.get_comments, (each, min_date, max_date))
        pool.close()
        pool.join()

    def get_comments(self, each, min_date, max_date):
        # 获取评论的逻辑
        page, next_page = 1, True
        while next_page:
            html = self.down.get_comment(each[0], str(page))
            data = self.spider.get_comment(
                html) if html is not 'bad_requests' else []
            next_page = self.pipe.save_shop_cmt(
                data, each, min_date, max_date) if not data == [] else False
            page += 1


class dianpingEntainmentDownloader:

    def __init__(self) -> None:
        super().__init__()
        self.session = requests.session()
        self.cookies = dianpingEntainmentSetting.COOKIES

    def do_get_requests(self, *args):
        html = 'bad_requests'
        retry = 5
        while retry > 0:
            try:
                args[1]['User-Agent'] = Faker().user_agent()
                time.sleep(dianpingEntainmentSetting.DELAY)
                response = self.session.get(
                    args[0],
                    headers=args[1],
                    cookies=self.cookies,
                    proxies=config.PROXIES,
                    timeout=30) if len(args) == 2 else self.session.get(
                    args[0],
                    headers=args[1],
                    cookies=self.cookies,
                    params=args[2],
                    proxies=config.PROXIES,
                    timeout=30)
                if response.status_code == 200:
                    self.session.cookies.update(response.cookies)
                    html = response.content.decode(
                        dianpingEntainmentSetting.ENCODING)
                    break
                elif response.status_code == 403:
                    html = 'bad_requests'
                    args[1]['Proxy-Switch-Ip'] = 'yes'  # 但凡遇到403，如果是代理的问题则切换ip
            except BaseException:
                print('请求时出错。')
                args[1]['Proxy-Switch-Ip'] = 'yes'
            retry -= 1
        return html

    def get_category(self, url):
        headers = dianpingEntainmentSetting.HEADERS
        html = self.do_get_requests(url, headers)
        return html

    def get_restaurant(self, url):
        headers = dianpingEntainmentSetting.HEADERS
        html = self.do_get_requests(url, headers)
        return html

    def get_info(self, id):
        headers = dianpingEntainmentSetting.HEADERS_JSON
        url = dianpingEntainmentSetting.INFO_URL
        params = dianpingEntainmentSetting.PARAMS
        params['shopId'] = id
        params['_nr_force'] = int(time.time() * 1000)
        html = self.do_get_requests(url, headers, params)
        url_d = url + '?' + 'shopId=' + str(params['shopId'])
        return html, url_d

    def get_comment(self, shopid, page):
        url = dianpingEntainmentSetting.CMT_URL % (shopid, page)
        headers = dianpingEntainmentSetting.HEADERS
        html = self.do_get_requests(url, headers)
        return html


class dianpingEntainmentSpider:
    def get_category(self, html):
        selector = etree.HTML(html)
        cate = dianpingEntainmentSetting.ENTAINMENT_CATEGORY  # 这里是有两个分类
        cons = selector.xpath('//div[@class="groups"]/div[@class="group"]')
        data = []
        for each in cons:
            if each.xpath('div[@class="sec-title"]/span/text()')[0] == cate[0]:
                cate_list = each.xpath('div[@class="sec-items"]/a')
                for i in cate_list:
                    name = i.xpath('text()')[0] if i.xpath('text()') else ''
                    count = i.xpath(
                        '@data-click-name')[0] if i.xpath('@data-click-name') else ''
                    data.append((name, count))
            if each.xpath('div[@class="sec-title"]/span/text()')[0] == cate[1]:
                cate_list = each.xpath('div[@class="sec-items"]/a')
                for i in cate_list:
                    name = i.xpath('text()')[0] if i.xpath('text()') else ''
                    count = i.xpath(
                        '@data-click-name')[0] if i.xpath('@data-click-name') else ''
                    data.append((name, count))
        return data

    def get_restaurant(self, html):
        selector = etree.HTML(html)
        data = []
        cons = selector.xpath('//div[@id="shop-all-list"]/ul/li')
        if cons:
            for each in cons:
                url = each.xpath('div[@class="txt"]/div[@class="tit"]/a/@href')[
                    0] if each.xpath('div[@class="txt"]/div[@class="tit"]/a/@href') else '&'
                name = each.xpath('div[@class="txt"]/div[@class="tit"]/a/h4/text()')[
                    0] if each.xpath('div[@class="txt"]/div[@class="tit"]/a/h4/text()') else '&'
                data.append([url, name])
        return data

    def get_info(self, html):
        data = []
        try:
            js_dict = json.loads(html)
        except BaseException:
            js_dict = {}
        if js_dict.get('code', '') == 200:
            msg = js_dict.get('msg', {})
            shopInfo = msg.get('shopInfo', {})
            data.append(str(shopInfo.get('address', '')))   # 地址
            data.append(str(shopInfo.get('crossRoad', '')))  # 周边信息
            data.append(str(shopInfo.get('glat', '')) + ',' +
                        str(shopInfo.get('glng', '')))  # 坐标
            data.append(str(shopInfo.get('businessHours', '')))   # 营业时间
            data.append(str(shopInfo.get('avgPrice', '')))     # 人均消费
            data.append(str(shopInfo.get('phoneNo', '')))  # 联系电话
            data.append(str(shopInfo.get('publicTransit', '')))  # 交通信息
            data.append(str(shopInfo.get('writeUp', '')))   # 简介
        return data

    def get_comment(self, html):
        data = []
        try:
            selector = etree.HTML(html)
            cons = selector.xpath(
                '//div[@class="comment-mode"]/div[@class="comment-list"]/ul/li')
            if cons:
                for each in cons:
                    user = each.xpath('div[@class="pic"]/p[@class="name"]/a/text()')[
                        0] if each.xpath('div[@class="pic"]/p[@class="name"]/a/text()') else ''
                    contribution = each.xpath('div[@class="pic"]/p[@class="contribution"]/span/@title')[
                        0] if each.xpath('div[@class="pic"]/p[@class="contribution"]/span/@title') else ''
                    attitute = each.xpath('div[@class="content"]/div[@class="user-info"]/span/@title')[
                        0] if each.xpath('div[@class="content"]/div[@class="user-info"]/span/@title') else ''
                    socer = ','.join(each.xpath('div[@class="content"]/div[@class="user-info"]/div[@class="comment-rst"]/span/text()')) if each.xpath(
                        'div[@class="content"]/div[@class="user-info"]/div[@class="comment-rst"]/span/text()') else ''
                    content = each.xpath('div[@class="content"]/div[@class="comment-txt"]/div/text()')[
                        0] if each.xpath('div[@class="content"]/div[@class="comment-txt"]/div/text()') else ''
                    date = each.xpath('div[@class="content"]/div[@class="misc-info"]/span[@class="time"]/a/text()')[0] if each.xpath(
                        'div[@class="content"]/div[@class="misc-info"]/span[@class="time"]/a/text()') else '2001-01-01'
                    fav = ''
                    if each.xpath(
                            'div[@class="content"]/div[@class="comment-recommend"]/text()'):
                        fav = ','.join(
                            each.xpath('div[@class="content"]/div[@class="comment-recommend"]/a/text()'))
                    data.append([user, contribution, attitute,
                                 socer, content, date, fav])
        except BaseException:
            print('评论解析时出错')
        return data


class dianpingEntainmentPipeline:
    def __init__(self):
        self.blank = dianpingEntainmentSetting.BLANK
        self.code = dianpingEntainmentSetting.ENCODING

    def deal_get_city_list(self):
        area = config.AREA_FILE
        city_list = set(i.strip().split(self.blank)
                        [-3] for i in open(area, 'r', encoding=self.code))
        return city_list

    def save_category_list(self, cate_list):
        cate = []
        for i in cate_list:
            for each in i:
                cate.append(each)
        cate_list = set(cate)   # 去重
        text = ''
        f = open(config.CATEGORY_ENTAINMENT, 'w', encoding=self.code)
        for i in cate_list:
            text += i[0] + self.blank + i[1] + self.blank + '\n'
        f.write(text)
        f.close()

    # def resturant_set(self):
    #     if os.path.exists(config.RESTAURANT_LIST):
    #         restaurant_set = set(i.strip().split(self.blank)[0] for i in open(config.RESTAURANT_LIST, 'r', encoding=self.code))
    #     else:
    #         open(config.RESTAURANT_LIST, 'w+', encoding=self.code)
    #         restaurant_set = set(i.strip().split(self.blank)[0] for i in open(config.RESTAURANT_LIST, 'r', encoding=self.code))
    #     return restaurant_set

    def construct_url(self):
        urls = []
        url = dianpingEntainmentSetting.SHOP_URL
        area = config.AREA_FILE
        entainment_cate = config.CATEGORY_ENTAINMENT
        for i in open(area, 'r', encoding=self.code):
            for t in open(entainment_cate, 'r', encoding=self.code):
                info = i.strip().split(self.blank)
                cate = t.strip().split(self.blank)
                urls.append([url %
                             (info[-3], cate[1], info[-2]), cate[0], info])
        return urls

    def save_shop_list(self, data, info, restaurant_set):
        content = ''
        for each in data:
            text = info[1] + self.blank + self.blank.join(
                [info[2][0], info[2][1], info[2][2], info[2][3], info[2][4], info[2][5], info[2][6], info[2][7]])
            if not each[0] is '&':
                shop_id = each[0].split('/')[-1]
                if shop_id not in restaurant_set:
                    content += shop_id + self.blank + \
                        each[1] + self.blank + text + '\n'
        with open(config.ENTAINMENT_LIST, 'a', encoding=self.code) as f:
            f.write(content)

    def get_shop_list(self):
        if os.path.exists(config.ENTAINMENT_LIST):
            shop_list = (
                i.strip().split(
                    self.blank) for i in open(
                    config.ENTAINMENT_LIST,
                    'r',
                    encoding=self.code))
        else:
            open(config.ENTAINMENT_LIST, 'w+', encoding=self.code)
            shop_list = (
                i.strip().split(
                    self.blank) for i in open(
                    config.ENTAINMENT_LIST,
                    'r',
                    encoding=self.code))
        return shop_list

    def get_shop_list_set(self):
        if os.path.exists(config.EX_ENTAINMENT_ID_LIST):
            shop_list_set = set(str(i.strip()) for i in open(
                config.EX_ENTAINMENT_ID_LIST, 'r', encoding=self.code))
        else:
            open(config.EX_ENTAINMENT_ID_LIST, 'w+', encoding=self.code)
            shop_list_set = set(str(i.strip()) for i in open(
                config.EX_ENTAINMENT_ID_LIST, 'r', encoding=self.code))
        return shop_list_set

    def save_shop_info(self, data, info, url):
        shop = config.ENTAINMENT_DATA
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
        with open(config.ENTAINMET_INFO % config.PROVINCE, 'a', encoding=self.code) as f:
            # text = ''
            # for i in config.ENTAINMENT_DATA_L:
            #     text += shop[i].replace('&', '').replace('\n', '').replace('\r', '').replace('None', '') + self.blank
            text = self.blank.join([shop[i].replace('&', '').replace('\n', '').replace(
                '\r', '').replace('None', '') for i in config.ENTAINMENT_DATA_L])
            f.write(text + '\n')
        # 保存这家店的ID
        with open(config.EX_ENTAINMENT_ID_LIST, 'a', encoding=self.code) as p:
            p.write(info[0] + '\n')

    def save_shop_cmt(self, data, info, min_date, max_date):
        result = True
        text = ''
        for each in data:
            date = self.clear_date(each[5])
            if date < max_date and date >= min_date:
                content = info[0] + self.blank + info[1] + \
                    self.blank + info[2] + self.blank
                content += each[0] + self.blank + each[1] + self.blank + each[3] + \
                    self.blank + each[4] + self.blank + date + self.blank + each[6]
                text += content.replace('\n', '').replace('\r', '') + '\n'
                result = True
            else:
                result = False
        with open(config.ENTAINMENT_CMT % (config.PROVINCE, min_date, max_date), 'a', encoding='utf8') as f:
            f.write(text)
        return result

    def clear_date(self, date_temp):
        date = date_temp
        if len(date_temp) == 5:
            date = datetime.datetime.today().strftime('%Y') + '-' + date_temp
        elif len(date_temp) == 8:
            date = '20' + date_temp
        else:
            date = '20' + re.findall('\d\d-\d\d-\d\d',
                                     date_temp)[0] if re.findall('\d\d-\d\d-\d\d',
                                                                 date_temp) else '17-01-01'
        return date

    def do_clear_category(self):
        f = open(config.CATEGORY_ENTAINMENT, 'w', encoding=self.code)
        f.close()


class dianpingEntainmentSetting:
    ENTAINMENT_CATEGORY = ['玩乐', '足疗洗浴']

    CATEGORY_NUMBER = '30'

    BLANK = '\u0001'

    ENCODING = 'utf8'

    CATEGORY_URL = 'http://www.dianping.com/search/category/%s/30/'

    # 四个参数，依旧是cityid， 菜品分类， 行政区
    SHOP_URL = 'http://www.dianping.com/search/category/%s/30/%s%sp'

    INFO_URL = 'http://www.dianping.com/ajax/json/shopfood/wizard/BasicHideInfoAjaxFP'

    CMT_URL = 'http://www.dianping.com/shop/%s/review_more_latest?pageno=%s'

    HEADERS = {
        'Host': 'www.dianping.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
    }

    DELAY = 0.1

    PARAMS = {
        "_nr_force": "1508318702379",
        "shopId": "66037477",
    }
    HEADERS_JSON = {
        'X-Request': 'JSON',
        'X-Requested-With': 'XMLHttpRequest',
        'Host': 'www.dianping.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
    }
    COOKIES = {
        "Cookie": "_hc.v=45688cab-38e5-5113-0925-5b29cec21bd0.1497591535;"
        " __utma=1.523204225.1500969035.1508122747.1508133891.3;"
        " __utmz=1.1500969035.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none);"
        " __mta=180821272.1508222890270.1508222890270.1508222890270.1;"
        " _lxsdk_cuid=15f29183988a8-054623d37a853c-791c30-1fa400-15f2918398ac8;"
        " _lxsdk=15f29183988a8-054623d37a853c-791c30-1fa400-15f2918398ac8;"
        " s_ViewType=10;"
        " JSESSIONID=B0971DDEBF2E111965BBF4D5DE1B8CB3;"
        " aburl=1;"
        " cy=8;"
        " cye=chengdu;"
        " _lxsdk_s=15f333628db-7fe-d63-993%7C%7C11"}


class dianpingSchedule:
    """
    这是之前的调度方案
    def execute(self, command):
        if command is 'all':
            dpe = dianpingEntainmentEngine()
            dpe.execute_get_catgory()
            dpe.execute_get_shop_list()
            dpe.execute_get_info()
            dpe.execute_update_comments()
            del dpe
        elif command is 'list':
            dpe = dianpingEntainmentEngine()
            dpe.execute_get_catgory()
            dpe.execute_get_shop_list()
            del dpe
        elif command is 'info':
            dpe = dianpingEntainmentEngine()
            dpe.execute_get_info()
            del dpe
        elif command is 'cmt':
            dpe = dianpingEntainmentEngine()
            dpe.execute_update_comments()
            del dpe
    #
    # 新的调度方案
    # 每一次流程，将完整执行一次
    # 从，获取新列表，更新新的商铺信息，更新评论
    # 评论的更新，每一次从上一次的 end_date 开始，一开始执行就设置本次的end_date
    """

    def execute(self, min_date, max_date):
        dpe = dianpingEntainmentEngine()
        dpe.execute_get_catgory()
        dpe.execute_get_shop_list()
        dpe.execute_get_info()
        dpe.execute_update_comments(min_date, max_date)
        with open(config.MIN_DATE_FILE_ENTERTAIN, 'w', encoding='utf8') as f:
            f.write(datetime.datetime.today().strftime('%Y-%m-%d'))
        del dpe

    def main(self):
        while True:
            with open(config.MAX_DATE_FILE_ENTERTAIN, 'w', encoding='utf8') as f:
                f.write(datetime.datetime.today().strftime('%Y-%m-%d'))
            min_date = open(
                config.MIN_DATE_FILE_ENTERTAIN,
                'r',
                encoding='utf8').read()
            max_date = open(
                config.MAX_DATE_FILE_ENTERTAIN,
                'r',
                encoding='utf8').read()
            self.execute(min_date, max_date)
            self.load_2_hdfs(min_date, max_date)

    def load_2_hdfs(self, min_date, max_date):
        shop_info = config.ENTAINMET_INFO % config.PROVINCE
        shop_cmt = config.ENTAINMENT_CMT % (
            config.PROVINCE, min_date, max_date)
        hdfs_shop_info = config.HDFS % (
            os.path.split(shop_info)[1])
        hdfs_shop_cmt = config.HDFS % (os.path.split(shop_cmt)[1])
        try:
            hdfs = HDFileSystem(host='192.168.100.178', port=8020)
            hdfs.put(shop_info, hdfs_shop_info)
            hdfs.put(shop_cmt, hdfs_shop_cmt)
        except Exception as e:
            print('集群挂了', e)


if __name__ == '__main__':
    dps = dianpingSchedule()
    dps.main()
