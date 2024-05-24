from BaseSpider.base_component.PageResolver import PageResolver
from BaseSpider.base_component.entity.PageAttribute import PageAttribute
from BaseSpider.tool.DealDate import stamp2time
import json
import re

class CQZF_I_G_ReadPageResolver(PageResolver):

    def __init__(self):
        self.url_prefix = 'https://www.ccgp-chongqing.gov.cn/stock-resources-front/intentionView?id='

    def resolver_page(self) -> PageAttribute:
        req_url = self.response.url
        string = json.loads(self.response.body)
        data = string['data']
        largest_page = int(string['count']) // len(data)
        aim_crawl_page = int(re.search(r'page=(\d+)&', req_url).group(1))

        cur_latest_url = self.url_prefix + data[0]['id']

        url_list = list(self.url_prefix+item['id'] for item in data)
        newest_time = stamp2time(int(data[0]['createTime'])//1000)
        oldest_time = stamp2time(int(data[-1]['createTime']//1000))
        page_size = len(data)

        # 该位置必须实现
        # page_attribute 参数必须全部有值
        page_attribute = PageAttribute(largest_page, cur_latest_url, page_size, aim_crawl_page, url_list, newest_time,
                                       oldest_time)
        return page_attribute
