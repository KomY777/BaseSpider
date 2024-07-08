

from BaseSpider.base_component.PageResolver import PageResolver
from BaseSpider.base_component.entity.PageAttribute import PageAttribute

import json

class ZGZF_I_G_ReqPageResolver(PageResolver):

    def __init__(self):
        self.url_prefix = 'http://cgyx.ccgp.gov.cn/cgyx/pub/pubSearch'

    def resolver_page(self) -> PageAttribute:
        resp = self.response
        url_prefix = 'http://cgyx.ccgp.gov.cn/cgyx/pub/details'
        response = json.loads(resp.body)
        rows = response['rows']
        url_list = []
        for i in rows:
            groupId= i.get('groupId')
            url = url_prefix + '?groupId=' + groupId
            url_list.append(url)

        aim_crawl_page= response['page']
        largest_page = response['totalpage']

        cur_latest_url = url_list[0]
        newest_time = rows[0]['createAt']
        oldest_time = rows[-1]['createAt']
        page_size = len(url_list)
        page_attribute = PageAttribute(int(largest_page), cur_latest_url, int(page_size), int(aim_crawl_page), url_list,
                                       newest_time,
                                       oldest_time)
        return page_attribute



