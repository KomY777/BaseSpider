import json
import socket
import time

from BaseSpider.spiders.spider_info import SpiderInfo
from BaseSpider.tool.DealDate import get_one_time_from_str
from BaseSpider.tool.RequestTool import HttpSession, HttpRequest

httpSession = HttpSession()
httpRequest = HttpRequest()


def get_spider_info_from_db(spider_id):
    return httpSession.request(r'spider_list_query', {'spider_id': spider_id}).json()['spider']


def get_resolvers_from_db(spider_id):
    return httpSession.request(r'resolver_query', {'spider_id': spider_id}).json()['resolvers']


def get_latest_url_from_db(spider_id):
    return httpSession.request(r'query_latest_url', {'spider_id': spider_id}).json()['latest_url']


def get_uuid():
    return httpSession.request(r'uuid').json()['uuid']


def get_total_num_from_db(spider_id):
    return httpSession.request(r'query_total_num', {'spider_id': spider_id}).json()['total_num']


def get_spider_await_from_db(spider_id):
    return httpSession.request(r'spider_await_query', {'spider_id': spider_id}).json()


def get_spider_await_status_from_db(spider_id):
    return httpSession.request(r'spider_await_status_query', {'spider_id': spider_id}).json()


def get_spider_model_from_db(spider_id):
    return httpSession.request('spider_model_query', {'spider_id': spider_id}).json()['spider']


def get_spider_init_from_db(spider_id):
    return httpSession.request('spider_init_query', {'spider_id': spider_id}).json()


def sas_update_aim_number(spider_id, aim_num):
    return httpSession.request('sas_update_aim_number', {'aim_num': aim_num, 'spider_id': spider_id}).json()


def set_spider_status(spider_id, status):
    httpSession.request(r'sas_update_status', {'status': status, 'spider_id': spider_id}).json()


def add_history(spider_id, spider_info, data_attr, predict_num, result, istrue_end='true'):
    crawl_history_id = httpSession.request('sas_update_aichis_idm_number', ).json()['history_id']
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    crawl_history = {'id': crawl_history_id, 'spider_id': spider_id, 'crawl_aim_url': data_attr.get('cur_latest_url'),
                     'redis_key': spider_info.redis_key, 'aim_crawl_num': predict_num,
                     'act_crawl_num': data_attr.get('com_page'), 'server_id': ip, 'server_name': ip,
                     'start_time': data_attr.get('start_time'),
                     'update_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                     'result': result, 'istrue_end': istrue_end}
    httpSession.request('chis_add', crawl_history)


def write_response_to_db(item: dict):
    """
    response数据入库
    :param item:
    :return:
    """
    crawl_html = {'class_type': 'db.sm', 'class_name': 'CrawlHtml', 'dict': str(item)}
    return httpSession.request('add_dict_to_sm', crawl_html).json()


def update_spider_status(data):
    httpSession.request(r'sas_update_spider_await_status', {'data': json.dumps(data)})


def add_spider_history(data):
    httpSession.request('chis_add', {'data': json.dumps(data)})


def update_spider_history(data):
    httpSession.request('chis_update', data)


def get_spider_info(spider_id):
    """
    # todo 获取爬虫信息
    :param spider_id:
    :return:
    """
    spider = SpiderInfo()

    info = get_spider_info_from_db(spider_id)
    spider.id = info['id']
    spider.name = info['name']
    spider.an_type = info['an_type']

    # spider.total_num = get_total_num_from_db(spider_id)

    spider.section_page_size = get_spider_await_from_db(spider_id)['section_page_size']

    status = get_spider_await_status_from_db(spider_id)
    spider.latest_url = status['latest_url']
    spider.status = status['status']
    spider.aim_number = status['aim_number']
    spider.crawled_section_num = status['crawled_section_num']

    spider.latest_time = get_one_time_from_str(status['latest_time'])
    spider.cur_time = get_one_time_from_str(status['cur_time'])
    spider.earliest_time = get_one_time_from_str(status['earliest_time'])
    spider.start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    spider.history_id = status['crawl_history_id']
    model = get_spider_model_from_db(spider_id)
    spider.redis_key = model['base_key']

    init = get_spider_init_from_db(spider_id)
    spider.url = init['url']
    spider.body = init['body']
    spider.method = init['method']
    spider.call_back = init['callback']

    spider.param = None

    spider.resolvers = {
        'REQ_URL': [],
        'READ_UL': [],
        'REQ_NEXT_PAGE': [],
        'READ_HM': []
    }
    resolvers = get_resolvers_from_db(spider_id)
    for resolver in resolvers:
        spider.resolvers[resolver['type']].append('BaseSpider.base_component.' + resolver['class_path'])
    # todo 解析器缺省设置
    return spider


def get_all_spider_info(spider_id):
    spider = SpiderInfo()

    spider_info = httpRequest.request('GET', 'baseInfo', {'spider_id': spider_id}).json()['data']
    info = spider_info['info']
    spider.id = info['id']
    spider.name = info['name']
    spider.an_type = info['an_type']
    spider.section_page_size = info['section_page_size']
    spider.redis_key = info['id']
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
        spider.resolvers[resolver['type']].append('http://localhost:9000/' + resolver['class_path'])
        spider.resolvers[resolver['type']].append(resolver['class_name'])
    return spider
