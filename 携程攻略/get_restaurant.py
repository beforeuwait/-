__author__ = 'Wang Jia Wei'

"""
这个脚本作为携程攻略中各旅游目的的餐馆的采集脚本
"""

import requests
import json
from faker import Faker
import multiprocessing
from lxml import etree

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
            print(each)
            self.shop_list_logic(each)
            # pool.apply_async()
            break
        # pool.close()
        # pool.join()

    def shop_list_logic(self, info):
        page, next_page = 1, True
        while next_page:
            html = self.down.shop_list(info[-1], page)
            shop_list = self.spider.shop_list(html) if html is not 'bad_requests' else []
            next_page = True if not shop_list == [] else False
            if next_page:
                self.pipe.save_shop_list(info, shop_list)
            page += 1
            break

    def shop_info_pid(self):
        """
        1. 再获取列表后，获取每个商铺的详情
        2. 同时获取pid，为评论的抓取做准备
        3. 这里暴露一个问题就是，必须在获取详情后才能拿到pid
        """
        shop_list = (i.strip().split(setting.blank)for i in open(setting.restaurant_list, 'r', encoding=setting.encode))
        for each in shop_list:
            print(each)

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
            retry -= 1
        return response

    def shop_list(self, city_id, page):
        url = setting.shop_list_url %(city_id, page)
        headers = setting.headers
        html = self.do_get_requests(url, headers)
        return html

class ctripShopSpider:
    def shop_list(self, html):
        selector = etree.HTML(html)
        shop_list = selector.xpath('//div[@class="list_wide_mod2"]/div[@class="list_mod2"]')
        data = []
        for each in shop_list:
            id = each.xpath('div[@class="abiconbox"]/@data-id')[0] if each.xpath('div[@class="abiconbox"]/@data-id') else ''
            name = each.xpath('div[@class="rdetailbox"]/dl/dt/a/@title')[0] if each.xpath('div[@class="rdetailbox"]/dl/dt/a/@title') else ''
            address = each.xpath('div[@class="rdetailbox"]/dl/dd[1]/text()')[0]if each.xpath('div[@class="rdetailbox"]/dl/dd[1]/text()')else ''
            average = each.xpath('div[@class="rdetailbox"]/dl/dd[2]/span/text()')[0]if each.xpath('div[@class="rdetailbox"]/dl/dd[2]/span/text()')else ''
            data.append([id, name, address, average])
        return data

class ctripShopPipeline:

    def save_shop_list(self, info, data):
        text = ''
        info.pop(-1)
        city = info
        for each in data:
            context = setting.blank.join(city)
            text += context + setting.blank + setting.blank.join(each) + '\n'
        with open(setting.restaurant_list, 'a', encoding=setting.encode) as f:
            f.write(text)

class setting:
    """
    这个类作为引入config.py里的参数并提供给这个脚本里使用
    """
    import config

    blank = config.BLANK

    encode = config.ENCODING

    proxy = config.get_proxy()

    city_list = config.CITY_LIST

    shop_list_url = 'http://you.ctrip.com/restaurantlist/%s/s0-p%s.html'

    restaurant_list = config.RESTAURANT_SHOP_LIST

    restaurant_info = config.RESTAURANT_SHOP_INFO

    headers = config.HEADERS

    headers_xml = config.HEADERS_XML

class ctripShopExecute:
    pass

if __name__ == '__main__':
    cse = ctripShopEngine()
    cse.shop_list()
    # cse.shop_info_pid()