# coding=utf8

__auhtor__ = 'WangJiaWei'
'''
记录：
    2017.12.04 重新开发，按照规范要求，解决无缘无故程序死掉的问题
    2017.12.06 完成改版后的demo1，取消多进程，一是并发有限，二容易出现宕掉的情况，三是给了充裕的时间
    2017.12.07 继续完成两个脚本的整合
    2017.12.12 修改逻辑，每次请求后，对requests_x.log 模块进行清空，只留最新的log信息
    2017.12.27 迭代脚本，解决shopping中评论只出现在history中，解决配置文件的动态加载问题
'''


import re
import os
import json
import time
import datetime
import logging
import requests
from faker import Faker
from lxml import etree
try:
    from hdfs3 import HDFileSystem
except:
    pass


class CtripItemsEngine(object):
    """作为整个爬虫系统引擎的存在

    该引擎作为餐饮和购物板块的抓取逻辑模块
    首先获取商铺列表
    再获取商铺详情以及其poiID
    最后获取该店铺的评论，可见携程攻略由于设置，因此

    Attributes:
        self.down: 下载器实例
        self.spider： 爬虫实例
        self.pipe：管道实例
    """

    def __init__(self, setting):
        self.down = CtripItemsDownloader(setting)
        self.spider = CtripItemsSpider(setting)
        self.pipe = CtripItemsPipeline(setting)
        self.setting = setting

    def shop_list(self, choice):
        """获取携程攻略各目的地的餐馆/购物场所列表"""

        # 获取已抓取的城市列表
        #
        # 开始之前应该清空列表

        self.clear_path(self.setting['shop_list'][choice])
        city_list_clear = self.city_list(self.setting['city_list'][self.setting['path']], choice)
        for city in city_list_clear:
            city = city.split(self.setting['blank'])
            self.shop_list_logic(city, choice)
        return

    def city_list(self, city_list, choice):
        if choice == 'shopping':
            city_set = []
            new_city_list = []
            for city in city_list:
                info = city.strip().split(self.setting['blank'])
                if info[-2] not in city_set:
                    city_set.append(info[-2])
                    info[4], info[5] = '', ''
                    code = re.findall('\d\d\d\d', info[6])[0]
                    info[6] = str(code) + '00'
                    new_city_list.append(self.setting['blank'].join(info))
        else:
            new_city_list = city_list
        return new_city_list


    def shop_list_logic(self, city, choice):
        """抓取店铺列表逻辑模块

        :param city: 每个城市的基本数据
        """
        page, next_page = 1, True
        while next_page:
            if city[-1] == '' or choice == 'shopping':
                response = self.down.shop_list(city[-2], page, choice)
            else:
                response = self.down.shop_list_area(city[-2], city[-1], page, choice)
            # 记录请求日志，因为出错容易在此处
            self.recording_response(response)
            # 如果请求是bad_request 即请求下一页
            shop_list_data = self.setting['shop_list_data']
            if response['response'] is not 'bad_requests':
                shop_list_data = self.spider.shop_list(response['response'], shop_list_data)
            next_page = True if not shop_list_data['data'] == [] else False
            if next_page:
                self.pipe.save_shop_list(city, shop_list_data['data'], choice)
            shop_list_data['data'].clear()
            page += 1

    def shop_info_pid(self, choice):
        """获取点评详情和poiid

        1. 再获取列表后，获取每个商铺的详情
        2. 同时获取pid，为评论的抓取做准备
        3. 这里暴露一个问题就是，必须在获取详情后才能拿到pid
        4. 注意这里需要做一个增量更新
        5. 提供两种方式抓取，普通，和多进程两种
        """
        # 这里一个集合用来收集以及抓取的店铺列表详情
        shop_already_exist = set(i.strip().split(self.setting['blank'])[0]
                                 for i in open(self.setting.shop_exists[choice], 'r', encoding=self.setting['encode']))

        shop_list = (i.strip().split(self.setting['blank'])
                     for i in open(self.setting['shop_list'][choice], 'r', encoding=self.setting['encode']))
        for shop in shop_list:
            if shop[-5] not in shop_already_exist:
                self.shop_info_pid_logic(shop, choice)


    def shop_info_pid_logic(self, shop, choice):
        """
        这里要做的是获取每个商铺详细信息，保存，同时保存一份已保存目录并添加pid字段，评论从已获取中提取商铺id以及pid
        :param info: 列表信息
        :return:
        """
        response = self.down.shop_info_pid(shop[-1])
        shop_info_data = self.setting['shop_info_data']
        # 记录请求过程
        self.recording_response(response)
        if response['response'] is not 'bad_requests':
            shop_info = self.spider.shop_info_pid(response['response'], shop_info_data, choice)
            if not shop_info['data'] == [] and shop_info['data'][2] is not '1':
                if not choice == 'shopping':
                    self.pipe.save_restaurant_info_pid(shop_info_data['data'], shop, choice)
                else:
                    self.pipe.save_shopping_info_pid(shop_info_data['data'], shop, choice)
        shop_info_data['data'].clear()
        return

    def shop_comment(self, start, end, choice):
        """这里作为获取每个店铺的评论模块"""
        # 每次开始前都将把cmt目录清空
        self.clear_path(self.setting['cmt_txt'][choice])
        shop_list = (i.strip().split(self.setting['blank'])for i in open(
            self.setting['shop_exists'][choice], 'r', encoding=self.setting['encode']))
        for shop in shop_list:
            if choice == 'shopping':
                self.shop_comment_logic(shop_id=shop[0],
                                        pid=shop[1],
                                        city_id=shop[2],
                                        cnc=shop[3],
                                        start=start,
                                        end=end,
                                        choice=choice
                                        )
            else:
                self.shop_comment_logic(shop_id=shop[0],
                                        pid=shop[1],
                                        cnc=[2],
                                        start=start,
                                        end=end,
                                        choice=choice
                                        )


    def shop_comment_logic(self, **kwargs):
        """由于网站恶心，只能看1000条，100页是上限"""
        num, next_page = 1, True
        while next_page:
            response = self.down.shop_comment(**kwargs, page=num)
            # 记录状态
            shop_cmt = self.setting['shop_data']
            self.recording_response(response)
            if response['response'] is not 'bad_requests':
                shop_cmt = self.spider.shop_comment(response['response'], shop_cmt)
            if not shop_cmt['data'] == []:
                next_page = self.pipe.save_shop_cmt(shop_cmt['data'],
                                                    kwargs.get('shop_id'),
                                                    kwargs.get('start'),
                                                    kwargs.get('end'),
                                                    kwargs.get('choice'))
            else:
                next_page = False
            if num == 100:
                break
            shop_cmt['data'].clear()
            num += 1


    def clear_path(self, path):
        """清洗目录

        :param path:
        """
        f = open(path, 'w+')
        f.close()
        return

    def recording_response(self, response):
        """"做记录写入日志

        暂时作为开发人员用来读取每次请求状态

        :param response: 返回的响应
        """
        if response['response'] is 'bad_requests':
            logging.debug('请求无效，返回"bad_requests"')
        elif response['error'] is not '':
            logging.warning('%s, url: %s, params: %s' % (response['error'], response['url'], response['params']))
        else:
            logging.debug('请求成功, url: %s, params: %s' % (response['url'], response['params']))


