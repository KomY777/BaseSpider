from BaseSpider.base_component.PageResolver import PageResolver
from BaseSpider.base_component.entity.PageAttribute import PageAttribute
from BaseSpider.tool.DealDate import changeAllConn
import json
import re


class CQGP_C_G_ReadPageResolver(PageResolver):

    def __init__(self):
        self.url_prefix = 'https://www.ccgp-chongqing.gov.cn/contractpost/manage_toContractViewPage.action' \
                          '?updateId='

    def resolver_page(self) -> PageAttribute:
        req_url = self.response.url
        string = json.loads(self.response.body)
        data = string['contracts']
        largest_page = int(string['count']) // len(data)
        aim_crawl_page = int(re.search(r'query.current=(\d+)&', req_url).group(1))
        cur_latest_url = self.url_prefix + data[0]['id']
        url_list = list(self.url_prefix + item['id'] for item in data)
        newest_time = changeAllConn(data[0]['announcementTime'])
        oldest_time = changeAllConn(data[-1]['announcementTime'])
        page_size = len(data)

        # 该位置必须实现
        # page_attribute 参数必须全部有值
        page_attribute = PageAttribute(largest_page, cur_latest_url, page_size, aim_crawl_page, url_list, newest_time,
                                       oldest_time)
        return page_attribute