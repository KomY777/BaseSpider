import math
import re
import json

from BaseSpider.base_component.PageResolver import PageResolver
from BaseSpider.base_component.entity.PageAttribute import PageAttribute
from BaseSpider.tool.DealDate import get_one_time_from_str

'''
必须定义的参数
'''
CONST_PARAM = {
    # 网址前缀
    'BASE_URL': '',
    # 当前最大网页
    'LARGEST_PAGE': '/html/body//*[@class="datagrid-pager pagination"]/table//tr/td[8]/span',
    # 当前网页最新URl
    'CUR_LATEST_URL': '',
    # URL列表XPATH路径
    'LINK_HREFS': '',
    # 当前页面页码
    'AIM_CRAWL_PAGE': '',
}


class ZGZF_AG_L_ReadPageResolver(PageResolver):
    #  该init方法必须在子类（该类）实现
    def __init__(self):
        self.x_base_url = CONST_PARAM.get('BASE_URL')
        self.x_largest_page = CONST_PARAM.get('LARGEST_PAGE')
        self.x_cur_latest_url = CONST_PARAM.get('CUR_LATEST_URL')
        self.x_link_hrefs = CONST_PARAM.get('LINK_HREFS')
        self.x_aim_crawl_page = CONST_PARAM.get('AIM_CRAWL_PAGE')

    # 将页面解析，返回当前页面信息
    def resolver_page(self) -> PageAttribute:
        response_body = str(self.response.body, 'utf-8')
        request_body = str(self.response.request.body, 'utf-8')
        response_jd = json.loads(response_body)

        largest_page = math.ceil(int(response_jd['total']) / 30)
        aim_crawl_page = re.findall(r'page=(.*)&rows', request_body)[0]
        orgId = response_jd['rows'][0]['orgId']
        cur_latest_url = 'http://jczy.ccgp.gov.cn/gs1/gs1agentreg/GS1AgentPubList/agentDetail4pubList.regx?orgId='+orgId
        newest_time = get_one_time_from_str(response_jd['rows'][0]['regValidDateStr'])
        oldest_time = get_one_time_from_str(response_jd['rows'][-1]['regValidDateStr'])

        # link_hrefs = self.response.xpath(self.x_link_hrefs)
        url_list = []


        page_size = 0
        for each in response_jd['rows']:
            page_size += 1
            act_url = 'http://jczy.ccgp.gov.cn/gs1/gs1agentreg/GS1AgentPubList/agentDetail4pubList.regx?orgId='+each['orgId']
            url_list.append(act_url)

        # 该位置必须实现
        # page_attribute 参数必须全部有值
        page_attribute = PageAttribute(largest_page, cur_latest_url, page_size, aim_crawl_page, url_list, newest_time, oldest_time)
        return page_attribute