class CtripItemsDownloader(object):
    """下载模块，一切请求信息都在这里做处理

        一切请求处理都在这个类里处理
    """
    def __init__(self, setting):
        self.setting = setting

    def do_get_requests(self, *args):
        ''' GET请求模块 '''
        retry = 30
        response = self.setting['request_result']
        response['url'] = args[0]
        response['params'] = args[2] if (len(args) == 3) else ''
        while retry > 0:
            args[1]['User-Agent'] = Faker().user_agent()
            try:
                if len(args) == 2:
                    res = requests.get(args[0], headers=args[1], proxies=self.setting['proxy'], timeout=30)
                else:
                    res = requests.get(args[0], headers=args[1], params=args[2], proxies=self.setting['proxy'], timeout=30)
                # 这里暂时只对 2xx和4xx做处理
                response['status_code'] = res.status_code
                if repr(res.status_code).startswith('2'):
                    response['response'] = res.content.decode(self.setting['encode'])
                    break
                elif repr(res.status_code).startswith('4'):
                    args[1]['Proxy-Switch-Ip'] = 'yes'
                    continue
                else:
                    # 其他情况，继续请求
                    #
                    # 继续完善后续情况
                    args[1]['Proxy-Switch-Ip'] = 'yes'
                    continue
            except Exception as e:
                response['error'] = e
            retry -= 1
        return response

    def shop_list(self, city_id, page, choice):
        url = self.setting['shop_list_url'][choice] % (city_id, page)
        headers = self.setting['headers']
        response = self.do_get_requests(url, headers)
        return response

    def shop_list_area(self, city_id, area_id, page, choice):
        url = self.setting['shop_list_url_area'][choice] % (city_id, area_id, page)
        headers = self.setting['headers']
        response = self.do_get_requests(url, headers)
        return response

    def shop_info_pid(self, link):
        url = self.setting['local_url'] % link
        headers = self.setting['headers']
        response = self.do_get_requests(url, headers)
        return response

    def shop_comment(self, **kwargs):
        url = self.setting['shop_comment_url']
        data = self.setting['comment_data'][kwargs.get('choice')]
        data['poiID'] = kwargs.get('pid')
        data['districtEName'] = kwargs.get('cnc')
        data['pagenow'] = kwargs.get('page')
        data['resourceId'] = kwargs.get('shop_id')
        data['districtId'] = kwargs.get('city_id')
        headers = self.setting['headers_xml']
        response = self.do_get_requests(url, headers, data)
        return response

