# coding=utf8

__author__ = 'WangJiaWei'

import os
import time
import datetime
try:
    from hdfs3 import HDFileSystem
except:
    pass
"""
每天 00：00 上传hdfs 15个空文件
包含：
    携程： 购物 娱乐 （列表，详情， 评论）
    点评： 美食 购物 娱乐 （列表， 详情， 评论）
"""

dp_list = {
    'food': os.path.abspath('%s_food_shop_list.txt' % '四川'),
    'entertainment': os.path.abspath('%s_entertainment_shop_list.txt' % '四川'),
    'shopping': os.path.abspath('%s_shopping_shop_list.txt' % '四川'),
}

dp_info = {
    'food': os.path.abspath('%s_food_shop_info.txt' % '四川'),
    'entertainment': os.path.abspath('%s_entertainment_shop_info.txt' % '四川'),
    'shopping': os.path.abspath('%s_shopping_shop_info.txt' % '四川'),
}

dp_cmt = {
    'food': os.path.abspath('%s_food_cmt.txt' % '四川'),
    'entertainment': os.path.abspath('%s_entertainment_cmt.txt' % '四川'),
    'shopping': os.path.abspath('%s_shopping_cmt.txt' % '四川')
}


cp_list = {
    'food': os.path.abspath('%s_restaurant_shop_list.txt' % '四川'),
    'shopping': os.path.abspath('%s_shopping_shop_list.txt' % '四川'),
}

cp_info = {
    'food': os.path.abspath('%s_restaurant_shop_info.txt' % '四川'),
    'shopping': os.path.abspath('%s_shopping_shop_info.txt' % '四川'),
}

cp_cmt = {
    'food': os.path.abspath('%s_restaurant_cmt.txt' % '四川'),
    'shopping': os.path.abspath('%s_shopping_cmt.txt' % '四川')
}

def make_file():
    # 创建空文件
    for i in ['food', 'shopping']:
        for each in [cp_list, cp_info, cp_cmt]:
            if not os.path.exists(each[i]):
                f = open(each[i], 'w+')
                f.close()

    for i in ['food', 'shopping', 'entertainment']:
        for each in [dp_list, dp_info, dp_cmt]:
            if not os.path.exists(each[i]):
                f = open(each[i], 'w+')
                f.close()

def load2hdfs():
    # 携程
    try:
        hdfs = HDFileSystem(host='192.168.100.178', port=8020)
        for i in ['food', 'shopping']:
            for each in [cp_list, cp_info, cp_cmt]:
                hdfs_file = '/user/spider/everyday/' + os.path.split(each[i])[1]
                hdfs.put(each[i], hdfs_file)
        for i in ['food', 'shopping', 'entertainment']:
            for each in [dp_list, dp_info, dp_cmt]:
                hdfs_file = '/user/spider/dianping/' + os.path.split(each[i])[1]
                hdfs.put(each[i], hdfs_file)
    except:
        print('集群挂了')

def main():
    while True:
        now = datetime.datetime.today().strftime('%H-%M')
        if now == '00-01':
            make_file()
            load2hdfs()
            time.sleep(3599*24)
        else:
            time.sleep(10)

if __name__ == '__main__':
    main()