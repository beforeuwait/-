'''
单纯用来获取地区，并做数据清洗
当前只需要 四川， 新疆
同时获取每个行政区

2017-11-27 修改逻辑
'''
import requests
import re
import time
import copy
import config
from lxml import etree

quanguo_url = 'http://www.dianping.com/citylistguonei'
headers = {
    'Host': 'www.dianping.com',
    'Referer': 'http://www.dianping.com/chengdu/food',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
}


def get_cities(*args):
    html = requests.get(quanguo_url, headers=headers).content.decode('utf8')
    selector = etree.HTML(html)
    data = []
    for each in args:
        cons = selector.xpath('//dl[@class="terms"]')
        for i in cons:
            if i.xpath('dt/text()')[0] == each:
                for city in i.xpath('dd/a'):
                    name = city.xpath('strong/text()')[0]
                    cnc = city.xpath('@href')[0].replace('food', '')
                    data.append([each, name, cnc])
    return data


def clear_data(data):
    params = {
        '国别': 'CN',
        '省全称': '&',
        '省简称': '&',
        '市全称': '&',
        '市简称': '&',
        '县全称': '&',
        '县简称': '&',
        '行政区代码': '&',
        'cnc': '&',
        'cityid': '&',
        'sub_area': '&'}
    city_list = []
    for each in data:
        for i in [i.strip().split('\u0001')
                  for i in open('city_list_total.txt', 'r', encoding='utf8')]:
            if each[0] in i and each[1] in i:
                count = i.index(each[1])
                if count == 2 or count == 3:
                    params['省全称'] = i[0]
                    params['省简称'] = i[1]
                    params['市全称'] = i[2]
                    params['市简称'] = i[3]
                    params['cnc'] = each[2]
                    params['行政区代码'] = re.findall('\d\d\d\d', i[-1])[0] + '00'
                else:
                    params['省全称'] = i[0]
                    params['省简称'] = i[1]
                    params['市全称'] = i[2]
                    params['市简称'] = i[3]
                    params['县全称'] = i[5]
                    params['县简称'] = i[4]
                    params['行政区代码'] = i[-1]
                    params['cnc'] = each[2]
                city_list.append(params)    # 字典放在列表里
                params = {
                    '国别': 'CN',
                    '省全称': '&',
                    '省简称': '&',
                    '市全称': '&',
                    '市简称': '&',
                    '县全称': '&',
                    '县简称': '&',
                    '行政区代码': '&',
                    'cnc': '&',
                    'cityid': '&',
                    'sub_area': '&'}
                break
    return city_list


def get_cityId(city_list):
    for each in city_list:
        url = 'http:%s'
        # print(url % each['cnc'])
        time.sleep(0.1)
        html = requests.get(
            url %each['cnc'],
            headers=headers,
            timeout=30).content.decode('utf8')

        # 这里需要的逻辑，只获取当前id
        selector = etree.HTML(html)
        url = selector.xpath(
            '//div[@class="groups"]/div[1]/div[@class="sec-items"]/a[1]/@href')
        if url:
            cityId = url[0].split('/')[-3]
            each['cityid'] = cityId
        else:
            cityId = re.findall('_setCityId\', (\d{1,6})', html, re.S)[0]
            each['cityid'] = cityId
    return city_list


def get_sub_area(total_list):
    '''这里的逻辑就是，给地级市加上行政区，对于已存在的行政区就加上sub_area'''
    sub_area_list = []
    for i in total_list:
        if i['县全称'] == '&':
            url = 'http://www.dianping.com/search/category/%s/10/g110' % i['cityid']
            time.sleep(0.1)
            html = requests.get(url, headers=headers).content.decode('utf8')
            selector = etree.HTML(html)
            cons = selector.xpath('//div[@id="J_nt_items"]/div[2]/a')
            for each in cons:
                name = each.xpath('span/text()')[0]
                sub_area = each.xpath('@href')[0].split(
                    '/')[-1].replace('g110', '')
                sub_area_list.append(
                    [i['市全称'], name, sub_area, i['cityid'], 0])

    new_list = []
    for i in sub_area_list:
        for each in total_list:
            if i[0] in each.values() and i[1] in each.values():
                each['sub_area'] = i[2]
                each['cityid'] = i[3]
                i[4] = 1
                # 这里需要一个做行政区处理的逻辑
                for t in [
                    i.strip().split('\u0001') for i in open(
                        'city_list_total.txt',
                        'r',
                        encoding='utf8')]:
                    if i[0] in t and i[1] in t:
                        each['行政区代码'] = t[-1]
                        break
                new_list.append(each)
                break
        if i[4] == 0:   # 这才是没处理的
            for each in total_list:
                if i[0] in each.values() and each['县全称'] == '&':
                    temp = copy.deepcopy(each)
                    temp['县全称'] = i[1]
                    temp['sub_area'] = i[2]
                    temp['cityid'] = i[3]
                    # 这里需要添加的逻辑就是 要做一个行政区code的判断
                    for t in [
                        i.strip().split('\u0001') for i in open(
                            'city_list_total.txt',
                            'r',
                            encoding='utf8')]:
                        if i[0] in t and i[1] in t:
                            temp['行政区代码'] = t[-1]
                            break
                    new_list.append(temp)
                    break

    # f = open('provs_city_code.txt', 'a', encoding='utf8')
    f = open(config.AREA_FILE, 'a', encoding='utf8')
    for each in new_list:
        t = ''
        for i in each.values():
            t += i + '\u0001'
        f.write(t.replace('&', '') + '\n')
    f.close()


def execute(*args):
    # 先清洗
    f = open(config.AREA_FILE, 'w+', encoding='utf8')
    f.close()

    data = get_cities(*args)
    # 第二步，匹配县市区
    city_list = clear_data(data)
    # # 第三步，给二级市匹配cityId
    total_list = get_cityId(city_list)
    # # 第四步，给二级市匹配行政区
    get_sub_area(total_list)


if __name__ == '__main__':
    execute('新疆')
