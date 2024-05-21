import re
import traceback
import BaseSpider.base_component.read_hm_resolver.util.GGZY_util as util

from BaseSpider.base_component.read_hm_resolver.util import getValue
from BaseSpider.base_component.read_hm_resolver.util.getValue import standardization, \
    unit_name_standardization
from BaseSpider.tool import DealDate
from BaseSpider.tool.param_tool import process_dict_call_GGZY
from BaseSpider.tool.DealDate import get_one_time_from_str
from BaseSpider.tool.judge_tool.content_count import content_count
from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver
from scrapy import Selector


class GGZY_CB_G_ReadHmResolver(HtmlPageResolver):
    code = 'true'
    result = ''
    content = {"proj_name": None, "proj_code": None, "proj_item": None, "call_unit": None,
               "region": None, "ancm_time": None, "budget": None, "proj_rel_p": None,
               "proj_rel_m": None, "agent_unit_p": None, "agent_unit_m": None, "tender_place": None,
               "bid_sale_m": None, "bid_sale_op_time": None, "bid_sale_en_time": None,
               "bid_sale_place": None, "bid_price": None, "bid_place": None, "other_ex": None,
               "purchase_m": None, "sourse_url": None, "bid_time": None, "title": None,
               "agent_unit_name": None, "agent_unit_address": None, "purchasing_unit_name": None,
               "call_unit_address": None,
               'web_site': 'http://www.ggzy.gov.cn/', 'source_web_name': '中国公共资源交易平台'
               }
    count_list = ['proj_name', 'call_unit', 'ancm_time', 'budget', 'proj_rel_p', 'proj_rel_m', 'agent_unit_name',
                  'agent_unit_address', 'agent_unit_p', 'agent_unit_m', 'tender_place', 'bid_sale_m',
                  'bid_sale_op_time', 'bid_sale_en_time', 'bid_sale_place', 'bid_price', 'sourse_url', 'bid_time',
                  'title', 'web_site', 'source_web_name']

    def __int__(self):
        self.response_text = Selector(text=self.response_text)

    def resolver_page(self) -> dict:
        try:
            title = self.response_text.xpath('//h4[@class="h4_o"]/text()').extract_first()
            if title and re.search('更正|变更|中标|开标', title):
                return {}
            content = standardization(self.getInquiryGovernment())
            code_dict = self.getCodeHtml()
            at_dict = self.get_attach(self.response_text)
            call_unit = self.getCallBidUnit(content)

        except Exception:
            traceback.print_exc()
            return self.page_attr

        else:
            new_page_attr = {'CB_G': content, 'code_dict': code_dict, 'at_dict': at_dict, 'call_unit': call_unit}
            self.page_attr.update(new_page_attr)
            return self.page_attr

    def getCallBidUnit(self, content):
        call_unit = {}
        if 'call_unit' in content and not content['call_unit'] == '':
            call_unit['name'] = content['call_unit']
            call_unit['code'] = content['call_unit']
        else:
            return {}
        if 'call_unit_address' in content and not content['call_unit_address'] == '':
            call_unit['address'] = content['call_unit_address']
        else:
            return {}

        return call_unit

    def getCodeHtml(self):
        code_dict = {}

        code_dict['url'] = self.response_url
        code_dict['file_type'] = self.response_url[self.response_url.rfind('.') + 1:]
        code_dict['file_size'] = '-1'
        code_dict['local_path'] = '暂无'
        code_dict['code'] = self.response_text.xpath('//div[@class="detail"]').extract_first()

        return code_dict

    def getInquiryGovernment(self):
        response = self.response_text


        text = response.response.body.decode('utf-8')
        html_list = util.parseHtml_list(text)
        item = util.parse2dict(html_list)
        dict_title = util.parse2dict_title(html_list)

        content = process_dict_call_GGZY(item)
        content.update(util.process_callbid_file(dict_title))
        content.update(util.process_callbid_tender(dict_title))
        content.update(util.process_callbid_open(dict_title))
        content.update(util.process_callbid_other_ex(dict_title))
        content.update(util.process_callbid_money(dict_title))
        content.update(util.process_callbid_contact(dict_title))
        content['proj_code'] = util.search_code(html_list)

        # 复杂数据获取
        content['title'] = response.xpath('//h4[@class="h4_o"]/text()').extract_first()
        content['proj_name'] = re.sub(r'公告|开标公告|标段', '', content['title'])
        content['proj_item'] = '政府采购'
        content['ancm_time'] = get_one_time_from_str(
            response.xpath('//p[@class="p_o"]//span[1]/text()').extract_first())
        content['sourse_url'] = self.response_url
        content['web_site'] = 'http://www.ggzy.gov.cn/'
        content['purchase_m'] = content['purchase_m'] if content['purchase_m'] else '公开招标'
        content['source_web_name'] = '公共资源交易平台'
        ex = response.xpath('//label[@id="platformName"]/text()').extract_first()
        content['region'] = util.get_region_from_str(content['title'], ex)

        # 数据格式修改
        content['ancm_time'] = DealDate.get_one_time_from_str(content['ancm_time'])
        content['call_unit'] = unit_name_standardization(content['call_unit'])
        content['agent_unit_name'] = unit_name_standardization(content['agent_unit_name'])
        content['bid_sale_op_time'] = DealDate.get_one_time_from_str(content['bid_sale_op_time'])
        content['bid_sale_en_time'] = DealDate.get_one_time_from_str(content['bid_sale_en_time'])
        content['bid_time'] = DealDate.get_one_time_from_str(content['bid_time'])
        content['bid_end_time'] = DealDate.get_one_time_from_str(content['bid_end_time'])
        content['bid_price'] = getValue.change_money(content['bid_price'])
        content['budget'] = getValue.change_money(content['budget'])

        content['resolution_rate'] = '%.2f' % content_count(content, self.count_list)

        return content

    '''
    获取附件信息
    '''

    def get_attach(self, response_text):
        file_name_list = response_text.xpath("//a[not(text()='原文链接地址')]/text()").extract()
        file_url_list = response_text.xpath("//a[not(text()='原文链接地址')]/@href").extract()
        if not file_url_list or not file_url_list:
            return []

        if not len(file_url_list) == len(file_name_list):
            return []

        at_dict = []
        for i in range(len(file_url_list)):
            item = {'url': file_url_list[i],
                    'file_name': file_name_list[i],
                    'file_type': file_name_list[i][file_name_list[i].rfind('.') + 1:],
                    'file_size': -1,
                    'local_path': '暂无'}
            if item['file_type'] not in ['pdf', 'txt', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']:
                continue
            at_dict.append(item)
        return at_dict
