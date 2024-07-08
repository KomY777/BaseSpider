from scrapy import FormRequest, Request

from BaseSpider.base_component.RequestResolver import RequestResolver
from BaseSpider.settings import USER_AGENT


class req(RequestResolver):

    def general_param(self) -> dict:
        # 必须加载父类方法
        super().general_param()

        gen_param = {'url': self.url, 'call_back': self.call_back}
        return gen_param

    def create_request(self) -> Request:
        # 必须加载父类方法
        super().create_request()

        request = Request(
            self.url,
            callback=self.m_parse,
            method='GET',
            dont_filter=True,
            headers={
                'User-Agent': USER_AGENT,
            },
            meta={"middleware": "requests"},
        )
        return request

    def m_parse(self, response):
        pass
