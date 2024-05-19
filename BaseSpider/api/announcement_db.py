from BaseSpider.api.index import AnnouncementDBRequest


instance = AnnouncementDBRequest()


def get_uuid():
    return instance.request(r'/uuid').json()['uuid']


def write_response_to_db(item: dict):
    """
    response数据入库
    :param item:
    :return:
    """
    crawl_html = {'class_type': 'db.sm', 'class_name': 'CrawlHtml', 'dict': str(item)}
    return instance.request('/add_dict_to_sm', crawl_html).json()
