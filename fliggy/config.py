"""
作为配置文件的存在
"""

import os

os.chdir(os.path.split(os.path.realpath(__file__))[0])

COMMEND = 'all'


PATH = 'Data'
if not os.path.exists(PATH):
    os.mkdir(os.path.abspath(PATH))

LIST = 'DataList'
if not os.path.exists(LIST):
    os.mkdir(os.path.abspath(LIST))

# 文件路径
ALL_AREA = os.path.join(os.path.abspath(LIST), 'city_list_total.txt')

HOTEL_LIST = os.path.join(os.path.abspath(LIST), 'fliggy_hotel_list.txt')
if not os.path.exists(HOTEL_LIST):
    f = open(HOTEL_LIST, 'w+')
    f.close()

HOTEL_LIST_AREA_ALREADY = os.path.join(os.path.abspath(LIST), 'hotel_list_area_already.txt')
if not os.path.exists(HOTEL_LIST_AREA_ALREADY):
    f = open(HOTEL_LIST_AREA_ALREADY, 'w+')
    f.close()

HOTEL_INFO = os.path.join(os.path.abspath(PATH), 'fliggy_hotel_info.txt')
if not os.path.exists(HOTEL_INFO):
    f = open(HOTEL_INFO, 'w+')
    f.close()

HOTEL_INFO_EX = os.path.join(os.path.abspath(PATH), 'hotel_info_ex.txt')
if not os.path.exists(HOTEL_INFO_EX):
    f = open(HOTEL_INFO_EX, 'w+')
    f.close()


# 请求头
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "authority": "hotel.fliggy.com",
    "method": "GET",
    "scheme": "https",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
}

# cookies
COOKISE = {
    "cookie": ""
}



# URL
HOTEL_LIST_URL = 'https://hotel.fliggy.com/ajax/hotelList.htm'

HOTEL_INFO_URL = 'https://hotel.fliggy.com/hotel_detail2.htm'

# params
PARAMS_LIST = {
    "pageSize": 20,
    "currentPage": 1,
    "city": "511324",
    "detailLinkCity": "511300",
    "cityName": "南充",
    "checkIn": "2017-11-03",
    "checkOut": "2017-11-04",
}

PARAMS_INFO = {
    "shid": "10089487"
}

# Data

HOTEL_DICT = {
    "中文全称": "",
    "中文简称": "",
    "所属地区": "",
    "地址": "",
    "地理位置": "",
    "等级": "",
    "类型": "",
    "开业时间": "",
    "最后一次装修时间": "",
    "最早入住时间": "",
    "最晚离店时间": "",
    "总客房数": "",
    "总床位数": "",
    "咨询电话": "",
    "传真": "",
    "邮政编码": "",
    "投诉电话": "",
    "交通信息": "",
    "周边信息": "",
    "简介": "",
    "国别": "CN",
    "省全称": "",
    "省简称": "",
    "市全称": "",
    "市简称": "",
    "县全称": "",
    "县简称": "",
    "行政区号": "",
    "url": "",
}
HOTEL_DICT_L = [
    "中文全称", "中文简称", "所属地区", "地址", "地理位置", "等级", "类型", "开业时间", "最后一次装修时间", "最早入住时间",
    "最晚离店时间", "总客房数", "总床位数", "咨询电话", "传真", "邮政编码", "投诉电话", "交通信息", "周边信息", "简介",
    "国别", "省全称", "省简称", "市全称", "市简称", "县全称", "县简称", "行政区号", "url",
]
# setting

BLANK = '\u0001'

ENCODING = 'utf-8'

DELAY = 5