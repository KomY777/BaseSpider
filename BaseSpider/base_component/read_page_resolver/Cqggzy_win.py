import time

from scrapy import Request

from BaseSpider.base_component.PageResolver import PageResolver
from BaseSpider.base_component.entity.PageAttribute import PageAttribute
from BaseSpider.tool.DealDate import get_one_time_from_str
import json
import re

class Cqggzy_win(PageResolver):

    def __init__(self):
        self.url_prefix = 'https://www.cqggzy.com/'

    def resolver_page(self) -> PageAttribute:
        resp = self.response
        url_prefix = 'https://www.cqggzy.com/'
        response = resp.body
        response = json.loads(response)
        response = response['result']['records']
        url_list = []
        for i in response:
            category = i['categorynum']
            infoid = i['infoid']
            infodate = i['infodate']
            infodata = re.split(" ", infodate)[0]
            infodata = infodata.replace("-", "")
            url = url_prefix + '/xxhz/014001/014001004/' + category + '/' + infodata + '/' + infoid + '.html'
            url_list.append(url)
        if len(self.response.request.body) != 0:
            aim_crawl_page = int(json.loads(bytes.decode(self.response.request.body))['pn'])/20+1
        else:
            aim_crawl_page = 1
        largest_page = 40
        cur_latest_url = url_list[0]
        newest_time = response[0]['infodate']
        oldest_time = response[-1]['infodate']
        page_size = len(url_list)
        page_attribute = PageAttribute(int(largest_page), cur_latest_url, int(page_size), int(aim_crawl_page), url_list,
                                       newest_time,
                                       oldest_time)
        return page_attribute



