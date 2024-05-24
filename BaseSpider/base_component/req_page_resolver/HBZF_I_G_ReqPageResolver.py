from urllib.parse import parse_qs, urlencode

from scrapy import FormRequest

from BaseSpider.base_component.RequestResolver import RequestResolver


class HBZF_I_G_ReqPageResolver(RequestResolver):
    """
    允许自定义代码
    """

    def general_param(self) -> dict:
        # 必须在子方法中进行父方法调用
        super().general_param()
        # 以下为自定义代码
        gen_param = {}
        url = 'http://www.ccgp-hubei.gov.cn/notice/cgyxgg/sjcgyxgg//index_{num}.html'.format(num=self.page_num)
        call_back = self.req_attr.call_back
        method = 'GET'

        gen_param['url'] = url
        gen_param['call_back'] = call_back
        gen_param['method'] = method

        return gen_param

    def create_request(self) -> FormRequest:
        # 必须在子方法中进行父方法调用
        super().create_request()

        '''
        以下为允许自定义方法
        '''
        request = FormRequest(
            self.url,
            encoding='utf-8',
            callback=self.m_parse,
            method=self.method,
            dont_filter=self.dont_filter,
        )

        return request

    def m_parse(self, response):
        pass
