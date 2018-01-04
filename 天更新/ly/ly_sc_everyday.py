'''
要求： 此脚本作为一个持久化的存在
1. 每日，对各个景区进行一次迭代，出现新的景区，补充放入列表中， 并进行评论数据抓取
2. 每一次迭代过程中，记录好时间，下一次迭代过程中通过读取上一次迭代时间，确定所需要的时间
3. 异常时间分为“今天”，“昨天”，“前天”,其余均为正常时间。
4. 不需要设置多进程抓取，4000个景区，每天4千次请求，轻松完成
***************************************************************
1. 请求景区列表的参数:
    url = https://www.ly.com/scenery/NewSearchList.aspx
    params = {
                "action": "getlist",
                "page": 1,
                "kw"= "成都",    地区
                "cid": "324",   地区的id
                }
2. 请求评论部分的参数:
    url = https://www.ly.com/scenery/AjaxHelper/DianPingAjax.aspx
    params = {
        "action": "GetDianPingList",
        "sid": "231579",    景区id
        "page": 1,          页数
        "labId": 6,         按时间来展示
        "pageSize": 100      每页评论数可自选
    }
****************************************************************
记录:
2017-08-15  开发完成 1.0版本
2.0版本构想：
    针对每次获取的新的景区，记录，同时获取它全部的评论

2017-08-16  开发完成 2.0版本

2017-10-20  调整逻辑，设为每天早上7点开跑
'''

__version__ = 1.0

import requests
import os
import re
import datetime
import time
import json
from imp import reload
from faker import Faker
from lxml import etree
try:
    from hdfs3 import HDFileSystem
except:
    pass
import config


class lyEngine:
    ''' 引擎的流程就是，迭代景区列表，新景区抓全部评论，其余景区抓指定的评论 '''

    def __init__(self):
        self.pipe = lyPipeline()
        self.down = lyDonwloader()
        self.spider = lySpider()

    def execute(self, order_date):
        #   刷新文档
        self.pipe.do_refresh_everyday_path()
        #    迭代景区列表
        self.iteration_scenic_list()
        #   更新景区评论
        self.update_scenic_cmt()
        '''
        第二部获取每个景区的评论，这里遇到的问题是，这个作为日更新的，只获取当日和昨天的数据，而基础数据只更新到5月。
        因为我要做一个日期选择的功能，在后期线上版本时候也便于维护
    '''
        #   更新迭代后景区列表的指定日期评论
        self.interation_scenic_cmt(order_date)

    def iteration_scenic_list(self):
        '''
        作为一个迭代景区列表的存在
        :return:
        '''
        city_list = self.pipe.city_list()()
        scenic_list = self.pipe.scenic_list_set()
        for each in city_list:
            page = 1
            #   之所选15，是因为会出现有的县城在请求时，会无限重复
            while page < 15:
                html = self.down.request_get_args(each[1], each[2], page)
                if not html == 'wrong_request':
                    content = self.spider.get_scenic_list(html)
                #   这里需要一个判断，是否此页有内容
                    if not self.spider.is_empyt_page(html):
                        self.pipe.save_as_scenic_list(
                            content, each[0], each[1], each[2], scenic_list())
                    else:
                        break
                page += 1

    def interation_scenic_cmt(self, order_date):
        '''
        作为景区评论的迭代存在，这里放入一个时间，自动判断并录入数据，达到每日更新的目的
        这里需要注意的地方，一个作为每日推送的版本，但是仍要做好数据存量的工作
        :return:
        '''
        #   第一步当然是遍历景区列表, 然后刷新一遍
        scenic_list = self.pipe.scenic_list()
        for each in scenic_list():
            page = 1
            next_page = True    # next_page 存在的意义在于判断是否本页数据为空,以及是否抓下一个景区
            while next_page:
                html = self.down.request_get_cmt(each[3], page)
                if html != 'wrong_requests':
                    next_page = self.spider.is_next_page(html, page)
                    if next_page:
                        #   这里不仅要拿数据，还要做判断，只要规定时间的数据
                        content = self.spider.get_cmt(html)
                        next_page = self.pipe.save_secenic_cmt_in_order(
                            content, order_date)
                page += 1




    def update_scenic_cmt(self):
        '''
        存在的意义就是，通过判断列表里新增的景区，从而对每一个景区进行迭代
        :return:
        '''
        new_scenic_list = self.pipe.new_secnic_list()
        for each in new_scenic_list():
            page = 1
            next_page = True
            while next_page:
                html = self.down.request_get_cmt(each, page)
                if html != 'wrong_requests':
                    next_page = self.spider.is_next_page(html, page)
                    if next_page:
                        content = self.spider.get_cmt(html)
                        self.pipe.save_as_new_scenic_cmt(content)
                page += 1


