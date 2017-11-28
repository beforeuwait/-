__author__ = 'Wang Jia Wei'

"""
这个脚本作为携程攻略中各旅游目的的餐馆的采集脚本
记录：
2017-10-27：为二级市添加行政区，不然，数据少的可怜,这个模块放在get_area.py中了

2017-11-07: 开始开发，评论部分
"""

import requests
import json
import re
import os
import config
import datetime
from faker import Faker
import multiprocessing
from lxml import etree
try:
    from hdfs3 import HDFileSystem
except:
    pass

class ctripShopEngine:
    def __init__(self) -> None:
        super().__init__()
        self.down = ctripShopDownloader()
        self.spider = ctripShopSpider()
        self.pipe = ctripShopPipeline()

    def shop_list(self):
        """
        获取携程攻略各目的地的餐馆列表
        """
        pool = multiprocessing.Pool(2)
        city_list = (i.strip().split(setting.blank) for i in open(setting.city_list, 'r', encoding=setting.encode)) # 获取已抓取的城市列表
        for each in city_list:
            # self.shop_list_logic(each)
            pool.apply_async(self.shop_list_logic, (each,))
        pool.close()
        pool.join()

    def shop_list_logic(self, info):
        page, next_page = 1, True
        while next_page:
            print(info, page)
            html = self.down.shop_list(info[-2], page) if info[-1] == '' else self.down.shop_list_area(info[-2], info[-1], page)
            shop_list = self.spider.shop_list(html) if html is not 'bad_requests' else []
            next_page = True if not shop_list == [] else False
            if next_page:
                self.pipe.save_shop_list(info, shop_list)
            page += 1


    def shop_info_pid(self):
        """
        1. 再获取列表后，获取每个商铺的详情
        2. 同时获取pid，为评论的抓取做准备
        3. 这里暴露一个问题就是，必须在获取详情后才能拿到pid
        4. 注意这里需要做一个增量更新
        5. 提供两种方式抓取，普通，和多进程两种
        """
        pool = multiprocessing.Pool(2)
        shop_ex_set = set(i.strip().split(setting.blank)[0]for i in open(setting.restaurant_ex, 'r', encoding=setting.encode))
        shop_list = (i.strip().split(setting.blank)for i in open(setting.restaurant_list, 'r', encoding=setting.encode))
        for each in shop_list:
            if each[8] not in shop_ex_set:
                # self.shop_info_pid_logic(each)
                pool.apply_async(self.shop_info_pid_logic, (each,))
        pool.close()
        pool.join()

    def shop_info_pid_logic(self, info):
        """
        这里要做的是获取每个商铺详细信息，保存，同时保存一份已保存目录并添加pid字段，评论从已获取中提取商铺id以及pid
        :param info: 列表信息
        :return:
        """
        html = self.down.shop_info_pid(info[-1])
        data = self.spider.shop_info_pid(html) if html is not 'bad_requests' else []
        self.pipe.save_shop_info_pid(data, info) if not data == [] and data[2] is not '1' else ''


    def shop_comment(self, start, end):
        """
        这里作为获取每个店铺的评论模块
        """
        pool = multiprocessing.Pool(1)
        shop_list = (i.strip().split(setting.blank)for i in open(setting.restaurant_ex, 'r', encoding=setting.encode))
        # cmt_done = set(i.strip() for i in open(setting.comment_done, 'r', encoding=setting.encode))
        for each in shop_list:
            # if each[0] not in cmt_done:
            # self.shop_comment_logic(each[0], each[1], each[2])
                # self.pipe.save_cmt_done(each[0])
            pool.apply_async(self.shop_comment_logic, (each[0], each[1], each[2], start, end))
        pool.close()
        pool.join()

    def shop_comment_logic(self, shop_id, pid, cnc, start, end):
        """
        由于网站恶心，只能看1000条，100页是上限。
        """
        print(shop_id, pid, cnc)
        num, next_page = 1, True
        while next_page:
            print(num)
            html = self.down.shop_comment(pid, cnc, num, shop_id)
            cmt_list = self.spider.shop_comment(html) if html is not 'bad_requests' else []
            next_page = self.pipe.save_shop_cmt(cmt_list, shop_id, start, end) if not cmt_list == [] else False
            if num == 100:
                break
            num += 1


