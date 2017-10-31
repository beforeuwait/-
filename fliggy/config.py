"""
作为配置文件的存在
"""

import os

os.chdir(os.path.split(os.path.realpath(__file__))[0])

PATH = 'Data'
if not os.path.exists(PATH):
    os.mkdir(os.path.abspath(PATH))

LIST = 'DataList'
if not os.path.exists(LIST):
    os.mkdir(os.path.abspath(LIST))

# 请求头
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "authority": "hotel.fliggy.com",
    "method": "GET",
    "scheme": "https",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    # "Proxy-Switch-Ip": "yes",
}
COOKISE = {
    "cookie": "cna=omZJEqUkxWICAXAsaqSn1mIS;"
              " UM_distinctid=15f702fc1813cc-0d94376464443a-31657c00-13c680-15f702fc182221;"
              " chanelStat=\"NQ==\";"
              " chanelStatExpire=\"2017-11-03 10:12:57\";"
              " hng=CN%7Czh-CN%7CCNY%7C156;"
              " uc1=cookie16=W5iHLLyFPlMGbLDwA%2BdvAGZqLg%3D%3D&cookie21=VFC%2FuZ9ainBZ&cookie15="
              "WqG3DMC9VAQiUQ%3D%3D&existShop=false&pas=0&cookie14=UoTcBryi%2BzwP0g%3D%3D&tag=8&lng=zh_CN;"
              " tracknick=beforeuwait;"
              " _l_g_=Ug%3D%3D;"
              " unb=457421924;"
              " cookie1=Vv9IQ5%2BKbs20nJ4RAK0TRc%2B6RhfoVlhcC4rRkQpoltg%3D;"
              " login=true;"
              " cookie17=VynOVuku3XDV; cookie2=17ef7be0359cc3960d53263da0bbd37d;"
              " _nk_=beforeuwait; uss=ACPnWjQ0qcBI3wnJKY57Z3ujftjTCaLUuTDw85GSgNf01du4TDjsMWs4iA%3D%3D;"
              " sg=t4e;"
              " t=e8b4d5b9fe24f7a4dc381101747811d1;"
              " _tb_token_=LmTsp8m2Iw5QTtdJd3mU; JSESSIONID=D811181BFC08822148DFD067D027461F;"
              " CNZZDATA1253581663=281493417-1509415606-https%253A%252F%252Fwww.alitrip.com%252F%7C1509433228;"
              " isg=AnNzJizLLuKBbOK5zGejXEMHAnFdAAX85zEW3iUQbRLJJJLGq3pBuij2qGIx"
}



# URL
HOTEL_LIST_URL = 'https://hotel.fliggy.com/ajax/hotelList.htm'


# params
PARAMS_LIST = {
    "pageSize": 20,
    "currentPage": 1,
    # "totalItem": 15057,
    # "startRow": 0,
    # "endRow": 19,
    "city": "511324",
    # "tid": "null",
    # "market": "0",
    # "previousChannel": "",
    # "u": "null",
    "detailLinkCity": "511300",
    "cityName": "南充",
    "checkIn": "2017-11-03",
    "checkOut": "2017-11-04",
    # "browserUserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    # "userClientIp": "182.151.214.57",
    # "userSessionId": "omZJEqUkxWICAXAsaqSn1mIS",
    # "offset": 20,
    # "keywords": "null",
    # "priceRange": "R0",
    # "dangcis": "null",
    # "brands": "null",
    # "services": "null",
    # "order": "DEFAULT",
    # "dir": "DESC",
    # "client": "11.228.51.56",
    # "tagids": "null",
    # "searchPoiName": "undefined",
    # "pByRadiusLng": "-1",
    # "pByRadiusLat": "-1",
    # "radius": "-1",
    # "pByRectMinLat": "-1",
    # "pByRectMinLng": "-1",
    # "pByRectMaxLat": "-1",
    # "pByRectMaxLng": "-1",
    # "lowPrice": "-1",
    # "highPrice": "-1",
    # "filterByKezhan": "false",
    # "searchBy": "",
    # "searchByTb": "false",
    # "businessAreaId": "null",
    # "skipKeywords": "false",
    # "district": "null",
    # "backCash": "false",
    # "shids": "null",
    # "activity": "null",
    # "filterDoubleEleven": "false",
    # "filterByRoomTickets": "false",
    # "filterHxk": "false",
    # "filterCxk": "false",
    # "filterByRoomTicketsAndNeedLogin": "false",
    # "filterByRoomTicketsAndNeedBuyTicket": "false",
    # "activityCode": "null",
    # "searchId": "null",
    # "userId": "null",
    # "hotelTypes": "null",
    # "filterByB2g": "false",
    # "filterByAgreement": "false",
    # "bizNo": "null",
    # "bizType": "null",
    # "region": 0,
    # "newYearSpeOffer": "false",
    # "laterPay": "false",
    # "sellerId": "null",
    # "isMemberPrice": "false",
    # "isLaterPayActivity": "false",
    # "isFilterByTeHui": "false",
    # "keyWordsType": "",
    # "userUniqTag": "null",
    # "iniSearchKW": "false",
    # "poiNameFilter": "",
    # "isFreeCancel": "false",
    # "isInstantConfirm": "false",
    # "activityCodes": "",
    # "overseaMarket": "false",
    # "roomNum": 1,
    # "notFilterActivityCodeShotel": "false",
    # "poisearch": "false",
    # "adultChildrenCondition": "&roomNum=1&aNum_1=2&cNum_1=0",
    # "previousPage": 1,
    # "nextPage": 2,
    # "pageFirstItem": 1,
    # "firstPage": "true",
    # "lastPage": "false",
    # "totalPage": 753,
    # "pageLastItem": 20,
    # "aNum_1": 2,
    # "cNum_1": 0,
    # "cAge_1_1": 0,
    # "cAge_1_2": 0,
    # "cAge_1_3": 0,
    # "_input_charset": "utf-8",
    # "laterPaySwitch": "",
    # "_ksTS": "1509416502865_3007",
    # "callback": "jsonp3008",
}

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