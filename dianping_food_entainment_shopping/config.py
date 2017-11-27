'''
作为配置文件的存在,同时可以把代理放在这里
'''
import os
os.chdir(os.path.split(os.path.realpath(__file__))[0])

COMMAND_FOOD = 'all'

COMMAND_ENTAINMENT = 'all'

COMMAND_SHOPPING = 'all'


PATH = 'Data'

PROVINCE = ''
# PATH = 'D:\workPlace\dianPing3.0\Data'


# 城市目录
AREA_FILE = os.path.join(os.path.abspath(PATH), 'provs_city_code.txt')

'''****************************美食***************************************************'''

CATEGORY_FOOD = os.path.join(os.path.abspath(PATH), 'food_list.txt')

RESTAURANT_LIST = os.path.join(os.path.abspath(PATH), 'restaurant_shop_list.txt')

RESTAURANT_INFO = os.path.join(os.path.abspath(PATH), 'restaurant_shop_info.txt')

EX_RESTAURANT_ID_LIST = os.path.join(os.path.abspath(PATH), 'ex_restaurant_list.txt')

RESTAURANT_CMT = os.path.join(os.path.abspath(PATH), 'restaurant_cmt_%s_%s.txt')

'''*****************************娱乐*****************************************************'''

CATEGORY_ENTAINMENT = os.path.join(os.path.abspath(PATH), 'entainment_list.txt')

ENTAINMENT_LIST = os.path.join(os.path.abspath(PATH), 'entainment_shop_list.txt')

ENTAINMET_INFO = os.path.join(os.path.abspath(PATH), 'entainment_shop_info.txt')

EX_ENTAINMENT_ID_LIST = os.path.join(os.path.abspath(PATH), 'ex_entainment_list.txt')

ENTAINMENT_CMT = os.path.join(os.path.abspath(PATH), 'entainment_cmt_%s_%s_%s.txt')

'''*****************************购物******************************************************'''

CATEGORY_SHOPPING = os.path.join(os.path.abspath(PATH), 'shopping_list.txt')

SHOPPING_LIST = os.path.join(os.path.abspath(PATH), 'shopping_shop_list.txt')

SHOPPING_INFO = os.path.join(os.path.abspath(PATH), 'shopping_shop_info.txt')

EX_SHOPPING_ID_LIST = os.path.join(os.path.abspath(PATH), 'ex_shopping_list.txt')

SHOPPING_CMT = os.path.join(os.path.abspath(PATH), 'shopping_cmt_%s_%s.txt')

'''***************************hdfs******************************************'''
HDFS = '/user/spider/bianmu_22_data/%s'

# Date

# MIN_DATE = '2012-01-01'
MIN_DATE_FILE_FOOD = os.path.join(os.path.abspath(PATH), 'start_date_food.txt')
MIN_DATE_FILE_SHOP = os.path.join(os.path.abspath(PATH), 'start_date_shop.txt')
MIN_DATE_FILE_ENTERTAIN = os.path.join(os.path.abspath(PATH), 'start_date_entertain.txt')
MAX_DATE_FILE_FOOD = os.path.join(os.path.abspath(PATH), 'end_date_food.txt')
MAX_DATE_FILE_SHOP = os.path.join(os.path.abspath(PATH), 'end_date_shop.txt')
MAX_DATE_FILE_ENTERTAIN = os.path.join(os.path.abspath(PATH), 'end_date_entertain.txt')
# MAX_DATE = '2017-11-24'

# Data

RESTAURANT_DATA = {
    "中文全称": "&",
    "中文简称": "&",
    "所属地区": "&",
    "地址": "&",
    "地理位置": "&",
    "类型": "&",
    "等级": "&",
    "营业时间": "&",
    "人均消费": "&",
    "特色菜品": "&",
    "咨询电话": "&",
    "传真": "&",
    "邮政编码": "&",
    "投诉电话": "&",
    "交通信息": "&",
    "周边信息": "&",
    "简介": "&",
    "国别": "&",
    "省自治区全称": "&",
    "省自治区简称": "&",
    "市州全称": "&",
    "市州简称": "&",
    "区县全称": "&",
    "区县简称": "&",
    "地区编码": "&",
    "url": "&",
    }
RESTAURANT_DATA_L = [
    "中文全称", "中文简称", "所属地区", "地址", "地理位置", "类型", "等级", "营业时间", "人均消费", "特色菜品", "咨询电话",
    "传真", "邮政编码", "投诉电话", "交通信息", "周边信息", "简介", "国别", "省自治区全称", "省自治区简称", "市州全称",
    "市州简称", "区县全称", "区县简称", "地区编码", "url",
    ]

ENTAINMENT_DATA = {
    "中文全称": "&",
    "中文简称": "&",
    "所属地区": "&",
    "地址": "&",
    "地理位置": "&",
    "类型": "&",
    "营业时间": "&",
    "咨询电话": "&",
    "传真": "&",
    "邮政编码": "&",
    "投诉电话": "&",
    "交通信息": "&",
    "周边信息": "&",
    "简介": "&",
    "国别": "&",
    "省自治区全称": "&",
    "省自治区简称": "&",
    "市州全称": "&",
    "市州简称": "&",
    "区县全称": "&",
    "区县简称": "&",
    "地区编码": "&",
    "url": "&",
}
ENTAINMENT_DATA_L = [
    "中文全称", "中文简称", "所属地区", "地址", "地理位置", "类型", "营业时间", "咨询电话", "传真", "邮政编码",
    "投诉电话", "交通信息", "周边信息", "简介", "国别", "省自治区全称", "省自治区简称", "市州全称", "市州简称", "区县全称",
    "区县简称", "地区编码", "url"
]

SHOPPING_DATA = {
    "中文全称": "&",
    "中文简称": "&",
    "所属地区": "&",
    "地址": "&",
    "地理位置": "&",
    "类型": "&",
    "营业时间": "&",
    "特色商品": "&",
    "传真": "&",
    "邮政编码": "&",
    "投诉电话": "&",
    "交通信息": "&",
    "周边信息": "&",
    "简介": "&",
    "国别": "&",
    "省自治区全称": "&",
    "省自治区简称": "&",
    "市州全称": "&",
    "市州简称": "&",
    "区县全称": "&",
    "区县简称": "&",
    "地区编码": "&",
    "url": "&",
}

SHOPPING_DATA_L = [
    "中文全称", "中文简称", "所属地区", "地址", "地理位置", "类型", "营业时间", "特色商品", "传真",
    "邮政编码", "投诉电话", "交通信息", "周边信息", "简介", "国别", "省自治区全称", "省自治区简称", "市州全称",
    "市州简称", "区县全称", "区县简称", "地区编码", "url"
]

# 代理

PROXIES = {
    "http": "http://HY3JE71Z6CDS782P:CE68530DAD880F3B@proxy.abuyun.com:9010",
    "https": "http://HY3JE71Z6CDS782P:CE68530DAD880F3B@proxy.abuyun.com:9010",
}