"""
作为配置模块的存在

日志：
2017-11-14：开始开发

"""

import os
#   用于定位到绝对路径
os.chdir(os.path.split(os.path.realpath(__file__))[0])



# 日期
start = '2017-05-01'
end = '2017-11-01'

# headers

headers_token = {
    "Host": "222.82.233.101",
    "Origin": "http://222.82.233.101",
    "Referer": "http://222.82.233.101/index_main.jsp",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36",
}

headers_login = {
    "Host": "222.82.233.101",
    "Origin": "http://222.82.233.101",
    "Referer": "http://222.82.233.101/mainframe.jsp",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36",
}

headers_data = {
    "Host": "222.82.233.101",
    "Origin": "http://222.82.233.101",
    "Referer": "http://222.82.233.101/team/query.do?action=list&forward=bureauTeamQueryList",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36",
}

# url

url_token = 'http://222.82.233.101/mainframe.jsp'

url_login = 'http://222.82.233.101/login.do'

url_data = 'http://222.82.233.101/team/query.do?action=list'

url_each_info = 'http://222.82.233.101/team/edit/editTeam.do'
#

blank = '\u0001'
encoding = 'utf-8'

#

data_login = {
    "secureLogin": "true",
    "action": "login",
    "userName": "B00-37",
    "password": ''
}

data_query = {
    "from": "query",
    "forward": "bureauTeamQueryList",
    "travelDayMinMaxMode": "cross",
    "travelDay": "2017-11-06"
}

each_info = {
    "action": "view",
    "id": ""
}

passwd = '123456789'

# file

team_list = os.path.join(os.path.abspath('Data'), 'team_list.txt')
if not os.path.exists(team_list):
    f = open(team_list, 'w')
    f.close()

each_schedule_info = os.path.join(os.path.abspath('Data'), 'schedule_info.txt')
if not os.path.exists(each_schedule_info):
    f = open(each_schedule_info, 'w+')
    f.close()