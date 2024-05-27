
from scrapy import FormRequest

from BaseSpider.base_component.RequestResolver import RequestResolver


class CQGP_C_G_ReqPageResolver(RequestResolver):
    """
    允许自定义代码
    """

    def general_param(self) -> dict:
        # 必须在子方法中进行父方法调用
        super().general_param()

        # 以下为自定义代码
        gen_param = {}

        page_number = self.page_num
        url = "https://www.ccgp-chongqing.gov.cn/contractpost/view_queryContractsHome.action?__platDomain__=www.ccgp-chongqing.gov.cn&query.pageSize=10&query.current={}&query.state=2&isSearch=flase".format(
            page_number)

        gen_param['url'] = url
        gen_param['call_back'] = self.req_attr.call_back
        gen_param['method'] = 'GET'

        return gen_param

    def create_request(self) -> FormRequest:
        # 必须在子方法中进行父方法调用
        super().create_request()

        '''
        以下为允许自定义方法

        '''
        # 将字符串转换为字典

        request = FormRequest(
            self.url,
            callback=self.m_parse,
            method=self.method,
            dont_filter=self.dont_filter
        )
        return request

    def m_parse(self, response):
        pass
