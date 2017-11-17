"""
这是一个测试，作为测试linkip的服务器是否返回jessionid
"""
import requests
import time
import json
session = requests.session()

url_home = 'http://yq.linkip.cn'
url_log = 'http://yq.linkip.cn/user/index.do'

data_log = {
    'name': 'beforeuwait',
    'password': 'forwjw2017',
    'type':1,
}
headers_login = {
    'Host': 'yq.linkip.cn',
    'Origin': 'http://yq.linkip.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
}

home_page = session.get(url_home,headers=headers_login)
jessionid = home_page.cookies.get('JSESSIONID')
cookie_text = ' userName=beforeuwait; userPass=forwjw2017; JSESSIONID=%s' %jessionid

cookies = {
    "Cookies": cookie_text
}

login = session.post(url_log, headers=headers_login, cookies=cookies,data=data_log)



headers = {
    'Host': 'yq.linkip.cn',
    'Origin': 'http://yq.linkip.cn',
    'Referer': 'http://yq.linkip.cn/user/qwyq.do',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

data = {
    'rangeId': 1,
    'currPage': 1,
    'themeId': 0,
    'topicId': 0,
    'sentiment': 1,
    'type': 0,
    'startDay': '2017-11-01 00:00',
    'endDay': '2017-11-16 23:59',
    'page': 500,
    'allKeywords': '',
    'orKeywords': '',
    'noKeywords': '',
    'tuKeywords': '',
    'keyWordLocation': 5
}
theme = [
    # ('南充', '45234'), ('成都', '45344'),
    ('西安', '45345'), ('云南', '45346'), ('新疆', '45347')]
tt = ['id', 'title', 'content', 'createtime', 'url', 'type', 'xss', 'source', 'score', 'sentiment']
# 开始循环
url = 'http://yq.linkip.cn/user/getdata.do'

s1 = time.time()

for city, id in theme:
    n ,page = 1, 1
    while n <= page:
        print(city, str(n))
        data['themeId'] = id
        data['currPage'] = n
        start = time.time()
        js = session.post(url, headers=headers, cookies=cookies,data=data, timeout=60)
        end = time.time()
        jessionid = js.headers.get('Set-Cookie', 'no')
        if jessionid != 'no':
            id = js.cookies.get('JSESSIONID', 'no')
            if id != 'no':
                cookie_text = ' userName=beforeuwait; userPass=forwjw2017; JSESSIONID=%s' % id
                cookies = {
                    "Cookies": cookie_text
                }
        js_dict = json.loads(js.content.decode('utf8'))
        page = int(js_dict.get('pageNum', 1))
        result = js_dict.get('result', [])
        text = ''
        for each in result:
            text += '\u0001'.join([str(each.get(i, ''))for i in tt]).replace('\n', '').replace('\r', '').replace(' ', '') + '\n'

        with open('%s_data.txt' % city, 'a', encoding='utf8') as f:
            f.write(text)
        long = int(end - start)
        try:
            time.sleep(20 - long)
        except:
            continue
        n += 1
s2 = time.time()

print(s2 - s1)