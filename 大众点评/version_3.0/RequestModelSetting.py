# coding=utf8

"""
RequestModel的配置文件
author: wangjiawie
date: 2018-03-29

使用说明:

虽然该model是大众点评的，但我是按照通用的来编写
包涵每个模块请求过程中，所需要的参数
每增加一个项目，需要手动在配置文件中添加相应的数据
"""

# 请求头

BASE_HEADERS = {
    "base": {
            'Accept': 'text/html,application/xhtml+xml,application/xml,application/json;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',  # 告诉服务器，可以将自己的http请求升级到 https

            },
    "xml": {
        "X-Requested-With": "XMLHttpRequest",
            },
    "jsml": {
        "X-Request": "JSON",
            },
}

# 需要手动去添加

HEADERS_HOST = {
    "dzdp": "www.dianping.com",     # 大众点评

}




# todo: 构造一个大众点评列表的请求头

def construct_headers(seed='dzdp'):
    """为大众点评构造一个请求头，找找思路"""
    headers = {}
    # 导入base
    headers.update(BASE_HEADERS.get('base'))
    print(headers)


construct_headers()


