from scrapy import FormRequest

from BaseSpider.base_component.RequestResolver import RequestResolver
from BaseSpider.settings import USER_AGENT


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
                'User-Agent': USER_AGENT,
            },
            meta=self.meta,
        )
        return request

    def m_parse(self, response):
        pass