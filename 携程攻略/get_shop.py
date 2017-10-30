__author__ = 'Wang Jia Wei'

"""
这个脚本作为携程攻略中各旅游目的的餐馆的采集脚本
记录：
2017-10-27： 为二级市添加行政区，不然，数据少的可怜,这个模块放在get_area.py中了
"""

import requests
import re
import config
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
        获取携程攻略各目的地的商铺列表，这个就需要说明的一点：
        一个城市没有分页，一次性采集完
        """
        # pool = multiprocessing.Pool(2)
        city_list = (i.strip().split(setting.blank) for i in open(setting.city_list, 'r', encoding=setting.encode)) # 获取已抓取的城市列表
        for each in city_list:
            """
            每一次新抓取一个城市或者区，都要对列表里对城市集合进行一次迭代，确保不会重复抓取，
            但是可能造成对结果就是如果一个城市抓取过程中出错，断电启动后，将不会再次抓取该城市
            """
            shop_list_ex = set(i.strip() for i in open(setting.shopping_list_ex, 'r', encoding=setting.encode))  # 城市集合
            if each[-2] not in shop_list_ex:
                self.shop_list_logic(each)
                self.pipe.save_city_already(each[-2])
            # pool.apply_async(self.shop_list, (each,))
        # pool.close()
        # pool.join()

    def shop_list_logic(self, info):
        page, next_page = 1, True
        while next_page:
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
        # pool = multiprocessing.Pool(2)
        shop_ex_set = set(i.strip().split(setting.blank)[-1]for i in open(setting.shopping_ex, 'r', encoding=setting.encode))
        shop_list = (i.strip().split(setting.blank)for i in open(setting.shopping_list, 'r', encoding=setting.encode))
        for each in shop_list:
            if each[-4] not in shop_ex_set:
                self.shop_info_pid_logic(each)
                # pool.apply_async(self.shop_info_pid_logic, (each,))
        # pool.close()
        # pool.join()

    def shop_info_pid_logic(self, info):
        """
        这里要做的是获取每个商铺详细信息，保存，同时保存一份已保存目录并添加pid字段，评论从已获取中提取商铺id以及pid
        :param info: 列表信息
        :return:
        """
        html = self.down.shop_info_pid(info[-1])
        data = self.spider.shop_info_pid(html) if html is not 'bad_requests' else []
        self.pipe.save_shop_info_pid(data, info) if data[0] is not '0' else ''

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

    def shop_info_pid(self, link):
        url = setting.local_url % link
        headers = setting.headers
        html = self.do_get_requests(url, headers)
        return html

    def shop_list_area(self, city_id, area_id, page):
        url = setting.shop_list_url_area %(city_id, area_id, page)
        print(url)
        headers = setting.headers
        html = self.do_get_requests(url, headers)
        return html

class ctripShopSpider:
    def shop_list(self, html):
        """
        针对购物这个脚本的spider
        """

        selector = etree.HTML(html)
        shop_list = selector.xpath('//div[@class="list_wide_mod2"]/div[@class="list_mod2"]')
        data = []
        for each in shop_list:
            name = each.xpath('div[@class="rdetailbox"]/dl/dt/a/@title')[0] \
                if each.xpath('div[@class="rdetailbox"]/dl/dt/a/@title') \
                else ''
            address = each.xpath('div[@class="rdetailbox"]/dl/dd[1]/text()')[0] \
                if each.xpath('div[@class="rdetailbox"]/dl/dd[1]/text()') \
                else ''
            url = each.xpath('div[@class="rdetailbox"]/dl/dt/a/@href')[0] \
                if each.xpath('div[@class="rdetailbox"]/dl/dt/a/@href') \
                else ''
            data.append([name, address, url])
        return data

    def shop_info_pid(self, html):
        data = []
        city_id = re.findall('var districtid = "(.*?)";', html)[0] if re.findall('var districtid = "(.*?)";', html) else '0'
        data.append(city_id)
        pid = re.findall('var poiid = "(.*?)";', html)[0] if re.findall('var poiid = "(.*?)";', html) else '0'
        data.append(pid)
        city_cnc = re.findall('var districtename = "(.*?)";', html)[0] if re.findall('var districtename = "(.*?)";', html) else ''
        data.append(city_cnc)
        selector = etree.HTML(html)
        categoty = selector.xpath('//div[@class="des_narrow f_right"]/div[@class="s_sight_infor"]/ul/li[2]/span[2]/a/text()')[0]\
            if selector.xpath('//div[@class="des_narrow f_right"]/div[@class="s_sight_infor"]/ul/li[2]/span[2]/a/text()')\
            else ''
        data.append(categoty)
        address = selector.xpath('//div[@class="des_narrow f_right"]/div[@class="s_sight_infor"]/ul/li[1]/span[2]/text()')[0]\
            if selector.xpath('//div[@class="des_narrow f_right"]/div[@class="s_sight_infor"]/ul/li[1]/span[2]/text()')\
            else ''
        data.append(address)
        tel = selector.xpath('//div[@class="des_narrow f_right"]/div[@class="s_sight_infor"]/ul/li[3]/span[2]/text()')[0]\
            if selector.xpath('//div[@class="des_narrow f_right"]/div[@class="s_sight_infor"]/ul/li[3]/span[2]/text()')\
            else ''
        data.append(tel)
        opentime = selector.xpath('//div[@class="des_narrow f_right"]/div[@class="s_sight_infor"]/dl/dd/text()')[0]\
            if selector.xpath('//div[@class="des_narrow f_right"]/div[@class="s_sight_infor"]/dl/dd/text()')\
            else ''
        data.append(opentime)
        descriptation = selector.xpath('//div[@itemprop="description"]')[0].xpath('string(.)')
        data.append(descriptation)
        products = ','.join(selector.xpath('//div[@class="card_list product_card"]/ul/li/dl/dt/text()'))
        data.append(products)
        try:
            trans = selector.xpath('//div[@class="toggle_s"]/div[@class="text_style"]/div/text()')[1] \
                if selector.xpath('//div[@class="toggle_s"]/div[@class="text_style"]/div/text()') \
                else ''
        except:
            trans = ''
        # city_id, pid, city_cnc, category, address, tel, opentime, descriptation,products,trans
        data.append(trans)
        return data


class ctripShopPipeline:

    def save_city_already(self, city_cnc):
        with open(setting.shopping_list_ex, 'a', encoding=setting.encode) as f:
            f.write(city_cnc + '\n')

    def save_shop_list(self, info, data):
        text = ''
        for each in data:
            context = setting.blank.join(info)
            id = each[-1].split('/')[-1].replace('.html', '')
            text += context + setting.blank + id + setting.blank + setting.blank.join(each).replace('\r', '').\
                replace('\n', '').replace(' ', '') + '\n'
        with open(setting.shopping_list, 'a', encoding=setting.encode) as f:
            f.write(text)

    def save_shop_info_pid(self, data, shop_info):
        info = setting.shopping_dict
        info_l = setting.shopping_dict_l
        info['中文全称'] = shop_info[-3]
        info['所属地区'] = shop_info[2]
        info['地址'] = shop_info[-2]
        info['类型'] = data[3]
        info['营业时间'] = data[6]
        info['特色商品'] = data[-2]
        info['咨询电话'] = data[5]
        info['交通信息'] = data[-1]
        info['简介'] = data[-3]
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
        # text_ex 存储对字段有 pid，city_cne, city_id, shop_id,
        text_ex = setting.blank.join([data[1], data[2], data[0], shop_info[-4]]) + '\n'

        with open(setting.shopping_info, 'a', encoding=setting.encode) as f:
            f.write(text)

        with open(setting.shopping_ex, 'a', encoding=setting.encode) as f:
            f.write(text_ex)

class setting:
    """
    这个类作为引入config.py里的参数并提供给这个脚本里使用
    """

    blank = config.BLANK

    encode = config.ENCODING

    proxy = config.get_proxy()

    city_list = config.CITY_LIST

    shop_list_url = 'http://you.ctrip.com/shoppinglist/%s/s0-p%s.html'

    shop_list_url_area = 'http://you.ctrip.com/shoppinglist/%s/s0-r%s-p%s.html'

    local_url = 'http://you.ctrip.com%s'

    shopping_list = config.SHOPPING_SHOP_LIST

    shopping_list_ex = config.SHOPPING_SHOP_LIST_EX

    shopping_info = config.SHOPPING_SHOP_INFO

    shopping_ex = config.SHOPPING_SHOP_EX

    shopping_dict = config.SHOPPING_DICT

    shopping_dict_l = config.SHOPPING_DICT_L

    headers = config.HEADERS

    headers_xml = config.HEADERS_XML

class ctripShopExecute:
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

if __name__ == '__main__':
    cse = ctripShopExecute(config.SHOPPING_COMMAND)
    cse.execute()