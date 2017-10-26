'''作为配置文件的存在'''

import os

os.chdir(os.path.split(os.path.realpath(__file__))[0])

PATH = 'Data'
if not os.path.exists(PATH):
    os.mkdir(os.path.abspath(PATH))

TEMP = 'DataTemp'
if not os.path.exists(TEMP):
    os.mkdir(os.path.abspath(TEMP))

LIST = 'DataList'
if not os.path.exists(LIST):
    os.mkdir(os.path.abspath(LIST))

ALL_CITY_LIST = os.path.join(os.path.abspath(LIST), 'city_list_total.txt')

#

CITY_LIST = os.path.join(os.path.abspath(LIST), 'city_list.txt')    # 城市列表

PROVS_LIST = os.path.join(os.path.abspath(TEMP), 'provs_list.txt')  # 临时的省份列表


RESTAURANT_SHOP_LIST = os.path.join(os.path.abspath(PATH), 'restaurant_shop_list.txt')

RESTAURANT_SHOP_INFO = os.path.join(os.path.abspath(PATH), 'restaurant_shop_info.txt')

# 代理

def get_proxy():
    # 要访问的目标页面
    # targetUrl = "http://test.abuyun.com/proxy.php"
    # 代理服务器
    proxyHost = "proxy.abuyun.com"
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

# 编码
BLANK = '\u0001'
ENCODING = 'utf-8'

# 请求头
HEADERS = {
    "Host": "you.ctrip.com",
    "Proxy-Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
}
HEADERS_XML = {
    "X-Requested-With": "XMLHttpRequest",
    "Host": "you.ctrip.com",
    "Proxy-Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
}


# 因为评论不做天更新的，因此，评论获取指定的一段时间内的全部评论
CMT_START_DATE = '2012-01-01'
CMT_START_END = '2017-10-25'