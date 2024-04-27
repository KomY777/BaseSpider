import requests
from BaseSpider.settings import SCHEDULE_ADMIN_SERVER_URL, ANNOUCEMENT_DB_SERVER_URL


class ScheduleAdminRequest(object):
    """不记录任何的请求方法"""

    @classmethod
    def request(cls, method, url, data=None, headers=None):  # 这里是要传入的参数，请求方法、接口地址、传参、头文件
        method = method.upper()  # 这里将传入的请求方法统一大写，然后进行判断采用什么方法
        if method == 'POST':
            return requests.post(url=SCHEDULE_ADMIN_SERVER_URL + url, json=data, headers=headers)
        elif method == 'GET':
            return requests.get(url=SCHEDULE_ADMIN_SERVER_URL + url, params=data, headers=headers)


class AnnouncementDBRequest(object):
    """记录Session的方法"""

    def __init__(self):
        self.session = requests.session()  # 初始化一个保存session的方法

    def request(self, url, data=None, headers=None):
        return self.session.post(url=ANNOUCEMENT_DB_SERVER_URL + url, data=data, headers=headers)

    def close(self):
        """断开session连接的方法"""
        self.session.close()
