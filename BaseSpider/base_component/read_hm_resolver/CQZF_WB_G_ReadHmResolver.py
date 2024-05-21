import json
import re
import traceback
from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver


class CQZF_WB_G_ReadHmResolver(HtmlPageResolver):

    def resolver_page(self) -> dict:
        content = {"proj_name": None, "proj_code": None, "proj_item": None, "call_unit": None,
                   "region": None, "ancm_time": None, 'actual_price': None, 'price_info': None,
                   'fund_source': None, "call_unit_address": None, "proj_rel_p": None, "proj_rel_m": None,
                   "agent_unit_name": None, "agent_unit_address": None, "agent_unit_p": None, "agent_unit_m": None,
                   "other_ex": None, "purchase_m": None, "sourse_url": None, "bid_time": None, "provide_unit": None,
                   "provide_address": None, "review_time": None, "review_place": None, "pxy_fee_standard": None,
                   "pxy_fee": None, "title": None, 'web_site': '', 'source_web_name': '', "tenderer_info": None,
                   "bidder_info": None
                   }
        details = []
        page_attr = {}
        try:
            obj = json.loads(self.response_text)
            data = obj['notice']
            html = data['html']
            content['title'] = data['title']
            content['web_site'] = 'https://www.ccgp-chongqing.gov.cn/'
            content['proj_name'] = data['projectName']
            content['proj_code'] = data['projectCode']
            content['proj_item'] = data['projectDirectoryName']
            content['call_unit'] = data['buyerName']
            content['ancm_time'] = data['issueTime']
            content['source_web_name'] = '重庆市政府采购网'
            content['sourse_url'] = self.response_url
            content['region'] = data['districtName']
            if 'agentName' in data:
                content['agent_unit_name'] = data['agentName']
            if 'purchaseDes' in data:
                items = json.loads(data['purchaseDes'])
                for i in items:
                    if 'good' in i:
                        if len(i['good']) > 1:
                            for item in i['good']:
                                if content['actual_price'] != None:
                                    content['actual_price'] += str(',' + item['count'])
                                else:
                                    content['actual_price'] = item['count']
                                if content['provide_unit'] != None:
                                    content['provide_unit'] = str(',' + item['providerName'])
                                else:
                                    content['provide_unit'] = item['providerName']
                                if content['provide_address'] != None:
                                    content['provide_address'] += str(',' + item['proAddress'])
                                else:
                                    content['provide_address'] = item['proAddress']
                                content['other_ex'] = item['remark']
                        else:
                            for item in i['good']:
                                content['actual_price'] = item['count']
                                content['provide_unit'] = item['providerName']
                    else:
                        for item in i['providerList']:
                            if content['provide_unit'] != None:
                                content['provide_unit'] = str(',' + item['providerName'])
                            else:
                                content['provide_unit'] = item['providerName']
                            if content['provide_address'] != None:
                                content['provide_address'] += str(',' + item['proAddress'])
                            else:
                                content['provide_address'] = item['proAddress']

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
            if re.search(r'代理机构联系电话：(.*?)', html):
                content['agent_unit_m'] = re.search(r'代理机构联系电话：(.*?)<', html).group(1)
            if re.search(r'代理服务收费标准：(.*?)', html):
                content['pxy_fee_standard'] = re.search(r'代理服务收费标准：(.*?)<', html).group(1)
            if re.search(r'代理服务费总计：(.*?)', html):
                content['pxy_fee'] = re.search(r'代理服务费总计：(.*?)<', html).group(1)

            if 'openBidTime' in data:
                content['bid_time'] = data['openBidTime']
            else:
                content['bid_time'] = data['bidBeginTime']
            content['purchase_m'] = data['projectPurchaseWayName']
            content['ancm_time'] = data['issueTime']
            page_attr = {'WB_G': content, 'details': details}
        except Exception as e:
            traceback.print_exc()

        return page_attr
