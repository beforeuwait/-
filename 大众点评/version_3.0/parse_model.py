# coding=utf8

"""
作为大众点评的解析模块，承担 列表，详情，评论的解析

关于data字段，数据存json格式

"""
import json
from lxml import etree

class DianpingList():
    """作为点评网商铺列表的解析器
    获取商铺的id，名称
    同时与预处理里中的地域信息匹配生成列表
    """

    def parse_list(self, result):
        # 处理selector，报错就停止
        try:
            selector = etree.HTML(result.get('html'))
        except:
            selector = None
        if selector is not None:
            list = selector.xpath('//div[@id="shop-all-list"]/ul/li')
            data = {}
            for each in list:
                url = each.xpath('div[@class="txt"]/div[@class="tit"]/a/@href')[0]
                name = each.xpath('div[@class="txt"]/div[@class="tit"]/a/h4/text()')[0]
                id = url.split('/')[-1]
                data[name] = id
            # 向seed里放入data
            result.update({'data':json.dumps(data)})
            # 判断是否有下一页
            next_page = self.has_next_page(result.get('html'))
            result.update({'next_page': next_page})

    # todo: 判断列表是否有下一页
    def has_next_page(self, html):
        """这里需要在seed里添加一个字段，nextPage: yes"""
        selector = etree.HTML(html)
        next_page = selector.xpath('//div[@class="page"]/a[@class="next"]')
        result = 'yes' if next_page else 'no'
        return result