class ctripShopDownloader:
    def do_get_requests(self, *args):
        retry = 5
        response = 'bad_requests'
        while retry > 0:
            args[1]['User-Agent'] = Faker().user_agent()
            try:
                res = requests.get(args[0], headers=args[1], proxies=setting.proxy, timeout=30) \
                    if len(args) == 2 \
                    else requests.get(args[0], headers=args[1], params=args[2], proxies=setting.proxy, timeout=30)
                if repr(res.status_code).startswith('2'):
                    response = res.content.decode(setting.encode)
                    break
                elif repr(res.status_code).startswith('4'):
                    args[1]['Proxy-Switch-Ip'] = 'yes'
                    continue
                # 这里暂时只对 2xx和4xx做处理
            except Exception as e:
                print('GET请求过程中出错', e)
                args[1]['Proxy-Switch-Ip'] = 'yes'
            retry -= 1
        return response

    def shop_list(self, city_id, page):
        url = setting.shop_list_url %(city_id, page)
        headers = setting.headers
        html = self.do_get_requests(url, headers)
        return html

    def shop_info_pid(self, link):
        url = setting.local_url % link
        headers = setting.headers
        html = self.do_get_requests(url, headers)
        return html

    def shop_list_area(self, city_id, area_id, page):
        url = setting.shop_list_url_area %(city_id, area_id, page)
        headers = setting.headers
        html = self.do_get_requests(url, headers)
        return html

    def shop_comment(self, pid, cnc, page, shop_id):
        url = setting.shop_comment_url
        data = setting.comment_data
        data['poiID'] = pid
        data['districtEName'] = cnc
        data['pagenow'] = page
        data['resourceId'] = shop_id
        headers = setting.headers_xml
        html = self.do_get_requests(url, headers, data)
        return html

class ctripShopSpider:
    def shop_list(self, html):
        selector = etree.HTML(html)
        shop_list = selector.xpath('//div[@class="list_wide_mod2"]/div[@class="list_mod2"]')
        data = []
        for each in shop_list:
            id = each.xpath('div[@class="abiconbox"]/@data-id')[0] \
                if each.xpath('div[@class="abiconbox"]/@data-id') \
                else ''
            name = each.xpath('div[@class="rdetailbox"]/dl/dt/a/@title')[0] \
                if each.xpath('div[@class="rdetailbox"]/dl/dt/a/@title') \
                else ''
            address = each.xpath('div[@class="rdetailbox"]/dl/dd[1]/text()')[0] \
                if each.xpath('div[@class="rdetailbox"]/dl/dd[1]/text()') \
                else ''
            average = each.xpath('div[@class="rdetailbox"]/dl/dd[2]/span/text()')[0] \
                if each.xpath('div[@class="rdetailbox"]/dl/dd[2]/span/text()') \
                else ''
            url = each.xpath('div[@class="rdetailbox"]/dl/dt/a/@href')[0] \
                if each.xpath('div[@class="rdetailbox"]/dl/dt/a/@href') \
                else ''
            data.append([id, name, address, average, url])
        return data

    def shop_info_pid(self, html):
        selector = etree.HTML(html)
        data = []
        ex_info = re.findall('poiData: (.*),', html)[0] \
            if re.findall('poiData: (.*),', html) \
            else ''
        try:
            js_dict = json.loads(ex_info)
        except Exception as e:
            print('坐标解析错误，', e)
            js_dict = {}
        # 经纬度
        lng = js_dict.get('lng', '')
        lat = js_dict.get('lat', '')
        data.append(lng)
        data.append(lat)
        # 如果pid 返回值为'1'的话，则放弃对该店铺的评论获取
        pid = selector.xpath('//input[@id="poi_id"]/@value')[0]\
            if selector.xpath('//input[@id="poi_id"]/@value')\
            else '1'
        data.append(pid)
        category = selector.xpath('//div[@class="s_sight_infor"]/ul/li[2]/span[2]/dd/a[1]/text()')[0]\
            if selector.xpath('//div[@class="s_sight_infor"]/ul/li[2]/span[2]/dd/a[1]/text()')\
            else ''
        data.append(category)
        tel = selector.xpath('//div[@class="s_sight_infor"]/ul/li[3]/span[2]/text()')[0]\
            if selector.xpath('//div[@class="s_sight_infor"]/ul/li[3]/span[2]/text()')\
            else ''
        data.append(tel)
        opentime = selector.xpath('//div[@class="s_sight_infor"]/ul/li[5]/span[2]/text()')[0]\
            if selector.xpath('//div[@class="s_sight_infor"]/ul/li[5]/span[2]/text()')\
            else ''
        data.append(opentime)
        description = selector.xpath('//div[@class="detailcon"]/div[@itemprop="description"]/text()')[0]\
            if selector.xpath('//div[@class="detailcon"]/div[@itemprop="description"]/text()')\
            else ''
        data.append(description)
        cate = selector.xpath('//div[@class="detailcon"]/div[@class="text_style"]/p/text()')[0]\
            if selector.xpath('//div[@class="detailcon"]/div[@class="text_style"]/p/text()')\
            else ''
        data.append(cate)
        return data

    def shop_comment(self, html):
        selector = etree.HTML(html)
        cons = selector.xpath('//div[@class="comment_ctrip"]/div[@class="comment_single"]')
        cmt_list = []
        if cons:
            for each in cons:
                user = each.xpath('div[@class="userimg"]/span/a/text()')[0] if each.xpath('div[@class="userimg"]/span/a/text()') else ''
                star = each.xpath('ul/li[1]/span[1]/span[1]/span/@style')[0] if each.xpath('ul/li[1]/span[1]/span[1]/span/@style') else ''
                socar = each.xpath('ul/li[1]/span[1]/span[2]/text()')[0] if each.xpath('ul/li[1]/span[1]/span[2]/text()') else ''
                time1 = each.xpath('ul/li[1]/span[2]/text()')[0] if each.xpath('ul/li[1]/span[2]/text()') else ''
                comment = each.xpath('ul/li[2]/span/text()')[0] if each.xpath('ul/li[2]/span/text()') else ''
                time2 = each.xpath('ul/li[3]/span[1]/span/em/text()')[0] if each.xpath('ul/li[3]/span[1]/span/em/text()') else ''
                cmt_list.append([user, star, socar, time1, comment, time2])
        return cmt_list



