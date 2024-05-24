from urllib.parse import parse_qs, urlencode

from scrapy import FormRequest

from BaseSpider.base_component.RequestResolver import RequestResolver


class GZZF_I_G_ReqPageResolver(RequestResolver):
    """
    允许自定义代码
    """

    def general_param(self) -> dict:
        # 必须在子方法中进行父方法调用
        super().general_param()

        # 以下为自定义代码
        gen_param = {}
        url = 'http://www.ccgp-guizhou.gov.cn/front/search/category'
        body = '{"districtCode":["520","522","529900"],"utm":"sites_group_front.5b1ba037.0.0.e51c1f00e0c411eca0e9c9663bd9c5bf",' \
               '"categoryCode":"ZcyAnnouncement10016","pageSize":15,"pageNo":' + str(self.page_num) + '}'
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
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "pragma": "no-cache",
            "x-requested-with": "XMLHttpRequest",
            "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37'
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
