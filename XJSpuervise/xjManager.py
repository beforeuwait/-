"""
作为新疆旅游目的地一城通的正式项目地址
日志：
2017-11-14 开始开发，解决登陆问题，其rsa算法采用的是自己修改过的版本
2017-11-15 成功登陆，开始拿开发数据抓去脚本
2017-11-16 完成详情采集部分，写正则简直想吐

"""
import config
import re
import time
import datetime
import requests
import execjs
from lxml import etree

class xjLoginSupervise:

    def __init__(self):
        self.down = xjDownloader()
        self.spider = xjSpider()
        self.pipe = xjPipeline()

    def get_token(self):
        html = self.down.get_token()
        token = self.spider.get_token(html) if html is not 'bad_requests' else '000'
        return token

    def construct_data(self, token):
        data = setting.data_login
        passwd = setting.psswd + token
        data['password'] = self.pipe.get_passwd(passwd)
        return data

    def login(self, data):
        self.down.login(data)


class xjEngine:
    def __init__(self):
        self.login = xjLoginSupervise()
        self.down = xjDownloader()
        self.spider = xjSpider()
        self.pipe = xjPipeline()

    def log_in(self):
        # 先获取token
        token = self.login.get_token()
        # 无脑验证环节
        while True:
            if token == '000':
                token = self.login.get_token()
            else:
                break
        # 构建请求参数
        data = self.login.construct_data(token)
        # 登陆
        self.login.login(data)


    def query_data(self):
        """
        这里要实现指定日期的查询
        """
        start = datetime.datetime.strptime(setting.start, '%Y-%m-%d')
        end = datetime.datetime.strptime(setting.end, '%Y-%m-%d')
        while True:
            self.query_data_logic(start.strftime('%Y-%m-%d'))
            start += datetime.timedelta(days=1)
            time.sleep(10)
            if start > end:
                break

    def query_data_logic(self, date):
        html = self.down.query_data(date)
        data = self.spider.query_data(html) if html is not 'bad_requests' else []
        self.pipe.save_team_data(data) if not data == [] else ''

    def each_team_info(self):
        team_list = (i.strip().split(setting.blank)for i in open(setting.team_list, 'r', encoding=setting.encode))
        for each in team_list:
            print(each)
            self.each_team_info_logic(each[0])
            break

    def each_team_info_logic(self, team_id):
        html = self.down.each_team_info(team_id)
        data = self.spider.get_each_team_info(html)
        self.pipe.save_each_team_info(data, team_id)

class xjDownloader:
    session = requests.session()

    def GET_request(self, **kwargs):
        retry = 3
        response = 'bad_requests'
        while retry > 0:
            try:
                res = self.session.get(kwargs.get('url'), headers=kwargs.get('headers'), params=kwargs.get('params'), timeout=30)
                if repr(res.status_code).startswith('2'):
                    response = res.text
                    break
            except Exception as e:
                print('请求中断', e)
            retry -= 1
        return response

    def POST_request(self, **kwargs):
        retry = 3
        response = 'bad_requests'
        while retry > 0:
            try:
                res = self.session.post(kwargs.get('url'), headers=kwargs.get('headers'), data=kwargs.get('data'), timeout=30)
                if repr(res.status_code).startswith('2'):
                    response = res.text
                    break
            except Exception as e:
                print('请求中断', e)
            retry -= 1
        return response

    def get_token(self):
        url = setting.url_token
        headers = setting.headers_token
        html = self.GET_request(url=url, headers=headers)
        return html

    def login(self, data):
        url = setting.url_login
        headers = setting.headers_login
        self.POST_request(url=url, headers=headers, data=data)

    def query_data(self, date):
        url = setting.url_data
        headers = setting.headers_data
        data = setting.data_query
        data['travelDay'] = date
        html = self.POST_request(url=url, headers=headers, data=data)
        return html

    def each_team_info(self, team_id):
        url = setting.url_each_info
        headers = setting.headers_data
        params = setting.params_each_info
        params['id'] = team_id
        html = self.GET_request(url=url, headers=headers, params=params)
        return html


