from scrapy import FormRequest
import datetime
from BaseSpider.base_component.RequestResolver import RequestResolver



class CQZF_CB_G_ReqPageResolver(RequestResolver):
    """
    允许自定义代码
    """

    def general_param(self) -> dict:
        # 必须在子方法中进行父方法调用
        super().general_param()

        # 以下为自定义代码
        gen_param = {}

        page_number = self.page_num
        now_time = datetime.datetime.now() - datetime.timedelta(days=360)
        START_TIME = now_time.strftime('%Y-%m-%d')
        END_TIME = datetime.datetime.now().strftime('%Y-%m-%d')
        url = "https://www.ccgp-chongqing.gov.cn/gwebsite/api/v1/notices/stable/new?__platDomain__=www.ccgp-chongqing.gov.cn&endDate=" + END_TIME + "&isResult=1&orBidProject=false&pi=" + str(
            page_number) + "&ps=20&startDate=" + START_TIME

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
