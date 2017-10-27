'''作为配置文件的存在'''

import os

os.chdir(os.path.split(os.path.realpath(__file__))[0])

# 命令
RESTAURANT_COMMAND = 'all'

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
if not os.path.exists(CITY_LIST):
    f = open(CITY_LIST)
    f.close()

PROVS_LIST = os.path.join(os.path.abspath(TEMP), 'provs_list.txt')  # 临时的省份列表
if not os.path.exists(PROVS_LIST):
    f = open(PROVS_LIST)
    f.close()

RESTAURANT_SHOP_LIST = os.path.join(os.path.abspath(PATH), 'restaurant_shop_list.txt')
if not os.path.exists(RESTAURANT_SHOP_LIST):
    f = open(RESTAURANT_SHOP_LIST)
    f.close()

RESTAURANT_SHOP_INFO = os.path.join(os.path.abspath(PATH), 'restaurant_shop_info.txt')
if not os.path.exists(RESTAURANT_SHOP_INFO):
    f = open(RESTAURANT_SHOP_INFO)
    f.close()


RESTAURANT_SHOP_EX = os.path.join(os.path.abspath(PATH), 'restaurant_shop_ex.txt') # 记录已抓取目录已经pid
if not os.path.exists(RESTAURANT_SHOP_EX):
    f = open(RESTAURANT_SHOP_EX)
    f.close()
    
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

# 字段，类似scrapy里的item

RESTAURANT_DICT = {
    "中文全称": "",
    "中文简称": "",
    "所属地区": "",
    "地址": "",
    "地理位置": "",
    "类型": "",
    "等级": "",
    "营业时间": "",
    "人均消费": "",
    "特色菜品": "",
    "咨询电话": "",
    "传真": "",
    "邮政编码": "",
    "投诉电话": "",
    "交通信息": "",
    "周边信息": "",
    "简介": "",
    "国别": "CN",
    "省自治区全称": "",
    "省自治区简称": "",
    "市州全称": "",
    "市州简称": "",
    "区县全称": "",
    "区县简称": "",
    "地区编码": "",
    "url": "",
}
RESTAURANT_DICT_L = [
    "中文全称", "中文简称", "所属地区", "地址", "地理位置", "类型", "等级", "营业时间", "人均消费",
    "特色菜品", "咨询电话", "传真", "邮政编码", "投诉电话", "交通信息", "周边信息", "简介", "国别",
    "省自治区全称", "省自治区简称", "市州全称", "市州简称", "区县全称", "区县简称", "地区编码", "url"
]
