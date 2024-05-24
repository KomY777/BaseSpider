from scrapy import Selector

from BaseSpider.base_component.PageResolver import PageResolver
from BaseSpider.base_component.entity.PageAttribute import PageAttribute
from BaseSpider.tool.DealDate import get_one_time_from_str
import json
import re
import requests


def get_time(url: str):
    try:
        resp = requests.get(url)
        resp = Selector(text=resp.text)
        string = resp.xpath('(//div[@class="art_con"]//span)[2]/text()').get()
        return get_one_time_from_str(string)
    except Exception as e:
        print(e)
        return ''

class HBZF_I_G_ReadPageResolver(PageResolver):

    def __init__(self):
        self.url_prefix = 'http://www.ccgp-hubei.gov.cn/'

    def resolver_page(self) -> PageAttribute:
        resp = self.response

        largest_page = resp.xpath("//ul[@class='pagination']/li[last()]/text()").get()
        largest_page = int(re.search(r'共\d+/(\d+)页', largest_page).group(1))
        aim_crawl_page = int(resp.xpath("//ul[@class='pagination']/li[@class='active']/a/text()").get())

        url_list = resp.xpath("(//div[@id='main']//ul)[1]//a/@href").extract()
        url_list = list(self.url_prefix+item for item in url_list)
        cur_latest_url = url_list[0]
        newest_time = get_time(url_list[0])
        oldest_time = get_time(url_list[-1])

        page_size = len(url_list)
        # 该位置必须实现
        # page_attribute 参数必须全部有值
        page_attribute = PageAttribute(largest_page, cur_latest_url, page_size, aim_crawl_page, url_list, newest_time,
                                       oldest_time)
        print(aim_crawl_page, newest_time, oldest_time, largest_page)
        return page_attribute
