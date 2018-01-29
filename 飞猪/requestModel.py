"""
这个最为请求模块
当前仍按照之前的思路开发此模块
"""

import requests
import time
import config
import datetime
from faker import Faker


class requestModel:
    def __init__(self) -> None:
        super().__init__()

    def do_get_requests(self, *args):
        retry = 3
        response = 'bad_requests'
        while retry > 0:
            args[1]['User-Agent'] = Faker().user_agent()
            try:
                res = requests.get(args[0], headers=args[1], timeout=30) \
                    if len(args) == 2 \
                    else requests.get(args[0], headers=args[1], params=args[2], timeout=30)
                if repr(res.status_code).startswith('2'):
                    try:
                        response = res.content.decode(config.ENCODING)
                    except:
                        response = res.text
                    break
            except Exception as e:
                print('GET请求过程中出错', e)
            retry -= 1
        return response

    def hotel_list(self, *args):
        url = config.HOTEL_LIST_URL
        params = config.PARAMS_LIST
        params['cityName'] = args[0]
        params['city'] = args[1]
        params['detailLinkCity'] = args[2]
        params['checkIn'] = (datetime.datetime.today() + datetime.timedelta(days=2)).strftime('%Y-%m-%d')
        params['checkOut'] = (datetime.datetime.today() + datetime.timedelta(days=3)).strftime('%Y-%m-%d')
        params['currentPage'] = args[3]
        headers = config.HEADERS
        html = self.do_get_requests(url, headers, params)
        return html

    def hotel_info(self, hotel_id):
        url = config.HOTEL_INFO_URL
        params = config.PARAMS_INFO
        params['shid'] = hotel_id
        headers = config.HEADERS
        headers['path'] = '/hotel_detail2.htm?shid=%s' %hotel_id
        html = self.do_get_requests(url, headers, params)
        return html