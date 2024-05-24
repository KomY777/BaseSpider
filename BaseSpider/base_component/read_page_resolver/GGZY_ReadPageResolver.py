import requests
import scrapy
from scrapy import Selector, Request
from BaseSpider.base_component.PageResolver import PageResolver
from BaseSpider.base_component.entity.PageAttribute import PageAttribute
from BaseSpider.tool.DealDate import get_one_time_from_str
import json
import re
import time
import datetime


class GGZY_ReadPageResolver(PageResolver):

    def __init__(self):
        self.session = requests.session()

    # 将页面解析，返回当前页面信息
    def resolver_page(self) -> PageAttribute:
        string = json.loads(self.response.body)
        largest_page = int(string['ttlpage'])
        aim_crawl_page = int(string['currentpage'])
        data = string['data']
        cur_latest_url = data[0]['url']

        url_list = list((re.sub(r'/a/', r'/b/', item['url'], 1) for item in data))
        newest_time = get_one_time_from_str(data[0]['timeShow'])
        oldest_time = get_one_time_from_str(data[-1]['timeShow'])
        #
        # newest_time = (datetime.datetime.strptime(newest_time, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        # oldest_time = (datetime.datetime.strptime(oldest_time, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        newest_time = self.get_time_from_url(url_list[0])
        # time.sleep(1)
        oldest_time = self.get_time_from_url(url_list[-1])

        page_size = len(data)
        # 该位置必须实现
        # page_attribute 参数必须全部有值
        page_attribute = PageAttribute(largest_page, cur_latest_url, page_size, aim_crawl_page, url_list, newest_time,
                                       oldest_time)
        return page_attribute

    def get_time_from_url(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Referer': 'http://www.ggzy.gov.cn/',
        }

        resp = None
        error = 0
        while error < 5:
            try:
                resp = self.session.get(url, headers=headers)
                break
            except:
                print('error')
                self.session = requests.session()
                error += 1
        resp = Selector(text=resp.text)
        time = get_one_time_from_str(resp.xpath('//p[@class="p_o"]//span[1]/text()').extract_first())
        return time
