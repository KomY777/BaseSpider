from scrapy import FormRequest

from BaseSpider.base_component.RequestResolver import RequestResolver


class SCZF_I_G_ReqPageResolver(RequestResolver):
    """
    允许自定义代码
    """

    def general_param(self) -> dict:
        # 必须在子方法中进行父方法调用
        super().general_param()
        # 以下为自定义代码
        gen_param = {}
        url = 'https://zfcg.scsczt.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=94c965cc-c55d-4f92-8469' \
              '-d5875c68bd04&channel=c5bff13f-21ca-4dac-b158-cb40accd3035&currPage={num}&pageSize=10&noticeType=59' \
              '&regionCode=&purchaseManner=&title=&openTenderCode=&purchaser=&agency=&purchaseNature' \
              '=&operationStartTime=&operationEndTime=&selectTimeName=noticeTime&cityOrArea='.format(num=self.page_num)
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