class xjSpider:
    def get_token(self, html):
        token = re.findall('var v=\'(.*)\';', html)[0] \
            if re.findall('var v=\'(.*)\';', html) \
            else '000'
        return token

    def query_data(self, html):
        selector = etree.HTML(html)
        cons = selector.xpath('//table[@id="team"]/tbody/tr')
        data = []
        for each in cons:
            team_id = each.xpath('td[1]/text()')[0] if each.xpath('td[1]/text()') else ''
            team_type = each.xpath('td[3]/text()')[0] if each.xpath('td[3]/text()') else ''
            team_number = each.xpath('td[4]/text()')[0] if each.xpath('td[4]/text()') else ''
            agency = each.xpath('td[5]/text()')[0] if each.xpath('td[5]/text()') else ''
            people_count = each.xpath('td[6]/text()')[0] if each.xpath('td[6]/text()') else ''
            pay_prep = each.xpath('td[7]/text()')[0] if each.xpath('td[7]/text()') else ''
            start_date = each.xpath('td[8]/text()')[0] if each.xpath('td[8]/text()') else ''
            setup_date = each.xpath('td[9]/text()')[0] if each.xpath('td[9]/text()') else ''
            go_date = each.xpath('td[10]/text()')[0] if each.xpath('td[10]/text()') else ''
            state = each.xpath('td[11]/text()')[0] if each.xpath('td[11]/text()') else ''
            data.append([team_id, team_type, team_number, agency, people_count, pay_prep, start_date, setup_date, go_date, state])
        return data

    def get_each_team_info(self, html):
        data = []
        text = re.findall('team begin(.*)team end', html, re.S)[0]
        team_number = re.findall('.teamSN=trimStr\(\'(.*?)\'\);', text)[0]  # 团号
        data.append(team_number)
        begin = re.findall('.beginDay=trimStr\(\'(.*?)\'\);', text)[0]      # 开团
        data.append(begin)
        end = re.findall('.endDay=trimStr\(\'(.*?)\'\);', text)[0]          # 结束
        data.append(end)
        agency = re.findall('.getTravelAgency\(\).name=trimStr\(\'(.*?)\'\);', text)[0]     # 旅行社
        data.append(agency)
        department = re.findall('.getDept\(\).name=trimStr\(\'(.*?)\'\);', text)[0]         # 部门
        data.append(department)
        operator = re.findall('.getOperator\(\).name=trimStr\(\'(.*?)\'\);', text)[0]       # 操作员
        data.append(operator)
        agency_ex = re.findall('.fromTravelAgency=trimStr\(\'(.*?)\'\);', text)[0]          # 组团社
        data.append(agency_ex)
        team_leader = re.findall('.teamLeader=trimStr\(\'(.*?)\'\);', text)[0]              # 领队
        data.append(team_leader)
        arrive_when = re.findall('.arriveWhenDesc=trimStr\(\'(.*?)\'\);', text)[0]          # 到达时间
        data.append(arrive_when)
        arrive_where = re.findall('.arriveWhereDesc=trimStr\(\'(.*?)\'\);', text)[0]        # 到达地址
        data.append(arrive_where)
        arrive_how = re.findall('.arriveHowDesc=trimStr\(\'(.*?)\'\);', text)[0]            # 到达方式
        data.append(arrive_how)
        return_when = re.findall('.returnWhenDesc=trimStr\(\'(.*?)\'\);', text)[0]          # 返程时间
        data.append(return_when)
        return_where = re.findall('.returnWhereDesc=trimStr\(\'(.*?)\'\);', text)[0]        # 返程地址
        data.append(return_where)
        return_how = re.findall('.returnHowDesc=trimStr\(\'(.*?)\'\);', text)[0]            # 返程方式
        data.append(return_how)
        team_type = re.findall('getTeamType\(\).name=trimStr\(\'(.*?)\'\);', text)[0]       # 团队类型
        data.append(team_type)
        come_from = re.findall('.getArea\(\).listName = trimStr\(\'(.*?)\'\);', text)[0]    # 来自
        data.append(come_from)
        adult_num = re.findall('.adultNumber = trimStr\(getInt\(\'(.*?)\'\)\);', text)[0]   # 成年数
        data.append(adult_num)
        children = re.findall('childrenNumber = trimStr\(getInt\(\'(.*?)\'\)\);', text)[0]  # 儿童数量
        data.append(children)
        car_no = re.findall('.getCar\(\).carNo = trimStr\(\'(.*?)\'\);', text)[0]           # 汽车
        data.append(car_no)
        trans_port = re.findall('transportName = trimStr\(\'(.*?)\'\);', text)[0]           # 车队
        data.append(trans_port)
        driver = re.findall('driverName = trimStr\(\'(.*?)\'\);', text)[0]                  # 司机
        data.append(driver)
        guide = re.findall('getGuide\(\).fullName = trimStr\(\'(.*?)\'\);', text)[0]        # 导游
        data.append(guide)
        sex = re.findall('getGuide\(\).gender = trimStr\(\'(.*?)\'\);', text)[0]            # 导游性别
        data.append(sex)
        guide_id = re.findall('getGuide\(\).license = trimStr\(\'(.*?)\'\);', text)[0]      # 导游证书
        data.append(guide_id)
        offical = re.findall('affiliatedOrganName= trimStr\(\'(.*?)\'\);', text)[0]         # 导游来自
        data.append(offical)
        tel = re.findall('mobile = trimStr\(\'(.*?)\'\);', text)[0]                         # 导游电话
        data.append(tel)
        # 酒店信息
        hotel_info = re.findall('teamItem=new TeamRoom\(\);(.*?)fillTeamItem\(teamItem\);', text, re.S)
        hotel_ex = ''
        for hotel in hotel_info:
            name = re.findall('arrange=trimStr\(\'(.*?)\'\);', hotel)[0]                    # 酒店名字
            arr_time = re.findall('prepArriveDay=trimStr\(\'(.*?)\'\);', hotel)[0]          # 到达时间
            left_time = re.findall('prepLeftDay=trimStr\(\'(.*?)\'\);', hotel)[0]           # 离开时间
            breakfast = '包含' if re.findall('breakfast=\'(.*?)\';', hotel)[0] == 'true' else '不包含'   # 早餐
            dinner ='包含' if re.findall('dinner=\'(.*?)\';', hotel)[0] == 'true' else '不包含'          # 正餐
            in_order = '包含' if re.findall('inOrder=\'(.*?)\';', hotel)[0] == 'true' else '不包含'      # 晚餐
            hotel_ex += name + ',' + arr_time + ',' + left_time + ',' + breakfast + ',' + dinner + ',' + in_order + ';'
        data.append(hotel_ex)
        # 行程 所在地
        schedule_ex = ''
        area_ex = ''
        schedule_area = re.findall('travelDay = (.*?)fillTeamItem\(shelduleTeamItem\);', text, re.S)
        for day in schedule_area:
            arrange = re.findall('arrange=trimStr\(\'(.*?)\'\);', day)
            if arrange:
                schedule_ex += re.findall('trimStr\(\'(\d\d\d\d-\d\d-\d\d)\'\);', day)[0] + ',' + re.findall('arrange=trimStr\(\'(.*?)\'\);', day)[0] + ';'

            city = re.findall('arriveCity=trimStr\(\'(.*?)\'\);', day)
            if city:
                area_ex += re.findall('trimStr\(\'(\d\d\d\d-\d\d-\d\d)\'\);', day)[0] + ',' + re.findall('arriveCity=trimStr\(\'(.*?)\'\);', day)[0] + ';'
        data.append(schedule_ex)
        data.append(area_ex)
        return data


