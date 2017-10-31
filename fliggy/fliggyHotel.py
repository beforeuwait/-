__author__ = "Wang Jia Wei"

"""
该脚本为 飞猪旅行 中的酒店脚本
1。获取指定省份各城市的酒店目录
2。获取酒店的评论

调研：
1。注意人家的反爬虫策略
2。首先通过各地行政区编码，获取该地的酒店数量
3。再是构造请求获取酒店列表，列表中酒店数据就较为全面了

日志：
2017-10-31： 开始开发脚本，将 requests 模块分离出来

"""

import requestModel
import config
import requests
import json

class figgyHotelEngine:
    def test_modle(self):
        url = config.HOTEL_LIST_URL
        headers = config.HEADERS
        params = config.PARAMS_LIST
        # response = requests.get(url, headers=headers, params=params, cookies=config.COOKISE, proxies=config.get_proxy())
        response = requests.get(url, headers=headers, params=params, cookies=config.COOKISE)
        print(response.status_code)
        print(response.content.decode('gbk'))
        js_dict = json.loads(response.text)
        cons = js_dict.get('hotelList', '')
        for each in cons:
            print(each)

class figgyHotelSpider:
    pass

class figgyHotelPipeline:
    pass

class setting:
    pass

if __name__ == '__main__':
    fhe = figgyHotelEngine()
    fhe.test_modle()