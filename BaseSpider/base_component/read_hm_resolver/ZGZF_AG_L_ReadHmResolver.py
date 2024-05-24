import time
from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver
from scrapy import Selector
import re


def AG_L_remove(orstr: str) -> str:
    regex = re.compile(r'<[^>]+>|\n|\t| |\xa0|\r', re.S)
    return regex.sub('', orstr)

CONST_PARAM = {
    # 公告标题参数
    'TITLE': '//*[@class="tc"][1]/text()',
}


class ZGZF_AG_L_ReadHmResolver(HtmlPageResolver):
    all_item = {}

    content = {"title": '默认', "OrgName": None, "OrgCode": None, "UpId": None, "UpName": None, "IdentityState": None,
                        "ImportTime": None, "MainProperty": None, "BusTerm": None, "FoundTime": None, "RegMoney": None,
                        "Linkman": None, "LinkmanName": None, "LinkmanPhone": None, "Remark": None, "LocalProv": None,
                        "LocalProvName": None, "LocalCity": None, "LocalCityName": None, "LocalCounty": None,
                        "LocalCountyName": None, "LocalAddr": None, "PostCode": None, "MainScope": None,
                        "ConcurrentlyScope": None, "TradeType": None, "TradeTypeName": None, "CompanyType": None,
                        "LegalPerson": None, "LegalPersonIdentity": None, "LegalPersonEmail": None,
                        "LegalPersonPhone": None, "RegAddress": None, "EffectAreaId": None, "EffectAreaName": None,
                        'web_site': 'http://jczy.ccgp.gov.cn/gs1/gs1agentreg/pubListIndex.regx',
                        'source_web_name': '中国政府采购网'
                        }

    def resolver_page(self) -> dict:
        self.response_text = Selector(text=self.response_text)

        try:
            content = self.getAgencyList()
            code_dict = []
            at_dict = []
        except:
            return self.page_attr
        else:
            new_page_attr = {'AG_L': content, 'code_dict': code_dict, 'at_dict': at_dict}
            self.page_attr.update(new_page_attr)
            return self.page_attr

    '''
    获取CB_G询价信息
    '''

    def getAgencyList(self):
        response = self.response_text
        content = {}
        content['title'] = '默认'
        # 复杂数据获取
        content['OrgName'] = response.xpath('//*[@id="basePanel"]/div[1]/table[1]//tr[1]/td[1]').get()
        content['OrgCode'] = response.xpath('//*[@id="basePanel"]/div[1]/table[1]//tr[1]/td[2]').get()
        content['UpId'] = ''
        content['UpName'] = ''
        content['IdentityState'] = '1'
        content['ImportTime'] = time.strftime("%Y-%m-%d", time.localtime())
        content['MainProperty'] = ''
        content['BusTerm'] = ''
        content['FoundTime'] = response.xpath('//*[@id="regValidDateStrTR"]').get()
        content['RegMoney'] = ''
        content['Linkman'] = ''
        content['LinkmanName'] = response.xpath('//*[@id="basePanel"]/div[1]/table[1]//tr[2]/td[1]').get()
        content['LinkmanPhone'] = response.xpath('//*[@id="basePanel"]/div[1]/table[1]//tr[2]/td[2]').get()
        content['Remark'] = response.xpath('//*[@id="basePanel"]/div[1]/table[1]//tr[10]/td/text()').get()
        content['LocalProv'] = ''
        content['LocalProvName'] = ''
        content['LocalCity'] = ''
        content['LocalCityName'] = ''
        content['LocalCounty'] = ''
        content['LocalCountyName'] = ''
        content['LocalAddr'] = response.xpath('//*[@id="basePanel"]/div[1]/table[1]//tr[4]/td').get()
        content['PostCode'] = ''
        content['MainScope'] = response.xpath('//*[@id="basePanel"]/div[1]/table[1]//tr[8]/td').get()
        content['ConcurrentlyScope'] = response.xpath('//*[@id="basePanel"]/div[1]/table[1]//tr[9]/td').get()
        content['TradeType'] = ''
        content['TradeTypeName'] = ''
        content['CompanyType'] = ''
        content['LegalPerson'] = response.xpath('//*[@id="basePanel"]/div[1]/table[1]//tr[3]/td').get()
        content['LegalPersonIdentity'] = ''
        content['LegalPersonEmail'] = ''
        content['LegalPersonPhone'] = ''
        content['RegAddress'] = response.xpath('//*[@id="basePanel"]/div[1]/table[1]//tr[4]/td').get()
        content['EffectAreaId'] = ''
        content['EffectAreaName'] = ''
        content['IsConfirm'] = '1'
        content['web_site'] = 'http://jczy.ccgp.gov.cn/gs1/gs1agentreg/pubListIndex.regx'
        content['source_web_name'] = '中国政府采购网'

        # 处理html标签和转义字符
        for k in content.keys():
            content[k] = AG_L_remove(content[k])

        return content

