import time
from BaseSpider.spiders.spider_info import SpiderInfo
from BaseSpider.tool.RequestTool import HttpRequest
httpRequest = HttpRequest()
DISPATCH_URL = r'http://127.0.0.1:2024/api/spider/'
FILE_SERVER_URL = r'http://localhost:9000/'


def get_spider_info(spider_id):
    spider = SpiderInfo()

    spider_info = httpRequest.request('GET', DISPATCH_URL + 'baseInfo', {'spider_id': spider_id}).json()['data']
    info = spider_info['info']
    spider.id = info['id']
    spider.name = info['name']
    spider.an_type = info['an_type']
    spider.section_page_size = info['section_page_size']
    spider.redis_key = info['name']
    spider.url = info['url']
    spider.body = info['body']
    spider.method = info['method']
    spider.call_back = info['callback']

    spider.start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    spider.param = None

    spider.resolvers = {
        'REQ_URL': [],
        'READ_UL': [],
        'REQ_NEXT_PAGE': [],
        'READ_HM': []
    }
    for resolver in spider_info['resolvers']:
        spider.resolvers[resolver['type']].append(FILE_SERVER_URL + resolver['class_path'])
        spider.resolvers[resolver['type']].append(resolver['class_name'])
    return spider
