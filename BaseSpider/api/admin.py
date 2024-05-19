import datetime
import time
from BaseSpider.spiders.spider_info import SpiderInfo
from BaseSpider.api.index import ScheduleAdminRequest
FILE_SERVER_URL = r'http://localhost:9000/'


def get_spider_info(spider_id):
    spider = SpiderInfo()

    spider_info = ScheduleAdminRequest.request('GET', '/spider/baseInfo', {'spider_id': spider_id}).json()['data']
    info = spider_info['info']
    spider.id = info['id']
    spider.name = info['name']
    spider.an_type = info['an_type']
    spider.url = info['url']
    spider.body = info['body']
    spider.method = info['method']
    spider.call_back = info['callback']

    spider.start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    spider.param = None

    spider.resolvers = {
        'REQ_DETAIL': [],
        'READ_PAGE': [],
        'REQ_PAGE': [],
        'READ_HM': []
    }
    for resolver in spider_info['resolvers']:
        spider.resolvers[resolver['type']].append('BaseSpider.base_component.' + resolver['class_path'])
    return spider

def update_task_status(data):
    return ScheduleAdminRequest.request('POST', '/task/update_task_status', data).json()


# if __name__ == '__main__':
#     update_task_status({
#         'task_id': '0DC739149A74400CA544CAA7',
#         'status': 3,
#         'total_crawl': 100,
#         'total_resolve': 100,
#         'log_url': '/logs/default/AnnouncementSpider/d4471b20021f11efa36dacde48001122.log',
#         'last_crawl_url': 'xxx',
#         'last_crawl_time': int(datetime.datetime.now().timestamp())
#     })
