"""
日志:
2017-11-02: 开始开发请求模块
2017-11-03: 关于思路的问题:
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
    1. api调用此类，完成请求
    2. 要完成请求的过程
    3. 异常输出在log里
    """
    def get_without_params(self, **kwargs):
        """
        作为没有参数的 GET 请求
        1. 参数需要 url, headers, cookies, allow_redirects,
        2. 模仿requests源码里 将allow_redirects 的值为 True, 如果有需要将其设置为False

        """
        kwargs.setdefault('allow_redirects', True)
        response = 'null_html'
        retry = 1
        while retry > 0:
            try:
                res = requests.get(
                    kwargs.get('url'),
                    headers=kwargs.get('headers'),
                    cookies=kwargs.get('cookies'),
                    allow_redirects=kwargs.get('allow_redirects'),
                    timeout=15)
                print(res.text)
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
    get.get_without_params(url='http://www.baidu.com')