from BaseSpider.base_component.PageResolver import PageResolver
from BaseSpider.base_component.entity.PageAttribute import PageAttribute
from BaseSpider.tool.DealDate import stamp2time
import json
import re


class CQZF_WB_G_ReadPageResolver(PageResolver):

    def __init__(self):
        self.url_prefix = 'https://www.ccgp-chongqing.gov.cn/gwebsite/api/v1/notices/stable/'
        self.faliure_list = []

    def resolver_page(self) -> PageAttribute:
        url_list = []
        req_url = self.response.url
        string = json.loads(self.response.body)
        data = string['notices']
        for item in data:
            if re.search(r'终止公告|变更公告|废标公告', item['title']):
                continue
            url_list.append(self.url_prefix + item['id'])
        largest_page = int(string['total']) // len(data)
        aim_crawl_page = int(re.search(r'pi=(\d+)&', req_url).group(1))
        cur_latest_url = self.url_prefix + data[0]['id']
        newest_time = data[0]['issueTime']
        oldest_time = data[-1]['issueTime']
        page_size = len(data)

        # 该位置必须实现
        # page_attribute 参数必须全部有值
        page_attribute = PageAttribute(largest_page, cur_latest_url, page_size, aim_crawl_page, url_list, newest_time,
                                       oldest_time)
        return page_attribute
