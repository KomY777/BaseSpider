import datetime
from urllib.parse import urlencode, parse_qsl, parse_qs

from scrapy import FormRequest

# 初始网页请求
from BaseSpider.base_component.RequestResolver import RequestResolver
from BaseSpider.settings import USER_AGENT


class ZGZF_I_G_ReqPageResolver(RequestResolver):

    def general_param(self) -> dict:
        super().general_param()

        # 以下为自定义代码
        gen_param = {}
        call_back = self.req_attr.call_back
        body = "type=0&pageSize=10&pageNo=1"
        params = dict(parse_qsl(body))
        method = 'POST'
        form_data = {}
        form_data['type'] = params.get('type')
        form_data['pageSize'] = params.get('pageSize')
        form_data['pageNo'] = self.page_num

        url = "http://cgyx.ccgp.gov.cn/cgyx/pub/pubSearchData"
        gen_param['url'] = url
        gen_param['body'] = urlencode(form_data)
        gen_param['call_back'] = call_back
        gen_param['method'] = method

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
            headers={"User-Agent": USER_AGENT},
            callback=self.m_parse,
            method=self.method,
            formdata=parse_qsl(self.body),
            dont_filter=self.dont_filter,
        )
        return request

    def m_parse(self, response):
        pass
