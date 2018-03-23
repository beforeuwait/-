# coding=utf8

"""
临时脚本，一次性脚本
"""
import requests
import time
from lxml import etree

cate = {
    "足疗按摩": "g141",
    "洗浴汗蒸": "g140",
    "KTV": "g135",
    "酒吧": "g133",
}

PROXIES = {
    "http": "http://HY3JE71Z6CDS782P:CE68530DAD880F3B@proxy.abuyun.com:9010",
    "https": "http://HY3JE71Z6CDS782P:CE68530DAD880F3B@proxy.abuyun.com:9010",
}

def list(cate_c, n):
    # cate_c = "长途汽车站"
    # area_c = "南市区"
    headers = {
        "Host": "www.dianping.com",
        "Referer": "http://www.dianping.com/fengjie/ch80",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
    }
    for i in range(n):
        url = "http://www.dianping.com/fengjie/ch80/{0}p".format(cate.get(cate_c))
        url = url + str(i + 1)
        print(url)
        # html = requests.get(url, headers=headers)
        html = requests.get(url, headers=headers, proxies=PROXIES)
        print(html.status_code)
        get_list(html.content.decode('utf8'), cate_c)
        time.sleep(2)

def get_list(html, cate_c):
    selector = etree.HTML(html)
    list = selector.xpath('//div[@id="shop-all-list"]/ul/li')
    for each in list:
        url = each.xpath('div[@class="txt"]/div[@class="tit"]/a/@href')[0]
        name = each.xpath('div[@class="txt"]/div[@class="tit"]/a/h4/text()')[0]
        id = url.split('/')[-1]
        print(name, id)
        text = '\u0001'.join([id, name, cate_c, 'CN', '重庆市', '重庆', '重庆市', '重庆', '奉节县', '奉节', ''])
        with open('entain_list_fengjie.txt', 'a', encoding='utf8') as f:
            f.write(text.replace('\n', '') + '\n')

if __name__ == '__main__':
    list('酒吧', 1)