class CtripItemsSpider(object):
    """网页的解析模块"""

    def __init__(self, setting):
        self.setting = setting

    def shop_list(self, response, shop_list_data):
        selector = None
        try:
            selector = etree.HTML(response)
        except Exception as e:
            shop_list_data['error'] = e
        if selector is not None:
            parse = self.setting['shop_list_parse']
            shop_list = selector.xpath(parse['shop_list'])
            data = shop_list_data['data']
            for shop in shop_list:
                id = shop.xpath(parse['id'])[0] if shop.xpath(parse['id']) else ''
                name = shop.xpath(parse['name'])[0] if shop.xpath(parse['name']) else ''
                address = shop.xpath(parse['address'])[0] if shop.xpath(parse['address']) else ''
                average = shop.xpath(parse['average'])[0] if shop.xpath(parse['average']) else ''
                url = shop.xpath(parse['url'])[0] if shop.xpath(parse['url']) else ''
                data.append([id, name, address, average, url])

        return shop_list_data

    def shop_info_pid(self, html, shop_info, choice):
        '''负责解析每个店铺的pid'''
        selector = None
        try:
            selector = etree.HTML(html)
        except Exception as e:
            shop_info['error'] = e
        if choice == 'restaurant' and selector is not None:
            selector = etree.HTML(html)
            # 解析规则
            parse = self.setting['shop_info_pid_parse']
            data = []
            ex_info = re.findall(parse['ex_info'], html)[0] if re.findall(parse['ex_info'], html) else ''
            try:
                shop_info['js_dict'] = json.loads(ex_info)
            except json.JSONDecodeError:
                shop_info['json_error'] = True
            # 经纬度
            lng = shop_info['js_dict'].get('lng', '')
            lat = shop_info['js_dict'].get('lat', '')
            data.append(lng)
            data.append(lat)
            # 如果pid 返回值为'1'的话，则放弃对该店铺的评论获取
            data.append(selector.xpath(parse['pid'])[0] if selector.xpath(parse['pid'])else '1')
            # 分类
            data.append(selector.xpath(parse['category'])[0] if selector.xpath(parse['category'])else '')
            # 电话
            data.append(selector.xpath(parse['tel'])[0]if selector.xpath(parse['tel'])else '')
            # 营业时间
            data.append(selector.xpath(parse['open_time'])[0]if selector.xpath(parse['open_time'])else '')
            # 描述
            data.append(selector.xpath(parse['descrip'])[0]if selector.xpath(parse['descrip'])else '')
            # cate
            data.append(selector.xpath(parse['cate'])[0]if selector.xpath(parse['cate'])else '')
            shop_info['data'] = data
        elif choice == 'shopping' and selector is not None:
            # 解析商铺的parse
            data = []
            parse = self.setting['shop_info_pid_parse']
            # city_id
            data.append(re.findall(parse['city_id'], html)[0] if re.findall(parse['city_id'], html) else '0')
            # pid
            data.append(re.findall(parse['shop_pid'], html)[0] if re.findall(parse['shop_pid'], html) else '0')
            # city_cnc
            data.append(re.findall(parse['city_cnc'], html)[0] if re.findall(parse['city_cnc'], html) else '')
            selector = etree.HTML(html)
            # catrgory
            data.append(selector.xpath(parse['shop_category'])[0]if selector.xpath(parse['shop_category']) else '')
            # addresss
            data.append(selector.xpath(parse['shop_address'])[0] if selector.xpath(parse['shop_address']) else '')
            # tel
            data.append(selector.xpath(parse['shop_tel'])[0] if selector.xpath(parse['shop_tel']) else '')
            # opentime
            data.append(selector.xpath(parse['shop_optime'])[0] if selector.xpath(parse['shop_optime']) else '')
            # deacriptation
            try:
                descriptation = selector.xpath(parse['shop_descrip'])[0].xpath('string(.)')
            except:
                descriptation = ''
            data.append(descriptation)
            # product
            data.append(','.join(selector.xpath(parse['shop_product'])))
            # trans
            try:
                trans = selector.xpath(parse['shop_trans'])[1] if selector.xpath(parse['shop_trans']) else ''
            except:
                trans = ''
            # city_id, pid, city_cnc, category, address, tel, opentime, descriptation,products,trans
            data.append(trans)
            shop_info['data'] = data
        return shop_info

    def shop_comment(self, html, shop_cmt):
        selector = None
        try:
            selector = etree.HTML(html)
        except Exception as e:
            shop_cmt['error'] = e
        if selector is not None:
            parse = self.setting['cmt_parse']
            comments = selector.xpath(parse['comments'])
            if comments:
                for comment in comments:
                    user = comment.xpath(parse['user'])[0] if comment.xpath(parse['user']) else ''
                    star = comment.xpath(parse['star'])[0] if comment.xpath(parse['star']) else ''
                    socar = comment.xpath(parse['socar'])[0] if comment.xpath(parse['socar']) else ''
                    average = comment.xpath(parse['average'])[0] if comment.xpath(parse['average']) else ''
                    content = comment.xpath(parse['content'])[0] if comment.xpath(parse['content']) else ''
                    time2 = comment.xpath(parse['time2'])[0] if comment.xpath(parse['time2']) else ''
                    photo = ''
                    if comment.xpath(parse['photo']):
                        photo = ','.join(comment.xpath(parse['photo']))
                    shop_cmt['data'].append([user, star, socar, average, content, time2, photo])
        return shop_cmt


