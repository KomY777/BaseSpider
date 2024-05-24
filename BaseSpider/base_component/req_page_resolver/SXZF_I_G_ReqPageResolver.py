from urllib.parse import parse_qs, urlencode

from scrapy import FormRequest

from BaseSpider.base_component.RequestResolver import RequestResolver


class SXZF_I_G_ReqPageResolver(RequestResolver):
    """
    允许自定义代码
    """

    def general_param(self) -> dict:
        # 必须在子方法中进行父方法调用
        super().general_param()

        # 以下为自定义代码
        gen_param = {}
        url = 'http://www.ccgp-shaanxi.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=a7a15d60-de5b' \
              '-42f2-b35a-7e3efc34e54f&channel=1eb454a2-7ff7-4a3b-b12c-12acc2685bd1&currPage={num}&pageSize=10&noticeType' \
              '=59%2C5E&regionCode=610001&purchaseManner=&title=&openTenderCode=&purchaseNature=&operationStartTime' \
              '=&operationEndTime=&selectTimeName=noticeTime&cityOrArea='.format(num=self.page_num)
        call_back = self.req_attr.call_back
        method = 'GET'

        gen_param['url'] = url
        gen_param['call_back'] = call_back
        gen_param['method'] = method

        return gen_param

    def create_request(self) -> FormRequest:
        # 必须在子方法中进行父方法调用
        super().create_request()

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37"
        }

        '''
        以下为允许自定义方法
        '''
        request = FormRequest(
            self.url,
            encoding='utf-8',
            callback=self.m_parse,
            method=self.method,
            headers=headers,
            dont_filter=self.dont_filter,
        )

        return request

    def m_parse(self, response):
        pass