class lyDonwloader:
    def __init__(self):
        self.headers = lySetting.HEADERS
        self.session = requests.session()
        self.sleep = lySetting.SLEEP
        self.proxy = lyProxypool()

    def request_get_args(self, area, cid, page):
        url = lySetting.SCENIC_URL
        params = {
            'action': 'getlist',
            'page': page,
            'kw': area,
            'cid': cid
        }
        html = self.do_get(url, params)
        return html

    def request_get_cmt(self, sid, page):
        url = lySetting.CMT_URL
        params = {
            "action": "GetDianPingList",
            "sid": sid,
            "page": page,
            'labId': '6',
            "pageSize": 100
        }
        html = self.do_get(url, params)
        return html

    def do_get(self, *args):
        retry = 30
        headers = lySetting.HEADERS
        headers['User-Agent'] = Faker().user_agent()
        while retry > 0:
            try:
                time.sleep(self.sleep)
                respon = self.session.get(
                    args[0],
                    headers=headers,
                    params=args[1],
                    proxies=self.proxy.get_proxy(),
                    timeout=30) if len(args) == 2 else self.session.get(
                    args[0],
                    headers=headers,
                    proxies=self.proxy.get_proxy(),
                    timeout=30)
                if respon.status_code == 200 or respon.status_code == 404 or respon.status_code == 403:
                    response = respon.content.decode('utf8')
                    headers['Proxy-Switch-Ip'] = 'no'
                    break
                else:
                    response = 'wrong_requests'
                    headers['Proxy-Switch-Ip'] = 'yes'
            except Exception as e:
                print('请求出错', e)
                response = 'wrong_requests'
                headers['Proxy-Switch-Ip'] = 'yes'
            retry -= 1

        return response


class lySpider:
    def get_scenic_list(self, html):
        selector = etree.HTML(html)
        con = selector.xpath('//div[@class="scenery_list"]')
        data_list = []
        for each in con:
            data = []
            data.append(
                each.xpath('div[@class="list_l"]/div[@class="s_info"]/@sid'))  # 景区id
            data.append(each.xpath(
                'div[@class="list_l"]/div[@class="s_info"]/div[1]/dl/dt[1]/a/text()'))  # 景区名字
            data.append(each.xpath(
                'div[@class="list_l"]/div[@class="s_info"]/div[1]/dl/dd[1]/span/text()'))  # star
            data.append(each.xpath(
                'div[@class="list_l"]/div[@class="s_info"]/div[1]/dl/dd[2]/p/text()'))  # address
            data.append(each.xpath(
                'div[@class="list_l"]/div[@class="s_info"]/div[1]/dl/dd[3]/p/text()'))  # 特色
            data.append(each.xpath(
                'div[@class="list_l"]/div[@class="s_info"]/div[2]/div/span/b/text()'))  # 门票
            data_list.append(data)
        return data_list

    def is_empyt_page(self, html):
        #   只有在empty page里才会出现这个span这个标签
        is_tag = re.findall(' <div class="(.*?)"> <span', html, re.S)
        result = True if is_tag else False
        return result

    def get_cmt(self, html):
        try:
            js_dict = json.loads(html)
        except Exception as e:
            print('json解析问题,原html错误:', e)
            js_dict = {}
        cons = js_dict.get('dpList', {})
        content = []
        if cons is not None:
            for each in cons:
                # 景区id+景区名字+用户名+内容+评论内容+ 好评差评+点赞数+日期
                DPItemId = each.get('DPItemId', '')
                DPItemName = each.get('DPItemName', '')
                dpUserName = each.get('dpUserName', '')
                dpContent = each.get('dpContent', '')
                lineAccess = each.get('lineAccess', '')
                zanCount = each.get('zanCount', '')
                dpDate = each.get('dpDate', '')
                dpImgUrl = each.get('dpImgUrl', '')
                imgs = ''
                if dpImgUrl is not None:
                    for each in dpImgUrl:
                        if each.get('imgUrl', '&'):
                            imgs += 'http:' + each.get('imgUrl', '&') + ','
                content.append([DPItemId, DPItemName, dpUserName,
                                dpContent, lineAccess, zanCount, dpDate, imgs])
        return content

    def is_next_page(self, html, page):
        result = False
        try:
            js_dict = json.loads(html)
        except Exception as e:
            print('json解析问题,原html错误,此处认为无下一页:', e)
            js_dict = {}
        totalPage = js_dict.get('pageInfo', {}).get('totalPage', 1)
        # errorMsg = js_dict.get('errorMsg', 'no')
        # result = True if errorMsg == '' else False
        if page <= totalPage:
            result = True
        return result


