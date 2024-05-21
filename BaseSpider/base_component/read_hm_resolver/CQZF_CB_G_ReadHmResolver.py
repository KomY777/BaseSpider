import json
import re
import traceback
from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver


class CQZF_CB_G_ReadHmResolver(HtmlPageResolver):

    def resolver_page(self) -> dict:
        content = {"proj_name": None, "proj_code": None, "proj_item": None, "call_unit": None,
                   "region": None, "ancm_time": None, "budget": None, "proj_rel_p": None,
                   "proj_rel_m": None, "agent_unit_p": None, "agent_unit_m": None, "tender_place": None,
                   "bid_sale_m": None, "bid_sale_op_time": None, "bid_sale_en_time": None,
                   "bid_sale_place": None, "bid_price": None, "bid_place": None, "other_ex": None,
                   "purchase_m": None, "sourse_url": None, "bid_time": None, "title": None,
                   "agent_unit_name": None, "agent_unit_address": None, "call_unit_address": None,
                   "source_web_name": None, 'web_site': 'https://www.ccgp-chongqing.gov.cn/', 'disabled': 0,
                   }
        details = []
        page_attr = {}
        try:
            obj = json.loads(self.response_text)
            data = obj['notice']
            html = data['html']
            content['title'] = data['title']
            content['proj_name'] = data['projectName']
            content['proj_code'] = data['projectCode']
            content['proj_item'] = data['projectDirectoryName']
            content['call_unit'] = data['buyerName']
            content['ancm_time'] = data['issueTime']
            content['source_web_name'] = '重庆市政府采购网'
            content['sourse_url'] = self.response_url
            content['region'] = data['districtName']
            content['budget'] = data['projectBudget']
            if 'agentName' in data:
                content['agent_unit_name'] = data['agentName']
            if 'purchaseDes' in data:
                items = json.loads(data['purchaseDes'])
                for i in items:
                    for item in i['good']:
                        content['proj_item'] += item['title'].replace('/', '-')
            if 'buyerJson' in data:
                call_unit = json.loads(data['buyerJson'])[0]
                content['call_unit_address'] = call_unit['buyerAddress']
                content['proj_rel_p'] = call_unit['buyerPerson']
                content['proj_rel_m'] = call_unit['buyerTel']
            else:
                if re.search(r'采购人地址：(.*?)', html):
                    content['call_unit_address'] = re.search(r'采购人地址：(.*?)<', html).group(1)
                if re.search(r'采购人电话：(.*?)', html):
                    content['proj_rel_m'] = re.search(r'采购人电话：(.*?)<', html).group(1)
            if re.search(r'代理机构地址：(.*?)', html):
                content['agent_unit_address'] = re.search(r'代理机构地址：(.*?)<', html).group(1)
            if re.search(r'代理机构经办人：(.*?)', html):
                content['agent_unit_p'] = re.search(r'代理机构经办人：(.*?)<', html).group(1)
            if re.search(r'代理机构电话：(.*?)', html):
                content['agent_unit_m'] = re.search(r'代理机构电话：(.*?)<', html).group(1)
            if re.search(r'投标文件递交地点：(.*?)', html):
                content['tender_place'] = re.search(r'投标文件递交地点：(.*?)<', html).group(1)
            if re.search(r'方式或事项：(.*?)', html):
                content['bid_sale_m'] = re.search(r'方式或事项：(.*?)<', html).group(1)
            if 'openBidTime' in data:
                content['bid_sale_op_time'] = data['openBidTime']
                content['bid_time'] = data['openBidTime']
            elif 'bidBeginTime' in data:
                content['bid_sale_op_time'] = data['bidBeginTime']
                content['bid_time'] = data['bidBeginTime']
            content['bid_sale_en_time'] = data['bidEndTime']
            if 'bidEndTime' in data:
                content['bid_end_time'] = data['bidEndTime']
            content['purchase_m'] = data['projectPurchaseWayName']
            page_attr = {'CB_G': content, 'details': details}
        except Exception as e:
            traceback.print_exc()

        return page_attr
