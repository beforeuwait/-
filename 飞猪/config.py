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
    "cookie": "hng=CN%7Czh-CN%7CCNY%7C156;"
              " thw=cn;"
              " ali_apache_id=11.128.42.195.1506165836158.367209.4;"
              " cna=omZJEqUkxWICAXAsaqSn1mIS; miid=527679198965532911;"
              " UM_distinctid=15f6dcac8f7ba8-0d42b12b089e6c-31657c00-13c680-15f6dcac8f8e54;"
              " _tb_token_=E0wN36l01wNEBwN4pzUF;"
              "v=0;"
              " uc3=sg2=BYTq733WezLkM7zXHVQevL79zcUGDMO%2F9xxLimVbR4c%3D&nk2=AQH1FfwVeBpCU8A%3D&id2=VynOVuku3XDV&vt3="
              "F8dBzLKHdSJGBugrYH8%3D&lg2=W5iHLLyFOGW7aA%3D%3D; existShop=MTUwOTUwMTYyMg%3D%3D;"
              " uss=Vvrz%2FHSi59HdqFfu3SK3F0%2Fn7anDMqJYD%2FQ7aseyTWDPS3aEXtFxqnzrog%3D%3D;"
              " lgc=beforeuwait;"
              " tracknick=beforeuwait;"
              " cookie2=1a473cdad6796ac20cb933143379cff8;"
              " sg=t4e;"
              " cookie1=Vv9IQ5%2BKbs20nJ4RAK0TRc%2B6RhfoVlhcC4rRkQpoltg%3D;"
              " unb=457421924;"
              " skt=d4a742b2eead561b;"
              " t=e8b4d5b9fe24f7a4dc381101747811d1;"
              " _cc_=UtASsssmfA%3D%3D;"
              " tg=0;"
              " _l_g_=Ug%3D%3D;"
              " _nk_=beforeuwait;"
              " cookie17=VynOVuku3XDV;"
              " _mw_us_time_=1509501749259;"
              " uc1=cookie16=U%2BGCWk%2F74Mx5tgzv3dWpnhjPaQ%3D%3D&cookie21="
              "Vq8l%2BKCLjA%2Bl&cookie15=U%2BGCWk%2F75gdr5Q%3D%3D&existShop=false&pas=0&"
              "cookie14=UoTcBr1GxeNQNw%3D%3D&cart_m=0&tag=8&lng=zh_CN;"
              " mt=ci=1_1;"
              " isg=Amhox3PupfJ1t4lNUAoZJTqQOVC6Oc4NiPj9XyKZtuPWfQjnyqGcK_69AyN2"
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