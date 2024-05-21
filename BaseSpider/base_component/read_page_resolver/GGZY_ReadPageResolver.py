import re

from BaseSpider.base_component.PageResolver import PageResolver
from BaseSpider.base_component.entity.PageAttribute import PageAttribute
from BaseSpider.tool.DealDate import get_one_time_from_str
import json
import re

class GGZY_ReadPageResolver(PageResolver):

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
        page_size = len(data)
        # 该位置必须实现
        # page_attribute 参数必须全部有值
        page_attribute = PageAttribute(largest_page, cur_latest_url, page_size, aim_crawl_page, url_list, newest_time,
                                       oldest_time)
        return page_attribute
