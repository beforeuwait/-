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
import json
import re
from lxml import etree

class figgyHotelEngine:

    def __init__(self) -> None:
        super().__init__()
        self.spider = figgyHotelSpider()
        self.pipe = figgyHotelPipeline()
        self.down = requestModel.requestModel()

    def hotel_list(self):
        """
        作为获取酒店列表的模块
        1。 酒店按照地区的行政编码获取，这大大方便了我们。
        2。 至于反爬虫规则，暂时没有破解的思路，只能放慢请求的频率。
        3。 同时也不能用代理
        """
        area_list = (i.strip().split(setting.blank)for i in open(setting.all_area, 'r', encoding=setting.encode))
        area_set = set(i.strip()for i in open(setting.hotel_list_area_already, 'r', encoding=setting.encode)) # 作为已经抓取城市的set
        for i in area_list:
            if i[-2] == '&':
                continue
            # 转处理逻辑
            if i[-1] not in area_set:
                self.hotel_list_logic(self.deal_area_info(i))
                self.pipe.save_area_code(i[-1])


    def deal_area_info(self, info):
        """
        这里作为地区的数据清洗，将还原该市的行政区编码，同时获取将 市辖区 换成该市
        :param info:
        :return: info
        """
        city_code = str(re.findall('\d\d\d\d', info[-1])[0]) + '00'
        info.append(city_code)
        if info[2] == '市辖区':
            info[2], info[3] = info[0], info[1]
        return info

    def hotel_list_logic(self, info):
        page, num = 1, 1
        while num <= page:
            html = self.down.hotel_list(info[3], info[-2], info[-1], num)
            hotel_list = self.spider.hotel_list(html) if html is not 'bad_requests' else []
            page = self.spider.get_pages(html) if html is not 'bad_requests' else 1
            self.pipe.save_hotel_list(hotel_list, info) if not hotel_list == [] else ''
            num += 1

    def hotel_info(self):
        """
        这部分作为列表获取完全后，进行每个酒店详情的获取
        :return:
        """
        hotel_list = (i.strip().split(setting.blank)for i in open(setting.hotel_list, 'r', encoding=setting.encode))
        hotel_set = (i.strip() for i in open(setting.hotel_info_ex, 'r', encoding=setting.encode))
        for each in hotel_list:
            if each[0] not in hotel_set:
                self.hotel_info_logic(each)

    def hotel_info_logic(self, info):
        html = self.down.hotel_info(info[0])
        data = self.spider.hotel_info(html)
        self.pipe.save_hotel_info(info, data)

class figgyHotelSpider:
    def hotel_list(self, html):
        hotel_list = []
        try:
            js_dict = json.loads(html)
        except:
            js_dict = {}
        cons = js_dict.get('hotelList', [])
        for each in cons:
            shid = each.get('shid', '')     # 酒店id
            name = each.get('name', '')     # 酒店name
            address = each.get('address', '')   #酒店address
            star = each.get('level', {}).get('star', '')    # 星级
            lat = each.get('lat', '')
            lng = each.get('lng', '')
            businessAreas = ','.join(each.get('businessAreas', ''))     # 周边
            hotel_list.append([str(shid), str(name), str(address), str(star), str(lat), str(lng), str(businessAreas)])
        return hotel_list

    def get_pages(self, html):
        try:
            js_dict = json.loads(html)
        except:
            js_dict = {}
        page = int(js_dict.get('query', {}).get('totalPage', 1))
        return page

    def hotel_info(self, html):
        data = []
        selector = etree.HTML(html)
        quote = selector.xpath('//div[@class="hotel-box hotel-desc"]/div[@class="bd"]')[0].xpath('string(.)')
        start = re.findall('\d\d\d\d年开业', html)[0] if re.findall('\d\d\d\d年开业', html) else ''
        room_num = re.findall('\d{1,3}间房', html)[0] if re.findall('\d{1,3}间房', html) else ''
        tel = re.findall('电话\d{3}-\d{8}', html)[0] if re.findall('电话\d{3}-\d{8}', html) else ''
        tel_ex = re.findall('传真\d{3}-\d{8}', html)[0] if re.findall('传真\d{3}-\d{8}', html) else ''
        data.append([start, room_num, tel, tel_ex, quote])
        return data

class figgyHotelPipeline:

    def save_area_code(self, city_id):
        with open(setting.hotel_list_area_already, 'a', encoding=setting.encode) as f:
            f.write(city_id + '\n')

    def save_hotel_list(self, hotel_list, city_info):
        info = city_info.copy()
        info.pop(-1)
        text = ''
        for each in hotel_list:
            each.extend(info)
            text += setting.blank.join(each) + '\n'
        with open(setting.hotel_list, 'a', encoding=setting.encode) as f:
            f.write(text)

    def save_hotel_info(self, info, data):
        hotel_dict = setting.hotel_dict
        hotel_dict_l = setting.hotel_dict_l
        hotel_dict['中文全称'] = info[1]
        hotel_dict['地址'] = info[2]
        hotel_dict['地理位置'] = str(info[4]) + ',' + str(info[5])
        hotel_dict['等级'] = info[3]
        hotel_dict['开业时间'] = data[0][0]
        hotel_dict['总客房数'] = data[0][1]
        hotel_dict['咨询电话'] = data[0][2]
        hotel_dict['传真'] = data[0][3]
        hotel_dict['周边信息'] = info[6]
        hotel_dict['简介'] = data[0][4]
        hotel_dict['省全称'] = info[7]
        hotel_dict['省简称'] = info[8]
        hotel_dict['市全称'] = info[9]
        hotel_dict['市简称'] = info[10]
        hotel_dict['县全称'] = info[11]
        hotel_dict['县简称'] = info[12]
        hotel_dict['行政区号'] = info[13]
        hotel_dict['url'] = 'https://hotel.fliggy.com/hotel_detail2.htm?shid=%s' % info[0]

        text = setting.blank.join([hotel_dict[i] for i in hotel_dict_l])
        with open(setting.hotel_info, 'a', encoding=setting.encode) as f:
            f.write(text.replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '') + '\n')

        with open(setting.hotel_info_ex, 'a', encoding=setting.encode) as f:
            f.write(info[0] + '\n')

class setting:

    blank = config.BLANK

    encode = config.ENCODING

    all_area = config.ALL_AREA

    hotel_list = config.HOTEL_LIST

    hotel_list_area_already = config.HOTEL_LIST_AREA_ALREADY

    hotel_info = config.HOTEL_INFO

    hotel_dict = config.HOTEL_DICT

    hotel_dict_l = config.HOTEL_DICT_L

    hotel_info_ex = config.HOTEL_INFO_EX


class schedule:
    def execute(self, commend):
        if commend == 'all':
            fhe = figgyHotelEngine()
            fhe.hotel_list()
            fhe.hotel_info()
            del fhe
        elif commend == 'list':
            fhe = figgyHotelEngine()
            fhe.hotel_list()
            del fhe
        elif commend == 'info':
            fhe = figgyHotelEngine()
            fhe.hotel_info()
            del fhe

if __name__ == '__main__':
    sch = schedule()
    commend = config.COMMEND
    sch.execute(commend)