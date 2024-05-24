
import traceback

from scrapy import Selector

from BaseSpider.tool.DealDate import get_one_time_from_str
from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver


class SXZF_I_G_ReadHmResolver(HtmlPageResolver):

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
            content['source_website'] = '陕西省政府采购网'
            content['source_url'] = self.response_url
            content['province'] = '陕西省'
            content['city'] = None
            content['region'] = None
            content['level'] = 1
            content['call_unit'] = resp.xpath("//span[@id='source']/text()").get().strip()[6:-1]
            content['purchase_unit'] = resp.xpath("//div[@class='noticeArea']/p[3]/text()").get().strip()
            content['acnm_time'] = get_one_time_from_str(resp.xpath("//span[@id='noticeTime']/i").get())

            ds = resp.xpath("//table[@class='noticeTable']//tr")
            total_budget = 0
            index = 1
            for item in ds:
                if index == 1:
                    index += 1
                    continue
                detail = {'proj_name': item.xpath("./td[2]/text()").get(), 'survey': item.xpath("./td[3]/text()").get()}
                money = item.xpath("./td[4]/text()").get()
                total_budget += float(money)
                detail['budget'] = money
                time = item.xpath("./td[5]/text()").get()
                if '日' not in time:
                    time += '01日'
                detail['purchase_time'] = get_one_time_from_str(time)
                detail['other'] = item.xpath("./td[6]/text()").get()
                details.append(detail)

            content['total_budget'] = '{:.2f}'.format(total_budget)

            page_attr = {'I_G': content, 'details': details}
            print(page_attr)
        except Exception as e:
            traceback.print_exc()

        return page_attr