class lyPipeline:
    def __init__(self):
        self.blank = lySetting.BLANK
        self.encode = lySetting.ENCODING
        self.hdfs = HDFileSystem(host='192.168.100.178', port=8020)

    def city_list(self):
        # return lambda: (i.strip().split(self.blank) for i in
        # open(os.path.join(os.path.abspath("DataList"),lySetting.CITY_LIST_PATH),'r',encoding=lySetting.ENCODING))
        return lambda: (
            i.strip().split(
                self.blank) for i in open(
                config.CITY_LIST_PATH,
                'r',
                encoding=lySetting.ENCODING))

    def scenic_list_set(self):
        # return lambda: set(i.strip().split(self.blank)[3] for i in
        # open(os.path.join(os.path.abspath("DataList"),lySetting.SCENIC_PATH),'r',encoding=lySetting.ENCODING))
        return lambda: set(
            i.strip().split(
                self.blank)[3] for i in open(
                config.SCENIC_PATH,
                'r',
                encoding=lySetting.ENCODING))

    def save_as_scenic_list(self, list, prov, city, cid, sc_list):
        ''' 参数显得多，同时sc_list是一个set   '''
        #   这里要对景区列表做一个增量
        content = ''
        for i in list:
            if not i[0][0] in sc_list:
                text = prov + self.blank + city + self.blank + cid + self.blank
                for each in i:
                    if each:
                        text += each[0] + self.blank
                    else:
                        text += '' + self.blank
                content += text.replace('\n', '').replace('\r', '') + '\n'
        #   只保存每次迭代新出现的景区
        # with open(os.path.join(os.path.abspath("DataList"),
        # lySetting.SCENIC_PATH), 'a', encoding=self.encode) as f:
        with open(config.SCENIC_PATH, 'a', encoding=self.encode) as f:
            f.write(content)

        #   添加一个新增加的景区
        # with open(os.path.join(os.path.abspath("DataList"),
        # lySetting.NEW_SCENIC_LIST), 'a', encoding=self.encode) as f:
        with open(config.NEW_SCENIC_LIST, 'a', encoding=self.encode) as f:
            f.write(content)

    def scenic_list(self):
        # return lambda: ( i.strip().split(self.blank) for i in
        # open(os.path.join(os.path.abspath("DataList"),
        # lySetting.SCENIC_PATH), 'r', encoding=self.encode))
        return lambda: (
            i.strip().split(
                self.blank) for i in open(
                config.SCENIC_PATH,
                'r',
                encoding=self.encode))

    def do_refresh_everyday_path(self):
        #   作为每次写入前，刷新一遍目录
        # f = open(os.path.join(os.path.abspath("Data"),lySetting.SCENIC_CMT_EVERYDAY), 'w+', encoding=self.encode)
        f = open(config.SCENIC_CMT_EVERYDAY, 'w+', encoding=self.encode)
        f.close()
        # g = open(os.path.join(os.path.abspath("DataList"),lySetting.NEW_SCENIC_LIST),'w',encoding=self.encode)
        g = open(config.NEW_SCENIC_LIST, 'w', encoding=self.encode)
        g.close()

    def save_secenic_cmt_in_order(self, content, order_time):
        #   一个今日数据，一个是历史累加数据
        text = ''
        #   通过count来判断，count为 0 则告诉引擎停止当前了
        count = 0
        for each in content:
            each[-2] = self.do_clear_date(each[-2])
            result = self.do_compare_date(order_time, each[-2])
            if result:
                count += 1
                text += self.blank.join(each).replace('\n',
                                                      '').replace('\r', '') + '\n'
            else:
                continue
        #   存每天
        # with open(os.path.join(os.path.abspath("Data"),
        # lySetting.SCENIC_CMT_EVERYDAY), 'a', encoding=self.encode) as f:
        with open(config.SCENIC_CMT_EVERYDAY, 'a', encoding=self.encode) as f:
            f.write(text)
        #   存历史
        # with open(os.path.join(os.path.abspath("Data"),
        # lySetting.SCENIC_CMT_HISTORY), 'a', encoding=self.encode) as f:
        with open(config.SCENIC_CMT_HISTORY, 'a', encoding=self.encode) as f:
            f.write(text)
        #   放hdfs上
        try:
            self.hdfs.put(
                '/home/spider/everyday/ly/Data/' +
                lySetting.SCENIC_CMT_EVERYDAY,
                '/user/spider/everyday/' +
                lySetting.SCENIC_CMT_EVERYDAY)
        except Exception as e:
            print('集群崩了', e)
        #   是时候做判断了，还要不要再跑一页
        next_page = True if count > 0 else False
        return next_page

    def do_clear_date(self, info):
        '''存在的意义在于,将 ”今天“，”昨天“， ”前天“这种字眼转化为实际时间'''
        if info in ['今天', '昨天', '前天']:
            info = datetime.datetime.today().strftime('%Y-%m-%d') if info == '今天' else info
            info = (
                datetime.datetime.today() -
                datetime.timedelta(
                    days=1)).strftime('%Y-%m-%d') if info == '昨天' else info
            info = (
                datetime.datetime.today() -
                datetime.timedelta(
                    days=2)).strftime('%Y-%m-%d') if info == '前天' else info
        else:
            info = info
        return info

    def do_compare_date(self, order_date, input_date):
        #   只要指定那一天的数据
        result = input_date == order_date
        #   但是在跑历史数据的情况下，需要选择以下
        # result = input_date >= order_date
        return result

    def new_secnic_list(self):
        # return lambda: (i.strip().split(self.blank)[3] for i in
        # open(os.path.join(os.path.abspath("DataList"),lySetting.NEW_SCENIC_LIST),'r',encoding=self.encode))
        return lambda: (
            i.strip().split(
                self.blank)[3] for i in open(
                config.NEW_SCENIC_LIST,
                'r',
                encoding=self.encode))

    def save_as_new_scenic_cmt(self, content):
        text = ''
        for each in content:
            each[-2] = self.do_clear_date(each[-2])
            text += self.blank.join(each).replace('\n',
                                                  '').replace('\r', '') + '\n'
        # with open(os.path.join(os.path.abspath("Data"),
        # lySetting.SCENIC_CMT_HISTORY), 'a', encoding=self.encode) as f:
        with open(config.SCENIC_CMT_HISTORY, 'a', encoding=self.encode) as f:
            f.write(text)


