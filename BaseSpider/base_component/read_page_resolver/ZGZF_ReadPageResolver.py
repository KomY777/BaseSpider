import re

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
    'LARGEST_PAGE': '',
    # 当前网页最新URl
    'CUR_LATEST_URL': '/html/body//*[@class="vT-srch-result-list-bid"]/li[1]/a/@href',
    # URL列表XPATH路径
    'LINK_HREFS': '/html/body//*[@class="vT-srch-result-list-bid"]/li/a/@href',
    # 当前页面页码
    'AIM_CRAWL_PAGE': '',
}


class ZGZF_ReadPageResolver(PageResolver):
    #  该init方法必须在子类（该类）实现
    def __init__(self):
        self.x_base_url = CONST_PARAM.get('BASE_URL')
        self.x_largest_page = CONST_PARAM.get('LARGEST_PAGE')
        self.x_cur_latest_url = CONST_PARAM.get('CUR_LATEST_URL')
        self.x_link_hrefs = CONST_PARAM.get('LINK_HREFS')
        self.x_aim_crawl_page = CONST_PARAM.get('AIM_CRAWL_PAGE')

    # 将页面解析，返回当前页面信息
    def resolver_page(self) -> PageAttribute:
        string = str(self.response.body, 'utf-8')  # 将bytes转换成str
        a = string.find("Pager({")  # 获取下标
        string = string[a + 7:a + 95]  # 获取需要字段
        largest_page = int(re.findall(r'\d+', string)[0])  # 获取字段中的数字
        aim_crawl_page = int(re.findall(r'\d+', string)[1]) + 1
        cur_latest_url = self.response.urljoin(self.response.xpath(self.x_cur_latest_url).get())

        link_hrefs = self.response.xpath(self.x_link_hrefs)
        url_list = []
        link_time = self.response.xpath('//*[@class="vT-srch-result-list-bid"]/li/span/text()').extract()
        link_time = [one for one in link_time if re.findall('^\r\n', one, 1) == []]
        page_size = 0
        for each in link_hrefs:
            page_size += 1
            act_url = self.response.urljoin(each.get())
            url_list.append(act_url)

        # 该位置必须实现
        # page_attribute 参数必须全部有值
        page_attribute = PageAttribute(largest_page, cur_latest_url, page_size, aim_crawl_page, url_list,get_one_time_from_str(link_time[0][:19]),get_one_time_from_str(link_time[-1][:19]))
        return page_attribute


