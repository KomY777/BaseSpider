import re

from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver
from BaseSpider.base_component.read_hm_resolver.util import getValue
from BaseSpider.base_component.read_hm_resolver.util.getValue import get_provide_unit_and_address, \
    is_number, get_pxy_fee_and_standard, standardization
from BaseSpider.base_component.read_hm_resolver.util.table_contents import \
    transverse_table_contents, simple_direction_table_contents
from BaseSpider.base_component.read_hm_resolver.util.text_contents import search_all_by_xpath, \
    dismantling
from BaseSpider.tool.DealDate import get_one_time_from_str
from BaseSpider.tool.param_tool import process_dict_win
from scrapy import Selector

CONST_PARAM = {
    # 公告标题参数
    'TITLE': '//*[@class="tc"][1]/text()',
}


class ZGZF_WB_G_ReadHmResolver(HtmlPageResolver):
    def __init__(self):
        self.all_item = {}
        self.response_text = Selector(text=self.response_text)
        self.content = {"proj_name": None, "proj_code": None, "proj_item": None, "call_unit": None, "region": None,
                        "ancm_time": None, "actual_price": None, "proj_rel_p": None, "proj_rel_m": None,
                        "agent_unit_p": None,
                        "agent_unit_m": None, "other_ex": None, "purchase_m": None, "sourse_url": None,
                        "bid_time": None,
                        "provide_unit": None, "review_time": None, "review_place": None, "pxy_fee_standard": None,
                        "agent_unit_name": None, "agent_unit_address": None, "purchasing_unit_name": None,
                        "call_unit_address": None,
                        "pxy_fee": None, "title": None, 'web_site': 'http://http://www.ccgp.gov.cn/',
                        'source_web_name': '中国政府采购网'
                        }

    def resolver_page(self) -> dict:
        try:
            self.content = standardization(self.getWinBidGovernment())
            code_dict = self.getCodeHtml()
            at_dict = self.getAttachment()
            prov_dict = self.getProvideUnit()
            undefined_exp = self.getUndefinedExp()
            experts = self.getExpert()
            call_unit = self.getCallBidUnit()
            agent_unit = self.getAgentUnit()

        except Exception as e:
            print(e)
            new_page_attr = {'WB_G': self.content, 'code_dict': {}, 'at_dict': [], 'prov_dict': [], 'undefined_exp': [],
                             'experts': [], 'call_unit': {}, 'agent_unit': []}
            self.page_attr.update(new_page_attr)
            return self.page_attr
        else:
            new_page_attr = {'WB_G': self.content, 'code_dict': code_dict, 'at_dict': at_dict,
                             'prov_dict': prov_dict, 'undefined_exp': undefined_exp, 'experts': experts,
                             'call_unit': call_unit, 'agent_unit': agent_unit}
            self.page_attr.update(new_page_attr)
            return self.page_attr

    def getWinBidGovernment(self):
        """
        获取WB_G中标信息
        """
        response = self.response_text
        print(self.response_url)
        # 页面解析
        item1 = transverse_table_contents(response)
        item2 = simple_direction_table_contents(response)
        item3 = dismantling(response.xpath('//div[@class="vF_detail_content_container"]'), 'p', '：')
        # 普通数据获取
        all_item = getValue.dictionary_dict(item1, item3)
        self.all_item = all_item
        self.content = process_dict_win(all_item)

        # 复杂数据获取
        self.content['title'] = response.xpath('//*[@class="tc"][1]/text()').get()
        self.content['proj_name'] = response.xpath('//div[@class="table"]//table//tr[2]/td[2]/text()').get()
        self.content['sourse_url'] = self.response_url

        pxy_fee_and_standard_dict = get_pxy_fee_and_standard(
            response.xpath('//div[@class="vF_detail_content_container"]').get())
        self.content['pxy_fee'] = pxy_fee_and_standard_dict['pxy_fee']
        self.content['pxy_fee_standard'] = pxy_fee_and_standard_dict['pxy_fee_standard']

        other_info = search_all_by_xpath('其它补充事宜', '相关公告', response, 'p', '', 2)
        self.content['other_ex'] = other_info.replace('\n', ' ')
        self.content['purchase_m'] = '中标'

        self.content['purchasing_unit_name'] = getValue.get_one_from_dict(
            getValue.search_similar_val('采购单位名称', all_item))
        self.content['call_unit_address'] = getValue.get_one_from_dict(
            getValue.search_similar_val('采购单位地址', all_item))
        self.content['agent_unit_name'] = getValue.get_one_from_dict(
            getValue.search_similar_val('代理机构名称', all_item))
        self.content['agent_unit_address'] = getValue.get_one_from_dict(
            getValue.search_similar_val('代理机构地址', all_item))

        self.content['review_time'] = getValue.get_one_from_dict(getValue.search_similar_val('评审时间', all_item))
        self.content['review_place'] = getValue.get_one_from_dict(getValue.search_similar_val('评审地点', all_item))
        self.content['web_site'] = 'http://http://www.ccgp.gov.cn/'
        self.content['source_web_name'] = '中国政府采购网'

        # 获取项目编号
        self.content['proj_code'] = getValue.get_proj_code(response)

        # 数据格式修改
        self.content['actual_price'] = getValue.change_money(self.content['actual_price'])
        self.content['pxy_fee'] = getValue.change_money(self.content['pxy_fee'])
        self.content['ancm_time'] = get_one_time_from_str(self.content['ancm_time'])
        self.content['review_time'] = get_one_time_from_str(self.content['review_time'])
        self.content['bid_time'] = get_one_time_from_str(self.content['bid_time'])

        # 供应商解析
        provide_unit_address = get_provide_unit_and_address(response)
        self.content['provide_unit'] = provide_unit_address.get('provide_unit')
        self.content['provide_address'] = provide_unit_address.get('provide_address')

        return self.content

    '''
    获取源文件信息
    '''

    def getCodeHtml(self):
        code_dict = {'url': self.response_url,
                     'file_type': 'html',
                     'file_size': '-1',
                     'local_path': '暂无',
                     'code': ''.join(self.response_text.xpath('//*[@id="detail"]/div[2]/div/div[2]').extract())}

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
            item = {'url': file_url_list[i],
                    'file_name': file_name_list[i],
                    'file_type': file_name_list[i][file_name_list[i].rfind('.') + 1:],
                    'file_size': -1,
                    'local_path': '暂无'}
            if item['file_type'] and len(item['file_type']) > 8:
                item['file_type'] = '未知'
            at_dict.append(item)
        return at_dict

    '''
    获取供应商
    '''

    def getProvideUnit(self):
        agent_unit = []
        provide_unit = []
        provide_address = []

        if self.content['provide_unit']:
            provide_unit = self.content['provide_unit'].split('，')
        if self.content['provide_address']:
            provide_address = self.content['provide_address'].split('，')

        # 对列表去重，并保持原顺序
        removal_provide_unit = list(set(provide_unit))
        removal_provide_unit.sort(key=provide_unit.index)
        removal_provide_address = list(set(provide_address))
        removal_provide_address.sort(key=provide_address.index)

        if len(removal_provide_unit) == len(removal_provide_address):
            for i in range(len(removal_provide_unit)):
                # 供应商名称、地址不包含或不等于某些特定字符
                regex = re.compile(r'(^无$|^null$|^/$|^-$|^——$|^--$|.*详见.*|.*见附件.*|)')
                if removal_provide_unit[i] is not None and removal_provide_unit[i] is not None and \
                        regex.match(removal_provide_unit[i]) == '' and regex.match(removal_provide_address[i]) == '':
                    item = {'code': removal_provide_unit[i],
                            'name': removal_provide_unit[i],
                            'address': removal_provide_address[i]}
                    agent_unit.append(item)
        return agent_unit

    '''
    获取未定义专家
    '''

    def getUndefinedExp(self):
        undefined_exp = []

        experts = getValue.get_one_from_dict(getValue.search_similar_val('评审专家名单', self.all_item))
        if experts == '':
            experts = getValue.get_one_from_dict(getValue.search_similar_val('评标委员会成员名单', self.all_item))
            if experts == '':
                experts = search_all_by_xpath('评审专家名单', '', self.response_text, 'p', '', 2)
                experts = re.split('[\n]', experts)
                if len(experts) > 1:
                    experts = experts[1]
                else:
                    return undefined_exp
        experts = [i for i in re.split('[、 /]', experts) if i != '' and i is not None]
        for expert in experts:
            item = {}
            item['name'] = expert
            undefined_exp.append(item)

        return undefined_exp

    '''
    获取专家
    '''

    def getExpert(self):
        return []

    '''
    获取采购机构
    '''

    def getCallBidUnit(self):
        call_unit = {}
        call_unit['name'] = getValue.get_one_from_dict(getValue.search_similar_val('采购单位', self.all_item))
        call_unit['address'] = getValue.get_one_from_dict(getValue.search_similar_val('采购单位地址', self.all_item))
        call_unit['code'] = getValue.get_one_from_dict(getValue.search_similar_val('采购单位', self.all_item))

        return call_unit

    '''
    获取代理机构
    '''

    def getAgentUnit(self):
        agent_unit = []
        item = {}
        item['code'] = self.content['agent_unit_name']
        item['name'] = self.content['agent_unit_name']
        item['address'] = self.content['agent_unit_address']
        if item['name'] and item['name'] != '' and item['address'] and item['address'] != '':
            agent_unit.append(item)
        return agent_unit
