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