import traceback
from datetime import datetime

from scrapy import Selector
import cpca
import re
from BaseSpider.tool.DealDate import get_one_time_from_str
from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver


class HBZF_I_G_ReadHmResolver(HtmlPageResolver):

    def resolver_page(self) -> dict:
        content = {
            'province': None, 'city': None, 'region': None, 'level': None, 'call_unit': None, 'purchase_unit': None,
            'title': None, 'acnm_time': None, 'total_budget': None, 'source_website': None, 'source_url': None
        }
        details = []
        page_attr = {}
        try:
            resp = Selector(text=self.response_text)
            content['title'] = resp.xpath('//*[@id="main"]/div/div/div/div/div[1]/div/div/div[1]/h2/span/text()').get()

            content['call_unit'] = str(resp.xpath(
                '//*[@id="main"]/div/div/div/div/div[1]/div/div/div[1]/div/span[2]/text()').get()).split('：')[1]
            content['acnm_time'] = str(get_one_time_from_str(str(resp.xpath(
                '//*[@id="main"]/div/div/div/div/div[1]/div/div/div[1]/div/span[1]/text()').get())))
            content['purchase_unit'] = content['call_unit']
            content['source_website'] = '湖北省政府采购网'
            content['source_url'] = self.response_url
            content['province'] = '湖北省'
            content['city'] = cpca.transform([content['title']]).loc[0, "市"]
            content['region'] = cpca.transform([content['title']]).loc[0, "区"]
            if content['region']:
                content['level'] = 3
            elif content['city']:
                content['level'] = 2
            else:
                content['level'] = 1

            ds = resp.xpath('//tbody/tr')
            total_budget = 0
            for index, item in enumerate(ds):
                if index == 0:
                    continue

                detail = {}
                detail['proj_name'] = item.xpath('./td[2]/p/text()').get()
                detail['survey'] = item.xpath('./td[3]/p/text()').get()
                money = item.xpath('./td[4]/p/text()').get()
                money = money.replace(',', '').replace('，', '')
                money = float(money)
                total_budget += money
                detail['budget'] = '{:.2f}'.format(money)
                time = re.findall(r'\d+', item.xpath('./td[5]/p/text()').get())
                if len(time) == 2:
                    time.append("01")
                detail['purchase_time'] = str(datetime.strptime('/'.join(time), '%Y/%m/%d'))
                detail['other'] = item.xpath('./td[6]/p/text()').get()
                details.append(detail)

            content['total_budget'] = '{:.2f}'.format(total_budget)
            page_attr = {'I_G': content, 'details': details}
        except Exception as e:
            traceback.print_exc()

        return page_attr
