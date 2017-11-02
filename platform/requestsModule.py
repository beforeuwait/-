"""
日志:
2017-11-02: 开始开发请求模块
"""
# ////////////////////////////////////////////////////////////////////
# //                          _ooOoo_                               //
# //                         o8888888o                              //
# //                         88" . "88                              //
# //                         (| ^_^ |)                              //
# //                         O\  =  /O                              //
# //                      ____/`---'\____                           //
# //                    .'  \\|     |//  `.                         //
# //                   /  \\|||  :  |||//  \                        //
# //                  /  _||||| -:- |||||-  \                       //
# //                  |   | \\\  -  /// |   |                       //
# //                  | \_|  ''\---/''  |   |                       //
# //                  \  .-\__  `-`  ___/-. /                       //
# //                ___`. .'  /--.--\  `. . ___                     //
# //              ."" '<  `.___\_<|>_/___.'  >'"".                  //
# //            | | :  `- \`.;`\ _ /`;.`/ - ` : | |                 //
# //            \  \ `-.   \_ __\ /__ _/   .-` /  /                 //
# //      ========`-.____`-.___\_____/___.-`____.-'========         //
# //                           `=---='                              //
# //      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        //
# //              佛祖保佑       永无BUG     永不修改                  //
# ////////////////////////////////////////////////////////////////////

import logging
import requests

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='myapp.log',
    filemode='w+'
                    )

class getModule:
    """
    这里作为 GET 请求执行模块
    """
    def get_without_params(self):
        response = 'null_html'
        retry = 1
        while retry > 0:
            try:
                res = requests.get('http://www.basidu.com', timeout=1)
            except Exception as e:
                logging.info('请求过程中出错,%s' % e)
                res = 'error_request'
            retry -= 1
class postModule:
    pass

class getAPI:
    pass

class postAPI:
    pass


if __name__ == '__main__':
    get = getModule()
    get.get_without_params()