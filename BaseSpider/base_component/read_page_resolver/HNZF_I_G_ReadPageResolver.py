from scrapy import Request

from BaseSpider.base_component.PageResolver import PageResolver
from BaseSpider.base_component.entity.PageAttribute import PageAttribute
from BaseSpider.tool.DealDate import stamp2time, get_one_time_from_str
import json
import re

class HNZF_I_G_ReadPageResolver(PageResolver):

    def __init__(self):
        self.url_prefix = 'http://www.ccgp-hunan.gov.cn/page/content/content.jsp?columnId='

    def resolver_page(self) -> PageAttribute:
        string = json.loads(self.response.body)
        data = string['rows']
        largest_page = int(string['total']) // len(data)
        body = self.response.request.body
        body = bytes.decode(body, encoding=self.response.request.encoding)
        aim_crawl_page = int(re.search(r'page=(\d+)&', body).group(1))

        url_list = list(self.url_prefix+str(item['COLUMN_ID']) for item in data)
        cur_latest_url = url_list[0]
        if 'STAFF_DATE_ALL' in data[0]:
            newest_time = stamp2time(int(data[0]['STAFF_DATE_ALL']['time'])//1000)
            oldest_time = stamp2time(int(data[-1]['STAFF_DATE_ALL']['time']//1000))
        else:
            newest_time = get_one_time_from_str(data[0]['STAFF_DATE'])
            oldest_time = get_one_time_from_str(data[-1]['STAFF_DATE'])
        page_size = len(data)

        # 该位置必须实现
        # page_attribute 参数必须全部有值
        page_attribute = PageAttribute(largest_page, cur_latest_url, page_size, aim_crawl_page, url_list, newest_time,
                                       oldest_time)
        print(aim_crawl_page, newest_time, oldest_time, largest_page)
        return page_attribute
