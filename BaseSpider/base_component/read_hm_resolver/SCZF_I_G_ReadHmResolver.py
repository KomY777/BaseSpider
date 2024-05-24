import traceback
from datetime import datetime

from scrapy import Selector
import cpca
import re
from BaseSpider.tool.DealDate import get_one_time_from_str
from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver


class SCZF_I_G_ReadHmResolver(HtmlPageResolver):

    def resolver_page(self) -> dict:
        content = {
            'province': None, 'city': None, 'region': None, 'level': None, 'call_unit': None, 'purchase_unit': None,
            'title': None, 'acnm_time': None, 'total_budget': None, 'source_website': None, 'source_url': None
        }
        details = []
        page_attr = {}
        try:
            resp = Selector(text=self.response_text)
            content['title'] = resp.xpath("//h1[@class='info-title']/text()").get().strip()
            content['source_website'] = '四川省政府采购系统'
            content['source_url'] = self.response_url
            content['province'] = '四川省'
            content['city'] = cpca.transform([content['title']]).loc[0, "市"]
            content['region'] = cpca.transform([content['title']]).loc[0, "区"]
            if content['region']:
                content['level'] = 3
            elif content['city']:
                content['level'] = 2
            else:
                content['level'] = 1
            content['call_unit'] = resp.xpath("//p/span[@id='source']/text()").get().strip()[8:14]
            content['purchase_unit'] = resp.xpath("//div[@class='noticeArea']/p[3]/text()").get().strip()
            content['acnm_time'] = get_one_time_from_str(resp.xpath("//span[@id='noticeTime']/i/text()").get().strip())

            ds = resp.xpath("//table[@class='noticeTable']//tr")
            total_budget = 0
            index = 1
            for item in ds:
                if index == 1:
                    index += 1
                    continue
                detail = {'proj_name': item.xpath("./td[2]/text()").get().strip(), 'survey': ''}
                survey = ''
                surveyList = item.xpath("./td[3]/div")
                for surveyItem in surveyList:
                    survey += surveyItem.xpath("./text()").get().strip()
                detail['survey'] = survey
                money = item.xpath("./td[4]/text()").get().strip()
                total_budget += float(money)
                detail['budget'] = '{:.2f}'.format(float(money))
                time = item.xpath("./td[5]/text()").get().strip()
                if '日' not in time:
                    time += '01日'
                detail['purchase_time'] = get_one_time_from_str(time)
                detail['other'] = item.xpath("./td[6]/text()").get().strip()
                details.append(detail)

            content['total_budget'] = '{:.2f}'.format(total_budget)
            page_attr = {'I_G': content, 'details': details}
        except Exception as e:
            traceback.print_exc()

        return page_attr