class CtripItemsPipeline(object):
    """管道，做数据处理用的"""

    def __init__(self, setting):
        self.setting = setting

    def save_shop_list(self, info, data, choice):
        text = ''
        exinfo = info.copy()
        exinfo.pop(-1)
        city = exinfo
        for each in data:
            context = self.setting['blank'].join(city)
            # 为shopping 添加id,以及在 restaurant 的人均位置添加city_id
            if choice == 'shopping':
                each[0] = re.findall('(\d{1,10})', each[-1].split('/')[-1])[0]
                each[-2] = re.findall('(\d{1,10})', each[-1].split('/')[-2])[0]
            text += re.sub('\n|\r| ', '', context + self.setting['blank'] + self.setting['blank'].join(each)) + '\n'
        with open(self.setting['shop_list'][choice], 'a', encoding=self.setting['encode']) as f:
            f.write(text)
        return

    def save_restaurant_info_pid(self, data, shop_info, choice):
        info = self.setting['rest_dict']
        info_l = self.setting['rest_dict_l']
        info['中文全称'] = shop_info[9]
        info['所属地区'] = shop_info[2]
        info['地址'] = shop_info[-3]
        info['地理位置'] = repr(data[0]) + ',' + repr(data[1])
        info['类型'] = data[3]
        info['营业时间'] = data[5]
        info['人均消费'] = shop_info[-2]
        info['特色菜品'] = data[-1]
        info['咨询电话'] = data[4]
        info['简介'] = data[-2]
        info['url'] = self.setting['local_url'] % shop_info[-1]
        info['省自治区全称'] = shop_info[0]
        info['省自治区简称'] = shop_info[1]
        info['市州全称'] = shop_info[2]
        info['市州简称'] = shop_info[3]
        info['区县全称'] = shop_info[4]
        info['区县简称'] = shop_info[5]
        info['地区编码'] = shop_info[6]
        text_list = [info[i] for i in info_l]
        text = re.sub('\n|\r| ', '', self.setting['blank'].join(text_list)) + '\n'
        text_ex = self.setting['blank'].join([shop_info[8], data[2],
                                      re.findall('(.*?)\d', shop_info[-1].split('/')[2])[0]]) + '\n'
        with open(self.setting['shop_info'][choice], 'a', encoding=self.setting['encode']) as f:
            f.write(text)
        with open(self.setting['shop_exists'][choice], 'a', encoding=self.setting['encode']) as f:
            f.write(text_ex)

    def save_shopping_info_pid(self, data, shop_info, choice):
        info = self.setting['shopping_dict']
        info_l = self.setting['shopping_dict_l']
        info['中文全称'] = shop_info[-4]
        info['所属地区'] = shop_info[2]
        info['地址'] = shop_info[-3]
        info['类型'] = data[3]
        info['营业时间'] = data[6]
        info['特色商品'] = data[-2]
        info['咨询电话'] = data[5]
        info['交通信息'] = data[-1]
        info['简介'] = data[-3]
        info['url'] = self.setting['local_url'] % shop_info[-1]
        info['省自治区全称'] = shop_info[0]
        info['省自治区简称'] = shop_info[1]
        info['市州全称'] = shop_info[2]
        info['市州简称'] = shop_info[3]
        info['区县全称'] = shop_info[4]
        info['区县简称'] = shop_info[5]
        info['地区编码'] = shop_info[6]
        text_list = [info[i] for i in info_l]
        text = re.sub('\n|\r| ', '', self.setting['blank'].join(text_list)) + '\n'
        # text_ex 存储对字段有 shopid,pid, city_id, citycne,
        text_ex = self.setting['blank'].join([shop_info[-5], data[1], data[0], data[2]]) + '\n'
        with open(self.setting['shop_info'][choice], 'a', encoding=self.setting['encode']) as f:
            f.write(text)

        with open(self.setting['shop_exists'][choice], 'a', encoding=self.setting['encode']) as f:
            f.write(text_ex)
        return

    def save_shop_cmt(self, cmt_list, shop_id, start, end, choice):
        text = ''
        result = False
        for each in cmt_list:
            if each[-2] >= start and each[-2] <= end:
                text += shop_id + self.setting['blank'] + self.setting['blank'].join(each).replace('\n', '').replace('\r', '') \
                    .replace(' ', '').replace('width:', '').replace('%', '') + '\n'
                result = True
            else:
                result = False
        with open(self.setting['cmt_txt'][choice], 'a', encoding=self.setting['encode']) as f:
            f.write(text)

        with open(self.setting['cmt_txt_h'][choice], 'a', encoding=self.setting['encode']) as f:
            f.write(text)
        return result


