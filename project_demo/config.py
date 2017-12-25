# coding=utf8

"""
该文件作为配置文件，实现程序的动态，灵活，简单维护性高
"""
import os
os.chdir(os.path.split(os.path.abspath(__file__))[0])


RESPONSE = {
    'html': 'bad_requests',
    'status_code': 200,
    'url': '',
    'error': '',
}

DATA_LIST = {
    'data': [],
    'error': ''
}