from scrapy import FormRequest

from BaseSpider.base_component.RequestResolver import RequestResolver


class SimpleReqResolver(RequestResolver):

    def general_param(self) -> dict:
        # 必须加载父类方法
        super().general_param()

        gen_param = {'url': self.url, 'call_back': self.call_back}
        return gen_param

    def create_request(self) -> FormRequest:
        # 必须加载父类方法
        super().create_request()

        request = FormRequest(
            self.url,
            callback=self.m_parse,
            method='GET',
            dont_filter=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
            },
            meta={'needProxy': False},
        )
        return request

    def m_parse(self, response):
        pass