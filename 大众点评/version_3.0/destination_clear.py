from __future__ import absolute_import
__author__ = 'wangjiawei'
__date__ = '2018-03-14'
"""
说明：这是地域清洗脚本，从json格式中提取数据，将每个省，每个市的数据输出，并放入json文件里
格式：{ 省:xx, 省id:xx,城市:xx, 城市cne: xx}
问题：这里只到二级，那么来说，三级更低，需要更进一步来清洗.
"""

import json
import time
import requests
from lxml import etree

# todo: 处理原始的json，将各省各城进行分类
def get_all_cities():
    json_text = open('prov_city_area/origin_provs_json.txt', 'r').read()
    json_dict = json.loads(json_text)
    # 先将各省放入一个字典里 格式{'1': '北京'}
    provs = {}
    for each in json_dict.get('provinceList'):
        provs[each.get('provinceId')] = each.get('provinceName')
    
    # 开始匹配城市
    all_cities = []
    cities_dict = json_dict.get('cityMap')
    for pid, pname in provs.items():
        city_list = cities_dict[pid]
        for each in city_list:
            cityAreaCode = each.get('cityAreaCode', '')
            cityEnName = each.get('cityEnName', '')
            cityId = each.get('cityId', '')
            cityName = each.get('cityName', '')
            cityOrderId = each.get('cityOrderId', '')
            parentCityId = each.get('parentCityId', '')
            all_cities.append({'prov': pname, 'cityName': cityName, 'cityEnName': cityEnName,
                            'cityId': cityId, 'cityAreaCode': cityAreaCode,
                             'cityOrderId': cityOrderId, 'parentCityId': parentCityId})
        
    result = json.dumps(all_cities)
    with open('prov_city_area/all_citys_1.txt', 'a', encoding='utf8') as f:
        f.write(result)

# todo:针对已有城市列表中，存在parent city字段，进行二次清洗
def get_all_city_parent():
    city_list = json.loads(open('prov_city_area/all_citys_1.txt', 'r').read())
    # 先获取一个集合 城市, 城市id
    city_id_list = {}
    for each in city_list:
        city_id_list[each.get('cityId')] = each.get('cityName')
    # 开始清洗
    for each in city_list:
        each['parentCity'] = city_id_list.get(each.get('parentCityId', 'none'), 'none')
    
    result = json.dumps(city_list)
    with open('prov_city_area/all_citys_2.txt', 'w', encoding='utf8') as f:
        f.write(result)

# todo: 针对第二次清洗，再次为每个二级市匹配三级或者更多
def clear_2nd():
    """当前遇到的难题有：
    1，可能会重复抓取的情况，就是列表里出现的三级城市，而抓取还会再抓一次，这里需要清理
    2，针对第一条，只挑选出parentCity为none 的，然后筛选子类
    """
    city_list = json.loads(open('prov_city_area/all_citys_2.txt', 'r').read())
    # 1. 统计出parentCity是none的，确定待抓取序列
    city_without_dad = []
    for city in city_list:
        if city.get('parentCity') == 'none':
            city_without_dad.append(city)
    # 2.保存待抓取序列，city_ready_2_crawl.txt
    result = json.dumps(city_without_dad)
    with open('prov_city_area/city_ready_2_crawl.txt', 'w', encoding='utf8') as f:
        f.write(result)

# TODO: 下午需要解决的是，请求网址，然后拿到每个行政区数据
HEADERS = {
    "Host": "www.dianping.com",
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"),
    }
COOKIES = {
    "Cookie": ("showNav=javascript:;"
               "navCtgScroll=0;"
               "navCtgScroll=0;"
               "showNav=#nav-tab|0|1;"
               " _lxsdk_cuid=161bc37672fc8-01d3f62a97e012-32687a04-13c680-161bc37672fc8;"
               "_lxsdk=161bc37672fc8-01d3f62a97e012-32687a04-13c680-161bc37672fc8;"
               "_hc.v=59decaa2-84aa-e238-6da0-49c0bbf865c0.1519281203;"
               "s_ViewType=10;dper=9b5ba8ba8fb7338106d7db259d132cf99f1c4f7f1807e94bea6e9fcda606c0b6;ua=18582389107;"
               "ctu=06936018815a622639a414e01836cb531dc3092e5e853dc9b35845d6e3c87db5;"
               "cityid=1;"
               "default_ab=shop%3AA%3A1%7Cindex%3AA%3A1%7CshopList%3AA%3A1%7Cshopreviewlist%3AA%3A1%7Csinglereview%3AA%3A1;"
               "ll=7fd06e815b796be3df069dec7836c3df;"
               "cy=8;"
               "cye=chengdu;"
               "_lxsdk_s=162230cf5a0-69d-49-e8b%7C%7C29")
    }

# todo: 完成全国城市列表的获取
def get_sub_destation():
    """请求一个固定的网址，从而获取全部的城市的下一级
    """
    # 仍旧是先获取列表
    f = open('prov_city_area/dianping_city.txt', 'a', encoding='utf8')
    n = 1
    for city in json.loads(open('prov_city_area/city_ready_2_crawl.txt', 'r').read()):
        print(n)
        if n > 3:
            city.pop('parentCityId')
            city.pop('parentCity')
            url = 'http://www.dianping.com/{0}/ch10'
            response = requests.get(url.format(city.get('cityEnName')), headers=HEADERS, cookies=COOKIES)
            selector = etree.HTML(response.content.decode('utf8'))
            sub_list = selector.xpath('//div[@id="region-nav"]/a')
            for area in sub_list:
                url = area.xpath('@href')
                sub_area = area.xpath('@data-click-title')[0]
                # 开始清洗
                if url:
                    sub_area_id = url[0].split('/')[-1]
                    city['subAreaName'] = sub_area
                    city['subAreaCode'] = sub_area_id
                    f.write(json.dumps(city))
                    f.write('\n')
            time.sleep(10)
        n += 1
    f.close()


if __name__ == '__main__':
    """
    各个步骤相对独立，自由选择
    """
    # 第一步清洗
    get_all_cities()
    # 第二步清洗
    get_all_city_parent()
    # 第三步清洗
    clear_2nd()
    # 最后一步
    get_sub_destation()
