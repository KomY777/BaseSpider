import json
import traceback
from BaseSpider.tool.DealDate import stamp2time
from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver
from requests import get
from re import search


class CQZF_I_G_ReadHmResolver(HtmlPageResolver):

    def resolver_page(self) -> dict:
        content = {
            'province': None, 'city': None, 'region': None, 'level': None, 'call_unit': None, 'purchase_unit': None,
            'title': None, 'acnm_time': None, 'total_budget': None, 'source_website': None, 'source_url': None
        }
        details = []

        page_attr = {}
        try:
            url = 'https://www.ccgp-chongqing.gov.cn/yw-gateway/demand/demand/{}/front'
            page_id = search(r'\?id=(.+)$', self.response_url).group(1)
            url = url.format(page_id)
            resp = get(url)
            resp.encoding = 'utf-8'
            resp = resp.text
            obj = json.loads(resp)
            data = obj['data']
            content['title'] = data['title']
            content['source_website'] = '重庆市政府采购网'
            content['source_url'] = self.response_url
            content['province'] = '重庆市'
            content['city'] = None
            content['region'] = data['createRegionName']
            if content['region'] == '重庆市':
                content['region'] = None
            if content['region']:
                content['level'] = 3
            else:
                content['level'] = 1
            content['call_unit'] = data['createOrgName']
            content['purchase_unit'] = data['budgetOrgName']
            content['acnm_time'] = stamp2time(int(data['createTime']) / 1000)
            content['total_budget'] = data['money']

            ds = data['intentionDetaileList']
            for item in ds:
                detail = {}
                detail['proj_name'] = item['title']
                detail['survey'] = item['depict']
                detail['budget'] = item['money']
                detail['purchase_time'] = stamp2time(int(item['expectTime']) / 1000)
                detail['other'] = item['remarks']
                details.append(detail)

            page_attr = {'I_G': content, 'details': details}
        except Exception as e:
            traceback.print_exc()

        return page_attr