class xjPipeline:
    def get_passwd(self, passwd):
        js_text = open('main.js', 'r', encoding='utf8').read()
        js = execjs.compile(js_text)
        result = js.call("encryptedString", passwd)
        return result

    def save_team_data(self, data):
        text = ''
        for each in data:
            text += setting.blank.join(each).replace('\n', '').replace('\r', '').replace(' ', '') + '\n'
        with open(setting.team_list, 'a', encoding=setting.encode) as f:
            f.write(text)

    def save_each_team_info(self, data, id):
        text = id + setting.blank + setting.blank.join(data)
        with open(setting.each_schedule, 'a', encoding=setting.encode) as f:
            f.write(text)

class setting:

    headers_token = config.headers_token
    headers_login = config.headers_login
    headers_data = config.headers_data
    url_token = config.url_token
    url_login = config.url_login
    url_data = config.url_data
    url_each_info = config.url_each_info
    data_login = config.data_login
    data_query = config.data_query
    psswd = config.passwd
    encode = config.encoding
    blank = config.blank
    team_list = config.team_list
    each_schedule = config.each_schedule_info
    params_each_info = config.each_info
    start = config.start
    end = config.end

if __name__ == '__main__':
    xje = xjEngine()
    xje.log_in()
    xje.query_data()
    xje.each_team_info()
