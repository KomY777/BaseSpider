from BaseSpider.base_component.PageResolver import PageResolver
from BaseSpider.base_component.entity.PageAttribute import PageAttribute
from BaseSpider.tool.DealDate import get_one_time_from_str
import json
import re

class SXZF_I_G_ReadPageResolver(PageResolver):

    def __init__(self):
        self.url_prefix = 'http://www.ccgp-shaanxi.gov.cn/freecms'

    def resolver_page(self) -> PageAttribute:
        req_url = self.response.url
        string = json.loads(self.response.body)
        data = string['data']
        largest_page = int(string['total']) // len(data)
        aim_crawl_page = int(re.search(r'currPage=(\d+)&', req_url).group(1))

        cur_latest_url = self.url_prefix + data[0]['htmlpath']

        url_list = list(self.url_prefix+item['htmlpath'] for item in data)
        newest_time = get_one_time_from_str(data[0]['addtimeStr'])
        oldest_time = get_one_time_from_str(data[-1]['addtimeStr'])
        page_size = len(data)
        # 该位置必须实现
        # page_attribute 参数必须全部有值
        page_attribute = PageAttribute(largest_page, cur_latest_url, page_size, aim_crawl_page, url_list, newest_time,
                                       oldest_time)
        print(aim_crawl_page, newest_time, oldest_time, largest_page)
        return page_attribute
