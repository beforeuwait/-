# coding=utf8

__author__ = 'wangjiawei'
__date__ = '2018-03-15'

"""
    作为模拟抓取平台的引擎，负责分发任务
    思路：
        列表：每个分类生成的店铺数据url，然后抓取，因此在slave部分需要一个控制页数的判断
        详情：无论是正常访问还是selenium，都是针对已有id生成全部url
        评论：同列表思路类似，在slave部分需要一个流程来判断
    
"""

import json
from order import CATEGORY

# todo: 列表的引擎

class shop_list_engine():
    """生成一个待抓取列表，页数由slave去控制
    格式:json
    """
    def make_choice(self, prov):
        """确定省份"""
        # prov = '四川'
        # 需要一个容器来接收指定的省份
        data = []
        # city_path = 'prov_city_area/dianping_city.txt'
        city_path = 'prov_city_area/city_region_info.txt'
        for each in (open(city_path, 'r', encoding='utf-8')):
            # js_dict = json.loads(each)
            js_dict = eval(each)
            if js_dict.get('prov') == prov:
                data.append(js_dict)
        return data

    def make_none_choice(self):
        """适用于全国的数据"""
        pass

    # todo:确定了省份后，然后需求分类，是美食还是娱乐
    def perference(self, choice):
        # choice = '美食'
        data = []
        for cate, code in CATEGORY.get(choice).items():
            data.append((cate, code, choice))
        return data

    # todo: 相继确认了省份，分类后，开始生成相应原始url，并放入队列(文件)
    def construct_url(self, city_list, cate_list):
        f = open('seed/shop_list.txt', 'w', encoding='utf8')
        for city in city_list:
            for each in cate_list:
                # 第一个城市，第二个分类，第三个行政区，第四个页数
                url = 'http://www.dianping.com/{0}/{1}{2}p'.format(city.get('cityEnName'), each[1], city.get('subAreaCode'))
                data = {
                    "method": "GET",
                    "region": city.get('region_info'),
                    "prov": city.get('prov'),
                    "city": city.get('cityName'),
                    "sub_area": city.get('subAreaName'),
                    "category": each[2],
                    "peference": each[0],
                    "topic": "dianping_food_list",
                    "url": url,
                    "domain": "dianping",
                    "referer": "http://www.dianping.com/{0}/{1}".format(city.get('cityEnName'), each[1]),
                }
                f.write(json.dumps(data))
                f.write('\n')
                del data
        f.close()


# todo: 商铺详情的引擎
class shop_info_engine():
    """依据列表生成一个待抓取的详情列表，然后交由slave去抓取
    格式:json
    """
    pass


# todo: 商铺评论的引擎
class shop_cmt_engine():
    """依据列表生成一个待抓取的详情列表，然后交由slave去抓取
    格式:json
    """
    pass


def main():
    sle = shop_list_engine()
    prov = '重庆'
    choice = '美食'
    city_list = sle.make_choice(prov)
    cate_list = sle.perference(choice)
    sle.construct_url(city_list, cate_list)


if __name__ == '__main__':
    main()
    for i in (open('seed/shop_list.txt')):
        print(json.loads(i))
        # print(i)