from urllib.parse import parse_qs, parse_qsl, urlencode

from scrapy import FormRequest

from BaseSpider.base_component.RequestResolver import RequestResolver


import datetime
GGZY_START_TIME = '2022-03-04'
GGZY_END_TIME = datetime.datetime.now().strftime('%Y-%m-%d')
FORM_DATA = {
    'BID_PLATFORM': '0',
    'DEAL_CITY': '0',
    # 类型 01 工程建设 02 政府采购
    'DEAL_CLASSIFY': '02',
    'DEAL_PLATFORM': '0',
    'DEAL_PROVINCE': '0',
    'DEAL_STAGE': '0000',
    'DEAL_TIME': '05',
    'DEAL_TRADE': '0',
    'PAGENUMBER': '1',
    'SOURCE_TYPE': '1',
    'TIMEBEGIN': GGZY_START_TIME,
    'TIMEBEGIN_SHOW': GGZY_START_TIME,
    'TIMEEND': GGZY_END_TIME,
    'TIMEEND_SHOW': GGZY_END_TIME,
    'isShowAll': '1'
}
import logging


class GGZY_WB_G_ReqPageResolver(RequestResolver):
    """
    允许自定义代码
    """

    def general_param(self) -> dict:
        # 必须在子方法中进行父方法调用
        super().general_param()

        # 以下为自定义代码
        gen_param = {}

        form_data = FORM_DATA
        form_data['PAGENUMBER'] = self.page_num
        form_data['DEAL_STAGE'] = '0202'
        form_data['DEAL_CLASSIFY'] = '02'

        gen_param['url'] = "http://deal.ggzy.gov.cn/ds/deal/dealList_find.jsp"
        gen_param['body'] = urlencode(form_data)
        gen_param['call_back'] = self.req_attr.call_back
        gen_param['method'] = 'POST'

        return gen_param

    def create_request(self) -> FormRequest:
        # 必须在子方法中进行父方法调用
        super().create_request()

        '''
        以下为允许自定义方法

        '''
        # 将字符串转换为字典
        form_data = parse_qs(self.body)

        logging.debug(form_data)

        request = FormRequest(
            self.url,
            callback=self.m_parse,
            method=self.method,
            formdata=form_data,
            dont_filter=self.dont_filter
        )
        return request

    def m_parse(self, response):
        pass
