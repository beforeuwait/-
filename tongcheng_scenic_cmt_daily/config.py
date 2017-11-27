'''作为配置文件的存在'''
import os
os.chdir(os.path.split(os.path.realpath(__file__))[0])
# path
DATA_PATH = 'Data'
DATA_LIST = 'DataList'
# file
NEW_SCENIC_LIST = os.path.join(os.path.abspath(DATA_LIST),'new_tc_scenic_list.txt')
CITY_LIST_PATH = os.path.join(os.path.abspath(DATA_LIST),'tc_city_list.txt')
SCENIC_PATH = os.path.join(os.path.abspath(DATA_LIST),'tc_scenic_list.txt')
SCENIC_CMT_EVERYDAY = os.path.join(os.path.abspath(DATA_PATH),'tc_scenic_everyday.txt')
SCENIC_CMT_HISTORY = os.path.join(os.path.abspath(DATA_PATH), 'tc_scenic_history.txt')
