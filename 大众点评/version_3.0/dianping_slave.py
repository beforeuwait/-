# coding:utf8

__author__ = 'wangjiawei'
__date__ = '2018-03-16'

"""
    命名为slave(奴隶)，实际上是一个broker，在没有中间件做支撑的时候，暂时通过文本来解决该问题
    1. 从seed里提取种子，生成完整的待抓取列表
    2. 调用request_model模块，完成请求
    3. 调用解析文件，完成解析
    
    ** 2018-03-19： 继续开发，意识到点评的反爬虫里很在意referer这个字段
    最好是抓取评论or详情的过程中，需要带上相应的referer字段
    同时cookie也要对应的配置
"""
import json
import time
from lxml import etree
from request_model import RequestModelAPI
from parse_model import DianpingList

# todo 1:模仿一个从消息队列里提取数据的中间模块

class SlaveModel(object):

    # todo: 需要一个接收消息的模块
    def reveive_seed(self):
        # 目前没有消息队列，这里通过文档打开
        seed_path = open('seed/shop_list.txt', 'r', encoding='utf8')
        for i in (seed_path):
            seed = json.loads(i)
            self.execute(seed)
            break

    # todo: 针对消息的处理部分，过渡件
    def execute(self, seed):
        # 收到seed，处理seed，调用request_model模块，调用parse模块
        # 关于50页url该如何设计呢

        # 实例化请求模块

        # 2018-03-29 突然发现这不是一个通用的execute
        rma = RequestModelAPI()
        for page in range(50):
            seed['url'] = self.construct_url(seed.get('url'), page+1)
            current_num = 1
            while current_num <= 5:
                time.sleep(3)
                result = rma.execute(seed)
                seed.update(result)
                # 解析规则

                # todo: 这儿的问题,需要在 parse里设置一个api来接收
                dpl = DianpingList()
                dpl.parse_list(result)
                # 放入消息队列，这里用文档形式
                if result.get('retry') == 'no':
                    with open('seed/shop_list_json.txt', 'w', encoding='utf8') as f:
                        f.write(json.dumps(seed))
                    del seed
                    del result
                    break

                elif result.get('next_page') == 'no':
                    break
                current_num += 1

            break


    def construct_url(self, link, page):
        """ url构造器，接受原始url，写入页面，并返回"""
        url = link + str(page)
        return url




if __name__ == '__main__':
    # sm = SlaveModel()
    # sm.reveive_seed()
    a = open('./seed/shop_list_json.txt', 'r', encoding='utf8').read()
    dpl = DianpingList()
    dpl.parse_list(json.loads(a))

    # todo: 需要解决一个很明显的问题，就是slave获取了数据，如何确定还有下一页，又如何告知其他slave或者引擎去执行下一个