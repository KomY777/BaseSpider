import re
import BaseSpider.base_component.read_hm_resolver.util.GGZY_util as util

from BaseSpider.base_component.read_hm_resolver.util import getValue
from BaseSpider.base_component.read_hm_resolver.util.getValue import standardization, \
    unit_name_standardization
from BaseSpider.tool import DealDate
from BaseSpider.tool.param_tool import engineering_dict_call
from BaseSpider.tool.DealDate import get_one_time_from_str
from BaseSpider.tool.judge_tool.content_count import content_count
from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver
from scrapy import Selector



class GGZY_CB_E_ReadHmResolver(HtmlPageResolver):
    code = 'true'
    result = ''
    countlist = ['proj_name', 'title', 'proj_place', 'resource_from', 'ET', 'bid_sale_m',
                 'bid_sale_op_time', 'bid_sale_en_time', 'bid_price', 'bid_sale_place', 'proj_unit',
                 'proj_rel_p', 'proj_rel_m', 'agent_unit', 'agent_unit_p', 'agent_unit_m',
                 'ancm_time', 'sourse_url', 'source_web_name', 'web_site']


    def resolver_page(self) -> dict:
        self.response_text = Selector(text=self.response_text)
        try:
            title = self.response_text.xpath('//h4[@class="h4_o"]/text()').extract_first()
            if title and re.search('更正|变更|中标|开标', title):
                return {}
            content = standardization(self.getInquiryGovernment())
            code_dict = self.getCodeHtml()
            at_dict = self.get_attach(self.response_text)
            call_unit = self.getCallBidUnit(content)

        except Exception:
            return self.page_attr

        else:
            new_page_attr = {'CB_E': content, 'code_dict': code_dict, 'at_dict': at_dict, 'call_unit': call_unit}
            self.page_attr.update(new_page_attr)
            return self.page_attr

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
        dict_title = util.parse2dict_title_gcjs(html_list)

        content = engineering_dict_call(item)
        # 复杂数据获取
        content['title'] = response.xpath('//h4[@class="h4_o"]/text()').extract_first()
        content['proj_name'] = content['title']
        content['ancm_time'] = get_one_time_from_str(
            response.xpath('//p[@class="p_o"]//span[1]/text()').extract_first())
        content['sourse_url'] = self.response_url
        content['web_site'] = 'http://www.ggzy.gov.cn/'
        content['source_web_name'] = '公共资源交易平台'
        content['proj_code'] = util.search_code(html_list)
        ex = response.xpath('//label[@id="platformName"]/text()').extract_first()
        content['region'] = util.get_region_from_str(content['title'], ex)

        content.update(util.process_callbid_file_gcjs(dict_title))
        content.update(util.process_callbid_tender_gcjs(dict_title))
        content.update(util.process_callbid_open(dict_title))
        content.update(util.process_callbid_other_ex(dict_title))
        content.update(util.process_callbid_contact_gcjs(dict_title))

        # 数据格式修改
        content['ancm_time'] = DealDate.get_one_time_from_str(content['ancm_time'])
        content['proj_unit'] = unit_name_standardization(content['proj_unit'])
        content['agent_unit'] = unit_name_standardization(content['agent_unit'])
        content['bid_sale_op_time'] = DealDate.get_one_time_from_str(content['bid_sale_op_time'])
        content['bid_sale_en_time'] = DealDate.get_one_time_from_str(content['bid_sale_en_time'])
        content['bid_end_time'] = DealDate.get_one_time_from_str(content['bid_end_time'])
        content['bid_price'] = getValue.change_money(content['bid_price'])

        content['resolution_rate'] = '%.2f' % content_count(content, self.countlist)

        return content

    '''
    获取附件信息
    '''

    def get_attach(self, response_text):
        file_name_list = response_text.xpath("//a[not(text()='原文链接地址')]/text()").extract()
        file_url_list = response_text.xpath("//a[not(text()='原文链接地址')]/@href").extract()

        at_dict = []
        for i in range(len(file_url_list)):
            item = {'url': file_url_list[i],
                    'file_name': file_name_list[i],
                    'file_type': file_name_list[i][file_name_list[i].rfind('.') + 1:],
                    'file_size': -1,
                    'local_path': '暂无'}
            at_dict.append(item)
        return at_dict

    def getCallBidUnit(self, content):
        call_unit = {}
        if 'proj_unit' in content and not content['proj_unit'] == '':
            call_unit['name'] = content['proj_unit']
            call_unit['code'] = content['proj_unit']
        else:
            return {}
        if 'proj_unit_address' in content and not content['proj_unit_address'] == '':
            call_unit['address'] = content['proj_unit_address']
        else:
            return {}

        return call_unit

