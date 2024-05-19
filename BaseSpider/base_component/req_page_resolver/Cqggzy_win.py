import datetime
import json
import time
from random import random
from urllib.parse import parse_qs

from scrapy import FormRequest

from BaseSpider.base_component.RequestResolver import RequestResolver


class Cqggzy_win(RequestResolver):

    def general_param(self) -> dict:
        # 必须在子方法中进行父方法调用
        super().general_param()

        # 以下为自定义代码
        gen_param = {}
        now_time = datetime.datetime.now() - datetime.timedelta(days=90)
        start_time = now_time.strftime("%Y-%m-%d " + "23:59:59")
        end_time = datetime.datetime.now().strftime("%Y-%m-%d " + "23:59:59")
        url = 'https://www.cqggzy.com/interface/rest/esinteligentsearch/getFullTextDataNew'
        # pn 为页数，rn为一页有多少条数据
        body = '{"token":"","pn":' + str((self.page_num - 1) * 20) + ',"rn":20,"sdt":"","edt":"","wd":"","inc_wd":"",' \
                                                                '"exc_wd":"","fields":"","cnum":"001",' \
                                                                '"sort":"{\\"istop\\":\\"0\\",\\"ordernum\\":\\"0\\",' \
                                                                '\\"webdate\\":\\"0\\",\\"rowid\\":\\"0\\"}",' \
                                                                '"ssort":"","cl":10000,"terminal":"","condition":[{' \
                                                                '"fieldName":"categorynum","equal":"014001004",' \
                                                                '"notEqual":null,"equalList":null,"notEqualList":[' \
                                                                '"014001018","004002005","014001015","014005014",' \
                                                                '"014008011"],"isLike":true,"likeType":2}],' \
                                                                '"time":[{"fieldName":"webdate",' \
                                                                '"startTime":"'+start_time+'",' \
                                                                '"endTime":"'+end_time+'"}],"highlights":"",' \
                                                                '"statistics":null,"unionCondition":[],"accuracy":"",' \
                                                                '"noParticiple":"1","searchRange":null,"noWd":true} '
        call_back = self.req_attr.call_back,
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
        # 将字符串转换为字典

        request = FormRequest(
            self.url,
            callback=self.m_parse,
            method=self.method,
            body=self.body,
            dont_filter=self.dont_filter,
            meta={'website': 'cqggzy'},
        )
        return request

    def m_parse(self, response):
        pass