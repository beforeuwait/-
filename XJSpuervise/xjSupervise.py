# coding=utf8
"""
主程序

"""
import requests
import re
import config
import execjs


session = requests.session()
url0 = 'http://222.82.233.101/mainframe.jsp'
url = 'http://222.82.233.101/login.do'
url2 = 'http://222.82.233.101'
headers = {
    "Host": "222.82.233.101",
    "Origin": "http://222.82.233.101",
    "Referer": "http://222.82.233.101/mainframe.jsp",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36",
}

headers1 = {
    "Host": "222.82.233.101",
    "Origin": "http://222.82.233.101",
    "Referer": "http://222.82.233.101/index_main.jsp",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36",
}
html2 = session.get(url2, headers=headers1)
html = session.get(url0, headers=headers1).content.decode('utf8')
ex_txt = re.findall('var v=\'(.*)\';', html)[0]

pwd = '123456789' + ex_txt
js_text = open('main.js', 'r', encoding='utf8').read()
js = execjs.compile(js_text)
result = js.call("encryptedString", pwd)

data = {
    "secureLogin": "true",
    "action": "login",
    "userName": "B00-37",
    "password": result
}
print(data)
login = session.post(url, headers=headers, data=data)
print(login.status_code)
print(login.content.decode('utf8'))