class CtripItemsSchedule(object):
    """
    调度模块
    """

    def execute(self):
        """
        这里是一个循环控制模块。一周执行一次
        """
        while True:
            setting = self.reload_config()
            start = time.time()
            self.main(setting)
            self.load_2_hdfs(setting)
            end = time.time()
            cost = int(end-start)
            if cost < 3600*24*7:
                time.sleep(3600*24*7 - cost)
                logging.debug('抓取完毕，开始休眠')
            else:
                continue

    def reload_config(self):
        """
        作为动态的配置文件的导入
        """
        config = open('config.ini', 'r', encoding='utf8').read()
        with open('config.py', 'w', encoding='utf8') as f:
            f.write(config)
        import config
        from imp import reload
        reload(config)
        setting = {
            'blank': config.BLANK,
            'encode': config.ENCODING,
            'city_list': config.CITY_LIST,
            'shop_list_data': config.SHOP_LIST_DATA,
            'shop_list': config.SHOP_LIST,
            'shop_exists': config.SHOP_EXISTS,
            'shop_info': config.SHOP_INFO,
            'shop_info_data': config.SHOP_INFO_DATA,
            'request_result': config.REQUESTS_RESULT,
            'proxy': config.PROXY,
            'shop_list_url': config.SHOP_LIST_URL,
            'headers': config.HEADERS,
            'headers_xml': config.HEADERS_XML,
            'shop_list_url_area': config.SHOP_LIST_URL_AREA,
            'local_url': config.LOCAL_URL,
            'shop_list_parse': config.REST_SHOP_LIST_PARSE,
            'shop_info_pid_parse': config.RES_SHOP_INFO_PID_PARSE,
            'rest_dict': config.RESTAURANT_DICT,
            'rest_dict_l': config.RESTAURANT_DICT_L,
            'shop_comment_url': config.SHOP_CMT_URL,
            'comment_data': config.CMT_DATA,
            'cmt_parse': config.CMT_PARSE,
            'shop_data': config.SHOP_CMT_DATA,
            'cmt_txt': config.SHOP_CMT,
            'cmt_txt_h': config.SHOP_CMT_HISTORY,
            'shopping_dict': config.SHOPPING_DICT,
            'shopping_dict_l': config.SHOPPING_DICT_L,
            'start_date': config.START_DATE,
            'choice': config.CHOICE,
            'hdfs_path': config.HDFS_PATH,
            'path': config.PATH,
        }
        return setting

    def load_2_hdfs(self, setting):
        list_path = setting.shop_list[setting.choice]
        hdfs_list_path = setting.hdfs_path % os.path.split(setting.shop_list[setting.choice])[1]
        info_path = setting.shop_info[setting.choice]
        hdfs_info_path = setting.hdfs_path % os.path.split(setting.shop_info[setting.choice])[1]
        cmt_path = setting.cmt_txt[setting.choice]
        hdfs_cmt_path = setting.hdfs_path % os.path.split(setting.cmt_txt[setting.choice])[1]
        try:
            hdfs = HDFileSystem(host='192.168.100.178', port=8020)
            hdfs.put(list_path, hdfs_list_path)
            hdfs.put(info_path, hdfs_info_path)
            hdfs.put(cmt_path, hdfs_cmt_path)
        except:
            logging.warning('集群挂了')

    def main(self, setting):
        start_date = self.read_date(setting)
        end_date = datetime.datetime.today().strftime('%Y-%m-%d')
        sl = CtripItemsEngine(setting)
        sl.shop_list(setting['choice'])
        sl.shop_info_pid(setting['choice'])
        sl.shop_comment(start_date, end_date, setting['choice'])
        self.input_date(end_date, setting)
        del sl
        return

    def read_date(self, setting):
        return open(setting['start_date'][setting['choice']], 'r', encoding=setting['encode']).read()

    def input_date(self, date, setting):
        with open(setting['start_date'][setting['choice']], 'w+', encoding=setting['encode']) as f:
            f.write(date)

if __name__ == '__main__':
    schedule = CtripItemsSchedule()
    schedule.execute()