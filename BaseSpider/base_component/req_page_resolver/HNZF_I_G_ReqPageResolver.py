from urllib.parse import parse_qs, urlencode

from scrapy import FormRequest

from BaseSpider.base_component.RequestResolver import RequestResolver


class HNZF_I_G_ReqPageResolver(RequestResolver):
    """
    允许自定义代码
    """

    def general_param(self) -> dict:
        # 必须在子方法中进行父方法调用
        super().general_param()
        # 以下为自定义代码
        gen_param = {}
        url = 'http://www.ccgp-hunan.gov.cn/mvc/getnewContentList1.do'
        body = 'column_code=51%2C52&title=&dept=&pub_time1=&pub_time2=&area_id=1&page={num}&pageSize=18'.format(
            num=self.page_num)
        call_back = self.req_attr.call_back
        method = 'POST'

        gen_param['url'] = url
        gen_param['body'] = body
        gen_param['call_back'] = call_back
        gen_param['method'] = method

        return gen_param

    def create_request(self) -> FormRequest:
        # 必须在子方法中进行父方法调用
        super().create_request()

        '''
        以下为允许自定义方法
        '''
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "pragma": "no-cache",
            "x-requested-with": "XMLHttpRequest"
        }
        request = FormRequest(
            self.url,
            encoding='utf-8',
            callback=self.m_parse,
            method=self.method,
            body=self.body,
            headers=headers,
            dont_filter=self.dont_filter,
        )

        return request

    def m_parse(self, response):
        pass
