import json
import traceback
from decimal import Decimal

import cpca
from scrapy import Selector

from BaseSpider.tool.DealDate import get_one_time_from_str
from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver
from requests import get
import re


class GZZF_I_G_ReadHmResolver(HtmlPageResolver):

    def resolver_page(self) -> dict:
        print(self.response_url)
        content = {
            'province': None, 'city': None, 'region': None, 'level': None, 'call_unit': None, 'purchase_unit': None,
            'title': None, 'acnm_time': None, 'total_budget': None, 'source_website': None, 'source_url': None
        }
        details = []

        page_attr = {}
        try:
            resp = Selector(text=self.response_text)
            txt = resp.xpath("//input[@name='articleDetail']/@value").get()
            txt = json.loads(txt)
            resp = Selector(text=txt['content'])
            content['title'] = txt['title']
            content['source_website'] = '贵州省政府采购网'
            content['source_url'] = self.response_url
            content['province'] = '贵州省'
            content['city'] = cpca.transform([content['title']]).loc[0, "市"]
            content['region'] = cpca.transform([content['title']]).loc[0, "区"]
            if content['region']:
                content['level'] = 3
            elif content['city']:
                content['level'] = 2
            else:
                content['level'] = 1
            content['call_unit'] = txt['author']
            content['purchase_unit'] = content['call_unit']
            content['acnm_time'] = get_one_time_from_str(txt['publishDate'])

            ds = resp.xpath('//tbody/tr')
            total_budget = 0
            for item in ds:
                detail = {}
                detail['proj_name'] = item.xpath("./td[@class='code-purchaseProjectName']/text()").get()
                detail['survey'] = item.xpath("./td[@class='code-purchaseRequirementDetail']/text()").get()
                money = item.xpath("./td[@class='code-budgetPrice']/text()").get()
                money = money.replace(',', '').replace('，', '')
                money = Decimal(money) / 10000
                total_budget += money
                detail['budget'] = '{:.2f}'.format(money)
                time = item.xpath("./td[@class='code-estimatedPurchaseTime']/text()").get()
                if '日' not in time:
                    time += '1日'
                detail['purchase_time'] = get_one_time_from_str(time)
                detail['other'] = item.xpath("./td[@class='code-remark']/text()").get()
                details.append(detail)

            content['total_budget'] = '{:.2f}'.format(total_budget)

            page_attr = {'I_G': content, 'details': details}
        except Exception as e:
            traceback.print_exc()

        return page_attr
