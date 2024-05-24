import json

from BaseSpider.base_component.PageResolver import PageResolver
from BaseSpider.base_component.entity.PageAttribute import PageAttribute
from BaseSpider.tool.DealDate import stamp2time
import re


class GZZF_I_G_ReadPageResolver(PageResolver):

    def __init__(self):
        self.url_prefix = 'http://www.ccgp-guizhou.gov.cn'

    def resolver_page(self) -> PageAttribute:
        string = json.loads(self.response.body)
        data = string['hits']['hits']
        largest_page = 1000
        aim_crawl_page = int(re.search(r'"pageNo":(\d+)}', bytes.decode(self.response.request.body)).group(1))
        print(aim_crawl_page)
        # url_list = list(self.url_prefix + item['_source']['url'] for item in data)
        url_list = list(self.url_prefix + '/site/detail?articleId=' + str(i) for i in list(item['_source']['articleId'] for item in data))
        cur_latest_url = url_list[0]
        newest_time = stamp2time(int(data[0]['_source']['publishDate']) // 1000)
        oldest_time = stamp2time(int(data[-1]['_source']['publishDate']) // 1000)
        page_size = len(data)

        # 该位置必须实现
        # page_attribute 参数必须全部有值
        page_attribute = PageAttribute(largest_page, cur_latest_url, page_size, aim_crawl_page, url_list, newest_time,
                                       oldest_time)
        return page_attribute

        # largest_page = self.response.xpath("//p[@class='pagination-container']/span[@class='total']/text()").get()
        # aim_crawl_page = self.response.xpath(
        #     "//li[@class='paginationjs-page J-paginationjs-page active']/a/text()").get()
        #
        # url_list = self.response.xpath("//div[@class='list-container']//li/a/@href")
        # url_list = list(self.url_prefix + item for item in url_list)
        # cur_latest_url = url_list[0]
        #
        # newest_time = get_one_time_from_str(self.response.xpath("(//span[@class='date'])[1]/text()").get())
        # oldest_time = get_one_time_from_str(self.response.xpath("(//span[@class='date'])[last()]/text()").get())
        # page_size = 15
        #
        # # 该位置必须实现
        # # page_attribute 参数必须全部有值
        # page_attribute = PageAttribute(largest_page, cur_latest_url, page_size, aim_crawl_page, url_list, newest_time,
        #                                oldest_time)
        # return page_attribute