class ctripShopPipeline:

    def save_shop_list(self, info, data):
        text = ''
        exinfo = info.copy()
        exinfo.pop(-1)
        city = exinfo
        for each in data:
            context = setting.blank.join(city)
            text += context + setting.blank + setting.blank.join(each) + '\n'
        with open(setting.restaurant_list, 'a', encoding=setting.encode) as f:
            f.write(text)

    def save_shop_info_pid(self, data, shop_info):
        info = setting.restaurant_dict
        info_l = setting.restaurant_dict_l
        info['中文全称'] = shop_info[9]
        info['所属地区'] = shop_info[2]
        info['地址'] = shop_info[-3]
        info['地理位置'] = repr(data[0]) + ',' + repr(data[1])
        info['类型'] = data[3]
        info['营业时间'] = data[5]
        info['人均消费'] = shop_info[-2]
        info['特色菜品'] = data[-1]
        info['咨询电话'] = data[4]
        info['简介'] = data[-2]
        info['url'] = setting.local_url %shop_info[-1]
        info['省自治区全称'] = shop_info[0]
        info['省自治区简称'] = shop_info[1]
        info['市州全称'] = shop_info[2]
        info['市州简称'] = shop_info[3]
        info['区县全称'] = shop_info[4]
        info['区县简称'] = shop_info[5]
        info['地区编码'] = shop_info[6]
        text_list = [info[i] for i in info_l]
        text = setting.blank.join(text_list).replace('\n', '').replace('\r', '').replace(' ', '') + '\n'
        text_ex = setting.blank.join([shop_info[8], data[2], re.findall('(.*?)\d', shop_info[-1].split('/')[2])[0]]) + '\n'
        with open(setting.restaurant_info, 'a', encoding=setting.encode) as f:
            f.write(text)

        with open(setting.restaurant_ex, 'a', encoding=setting.encode) as f:
            f.write(text_ex)

    def save_shop_cmt(self, cmt_list, shop_id, start, end):
        text = ''
        result = False
        for each in cmt_list:
            if each[-1] >= start and each[-1] <= end:
                text += shop_id + setting.blank + setting.blank.join(each).replace('\n', '').replace('\r', '') \
                    .replace(' ', '').replace('width:', '').replace('%', '') + '\n'
                result = True
            else:
                result = False
        with open(setting.comment_txt % (start, end), 'a', encoding=setting.encode) as f:
            f.write(text)
        return result

    def save_cmt_done(self, shop_id):
        #   保存进度
        with open(setting.comment_done, 'a', encoding=setting.encode) as f:
            f.write(shop_id + '\n')

