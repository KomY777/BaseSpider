import re

from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver
from scrapy import Selector

from BaseSpider.base_component.read_hm_resolver.util import getValue
from BaseSpider.base_component.read_hm_resolver.util.getValue import standardization, \
    unit_name_standardization
from BaseSpider.base_component.read_hm_resolver.util.table_contents import \
    transverse_table_contents, simple_direction_table_contents
from BaseSpider.base_component.read_hm_resolver.util.text_contents import search_all_by_xpath, \
    dismantling, search_all
from BaseSpider.tool import DealDate
from BaseSpider.tool.param_tool import process_dict_call


CONST_PARAM = {
    # 公告标题参数
    'TITLE': '//*[@class="tc"][1]/text()',
}


class ZGZF_CB_G_ReadHmResolver(HtmlPageResolver):
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
               'web_site': 'http://http://www.ccgp.gov.cn/', 'source_web_name': '中国政府采购网'
               }


    def resolver_page(self) -> dict:
        self.response_text = Selector(text=self.response_text)
        try:
            content = standardization(self.getInquiryGovernment())
            code_dict = self.getCodeHtml()
            at_dict = self.getAttachment()
            call_unit = self.getCallUnit()

        except:
            return self.page_attr

        else:
            new_page_attr = {'CB_G': content, 'code_dict': code_dict, 'at_dict': at_dict, 'call_unit': call_unit}
            # print(new_page_attr)
            self.page_attr.update(new_page_attr)
            return self.page_attr

    '''
    获取CB_G询价信息
    '''

    def getInquiryGovernment(self):
        response = self.response_text
        # 页面解析
        item1 = transverse_table_contents(response)
        item2 = dismantling(response, 'p', '：')
        # 普通数据获取
        all_item = getValue.dictionary_dict(item1, item2)
        # print(all_item)
        content = process_dict_call(all_item)
        # 复杂数据获取
        # print(self.response_url)
        content['title'] = response.xpath('//*[@class="tc"][1]/text()').get()
        content['proj_name'] = response.xpath("//table/tr[2]/td[2]/text()").get()
        content['sourse_url'] = self.response_url
        content['purchase_m'] = '公开招标'
        content['web_site'] = 'http://http://www.ccgp.gov.cn/'
        content['source_web_name'] = '中国政府采购网'
        content['bid_end_time'] = search_all('投标截止时间：', '开标时间', response, 'p', '')

        temp_bid_time = content['bid_sale_op_time']
        if '至' in temp_bid_time:
            # 标书发售开始时间
            content['bid_sale_op_time'] = re.split(r'至', temp_bid_time)[0]
            # 标书发售结束时间
            content['bid_sale_en_time'] = re.split(r'至', temp_bid_time)[1]
        else:
            # 标书发售开始时间
            content['bid_sale_op_time'] = temp_bid_time
            # 标书发售结束时间
            content['bid_sale_en_time'] = temp_bid_time

        # 其它补充事宜
        other_info = search_all_by_xpath('其它补充事宜', '采购项目需要落实的政府采购政策', response, 'p', '')
        content['other_ex'] = other_info.replace('\n', ' ')

        # 获取项目编号
        content['proj_code'] = getValue.get_proj_code(response)

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

        self.content = content

        return content

    '''
    获取源文件信息
    '''

    def getCodeHtml(self):
        code_dict = {}

        code_dict['url'] = self.response_url
        code_dict['file_type'] = code_dict['url'][code_dict['url'].rfind('.') + 1:]
        code_dict['file_size'] = '-1'
        code_dict['local_path'] = '暂无'
        code_dict['code'] = ''.join(self.response_text.xpath('//*[@id="detail"]/div[2]/div/div[2]').extract())

        return code_dict

    '''
    获取附件信息
    '''

    def getAttachment(self):
        file_name_list = self.response_text.xpath('//a[@class="bizDownload"]/text()').extract()
        file_url_list = self.response_text.xpath('//a[@class="bizDownload"]/@id').extract()
        for i, j in enumerate(file_url_list):
            file_url_list[i] = 'http://www.ccgp.gov.cn/oss/download?uuid=' + file_url_list[i]

        at_dict = []
        for i in range(len(file_url_list)):
            item = {}
            item['url'] = file_url_list[i]
            item['file_name'] = file_name_list[i]
            item['file_type'] = file_name_list[i][file_name_list[i].rfind('.') + 1:]
            item['file_size'] = -1
            item['local_path'] = '暂无'
            at_dict.append(item)
        return at_dict


    def getCallUnit(self):
        call_unit = {}
        call_unit['code']=self.content.get('call_unit')
        call_unit['name']=call_unit['code']
        call_unit['address']=self.content.get('call_unit_address')
        return call_unit