class lySetting:
    #   normal
    BLANK = '\u0001'
    ENCODING = 'utf8'
    SLEEP = 0.1
    #   path
    NEW_SCENIC_LIST = 'new_tc_scenic_list.txt'
    CITY_LIST_PATH = 'tc_city_list.txt'
    SCENIC_PATH = 'tc_scenic_list.txt'
    SCENIC_CMT_EVERYDAY = 'tc_scenic_everyday.txt'
    SCENIC_CMT_HISTORY = 'tc_scenic_history.txt'

    #   url
    SCENIC_URL = 'https://www.ly.com/scenery/NewSearchList.aspx'
    CMT_URL = 'https://www.ly.com/scenery/AjaxHelper/DianPingAjax.aspx'
    #   headers
    HEADERS = {
        'Host': 'www.ly.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': '',
        #   每一次请求自动换IP
        'Proxy-Switch-Ip': 'yes'
    }


class lyProxypool:
    def get_proxy(self):
        # 要访问的目标页面
        # targetUrl = "http://test.abuyun.com/proxy.php"
        # 代理服务器
        proxyHost = "proxy.abuyun.com"
        # proxyPort = "9020"
        proxyPort = "9010"

        # 代理隧道验证信息
        proxyUser = "HY3JE71Z6CDS782P"
        proxyPass = "CE68530DAD880F3B"

        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }

        proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }
        return proxies

class lySchedule:
    def execute(self):
        setting = self.reload_setting()  # 仅仅改到这一步，头晕，不想弄了

        lye = lyEngine()
        #   第一次补充数据从 2017-05-01开始
        # lye.execute('2017-05-01')
        yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        lye.execute(yesterday)
        #  析构实例
        del lye


    def reload_setting(self):
        # 作为配置文件的动态加载部分
        config_text = open('config.ini', 'r', encoding='utf8').read()
        with open('config.py', 'w+', encoding='utf8') as f:
            f.write(config_text)
        import config
        reload(config)
        return config



if __name__ == '__main__':
    while True:
        date = datetime.datetime.today().strftime('%H-%M')
        if date == '07-01':
            start = time.time()
            lys = lySchedule()
            lys.execute()
            del lys
            end = time.time()
            sleep = int(end - start)
            time.sleep(3600 * 24 - sleep)
        else:
            time.sleep(10)