class setting:
    """
    这个类作为引入config.py里的参数并提供给这个脚本里使用
    """

    blank = config.BLANK

    encode = config.ENCODING

    proxy = config.PROXY

    city_list = config.CITY_LIST

    shop_list_url = 'http://you.ctrip.com/restaurantlist/%s/s0-p%s.html'

    shop_list_url_area = 'http://you.ctrip.com/restaurantlist/%s/s0-r%s-p%s.html'

    shop_comment_url = 'http://you.ctrip.com/destinationsite/TTDSecond/SharedView/AsynCommentView'

    local_url = 'http://you.ctrip.com%s'

    restaurant_list = config.RESTAURANT_SHOP_LIST

    restaurant_info = config.RESTAURANT_SHOP_INFO

    restaurant_ex = config.RESTAURANT_SHOP_EX

    restaurant_dict = config.RESTAURANT_DICT

    restaurant_dict_l = config.RESTAURANT_DICT_L

    headers = config.HEADERS

    headers_xml = config.HEADERS_XML

    comment_data = config.RESTAURANT_DATA

    comment_txt = config.RESTAURANT_SHOP_CMT

    comment_done = config.RESTAURANT_CMT_DONE

    start_date = config.CMT_START_DATE

    end_date = config.CMT_START_END

class ctripShopExecute:
    """
    def __init__(self, commend):
        self.commend = commend

    def execute(self):
        if self.commend == 'all':
            cse = ctripShopEngine()
            cse.shop_list()
            cse.shop_info_pid()
            del cse

        elif self.commend == 'list':
            cse = ctripShopEngine()
            cse.shop_list()
            del cse

        elif self.commend == 'info':
            cse = ctripShopEngine()
            cse.shop_info_pid()
            del cse

        elif self.commend == 'cmt':
            cse = ctripShopEngine()
            cse.shop_comment()
            del cse

    # 新的调度将执行, 只抓取9个省份的数据
    # 不断重复抓取
    # 每次更新列表，添加新的info信息
    # 按抓取日期上床评论
    """
    def execute(self, start_date, end_date):

        cse = ctripShopEngine()
        cse.shop_list()
        cse.shop_info_pid()
        cse.shop_comment(start_date, end_date)
        with open(config.RESTAURANT_CMT_START, 'w', encoding=setting.encode) as f:
            f.write(datetime.datetime.today().strftime('%Y-%m-%d'))
        del cse

    def main(self):
        while True:
            # 一开始将设置当时的时间为结束时间
            with open(config.RESTAURANT_CMT_END, 'w', encoding=setting.encode) as f:
                f.write(datetime.datetime.today().strftime('%Y-%m-%d'))
            start_date = open(config.RESTAURANT_CMT_START, 'r', encoding=setting.encode).read()
            end_date = open(config.RESTAURANT_CMT_END, 'r', encoding=setting.encode).read()
            self.execute(start_date, end_date)
            self.load2hdfs(start_date, end_date)

    def load2hdfs(self, start, end):
        cmt = config.RESTAURANT_SHOP_CMT % (start, end)
        shop_info = config.RESTAURANT_SHOP_INFO
        shop_list = config.RESTAURANT_SHOP_LIST
        hdfs_cmt = config.HDFS_PATH % (os.path.split(cmt)[1])
        hdfs_info = config.HDFS_PATH % (os.path.split(shop_info)[1])
        hdfs_shop_list = config.HDFS_PATH % (os.path.split(shop_list)[1])
        try:
            hdfs = HDFileSystem(host='192.168.100.178', port=8020)
            hdfs.put(cmt, hdfs_cmt)
            hdfs.put(shop_info, hdfs_info)
            hdfs.put(shop_list, hdfs_shop_list)
        except Exception as e:
            print('集群挂了', e)

if __name__ == '__main__':
    cse = ctripShopExecute()
    cse.main()