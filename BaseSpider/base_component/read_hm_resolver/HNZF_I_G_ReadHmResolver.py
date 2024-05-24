import traceback
from datetime import datetime

import requests
from scrapy import Selector
import cpca
import re
from BaseSpider.tool.DealDate import get_one_time_from_str
from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver


class HNZF_I_G_ReadHmResolver(HtmlPageResolver):

    def resolver_page(self) -> dict:
        content = {
            'province': None, 'city': None, 'region': None, 'level': None, 'call_unit': None, 'purchase_unit': None,
            'title': None, 'acnm_time': None, 'total_budget': None, 'source_website': None, 'source_url': None
        }
        details = []
        page_attr = {}
        try:
            url = self.response_url
            url_iframe = 'http://' + url.split('/')[2] + '/mvc/viewContent.do?' + url.split('?')[1]
            resp_iframe = requests.get(url_iframe)
            resp_iframe.encoding = 'utf-8'
            resp_iframe = Selector(text=resp_iframe.text)

            resp = Selector(text=self.response_text)
            content['title'] = resp.xpath('/html/body/div[2]/div[2]/table/tr[1]/td/h1/font/text()').extract_first()
            content['call_unit'] = resp_iframe.xpath('//*[@id="yxgk_content"]/p[1]/u[2]/span/text()').extract_first()
            content['acnm_time'] = str(get_one_time_from_str(str(resp.xpath(
                '/html/body/div[2]/div[2]/table/tr[2]/td/h3/text()').extract_first())))
            content['purchase_unit'] = content['call_unit']
            content['source_website'] = '湖南省政府采购网'
            content['source_url'] = url
            content['province'] = '湖南省'
            content['city'] = cpca.transform([content['title']]).loc[0, "市"]
            content['region'] = cpca.transform([content['title']]).loc[0, "区"]
            if content['region']:
                content['level'] = 3
            elif content['city']:
                content['level'] = 2
            else:
                content['level'] = 1

            ds = resp_iframe.xpath('//*[@id="qualitb"]/tbody/tr')
            total_budget = 0
            for index, item in enumerate(ds):
                if index == 0:
                    continue

                detail = {}
                detail['proj_name'] = item.xpath('./td[2]/p/span/text()').extract_first()
                detail['survey'] = item.xpath('./td[3]/p/span/text()').extract_first()
                money = float(re.search(r'\d+', item.xpath('./td[4]/p/span/text()').extract_first()).group(0))
                total_budget += money
                detail['budget'] = '{:.2f}'.format(money)
                time = re.findall(r'\d+', item.xpath('./td[5]/p/span/text()').extract_first())
                time = [time[0][0:4], time[0][4:6]]
                if len(time) == 2:
                    time.append("01")
                detail['purchase_time'] = str(datetime.strptime('/'.join(time), '%Y/%m/%d'))
                detail['other'] = item.xpath('./td[6]/p/span/text()').extract_first()
                details.append(detail)

            content['total_budget'] = '{:.2f}'.format(total_budget)
            page_attr = {'I_G': content, 'details': details}
        except Exception as e:
            traceback.print_exc()

        return page_attr