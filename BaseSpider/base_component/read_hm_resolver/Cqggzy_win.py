import json
import logging
import random

import requests
import re

from lxml import etree
from lxml.etree import tostring
from requests import get
from scrapy import Selector

import re
import time

from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver


class Cqggzy_win(HtmlPageResolver):

    # 解析单个页面
    def resolver_page(self) -> dict:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/113.0.0.0 Safari/537.36 '
        }
        resp = self.response_text
        if "Sorry, " in resp:
            return
        tree = etree.HTML(resp)
        content = {"proj_name": None, "proj_code": None, "proj_item": None, "call_unit": None,
                   "region": None, "ancm_time": None, 'actual_price': None, 'price_info': None,
                   'fund_source': None, "call_unit_address": None, "proj_rel_p": None, "proj_rel_m": None,
                   "agent_unit_name": None, "agent_unit_address": None, "agent_unit_p": None, "agent_unit_m": None,
                   "other_ex": None, "purchase_m": None, "sourse_url": None, "bid_time": None, "provide_unit": None,
                   "provide_address": None, "review_time": None, "review_place": None, "pxy_fee_standard": None,
                   "pxy_fee": None, "title": None, 'web_site': '', 'source_web_name': '', "tenderer_info": None,
                   "bidder_info": None
                   }
        page_attr = {}
        try:
            li = tree.xpath("//p")
            if not li:
                li = tree.xpath("//tbody//tr//td")
            result = ''
            for node in li:
                text_content = node.xpath('string(.)').__str__()
                result = result + text_content
            result = re.sub(r"\s+", "", result)

            content['title'] = tree.xpath("//h3[@class='article-title']")[0].text
            content['proj_name'] = content['title'].replace('的中标结果公示', '')
            content['ancm_time'] = re.search(r"信息时间：(.+?)】",
                                             tree.xpath("//div[@class='info-source']/text()")[0]).group(1) + " 00:00:00"

            base_url = "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoRelationListNew"
            infoid = self.response_url.split("/")[-1].split(".")[0]
            siteguid = "d7878853-1c74-4913-ab15-1d72b70ff5e7"
            categorynum = "014001001"
            url_new = base_url + "&infoid=" + infoid + "&siteguid=" + siteguid + "&categorynum=" + categorynum
            ran = random.random()*20
            time.sleep(ran)
            resp_new = get(url=url_new, headers=headers).content
            content['proj_code'] = re.search(r'\\"infoD\\":\\"(.*?)\\"', resp_new.decode('utf-8')).group(1)
            if re.search(r"招标人信息名称(.+?)社会信用代码", result):
                content['call_unit'] = re.search(r"招标人信息名称(.+?)社会信用代码", result).group(1)
            elif re.search(r"招标人信息（盖章）名称(.+?)社会信用代码", result):
                content['call_unit'] = re.search(r"招标人信息（盖章）名称(.+?)社会信用代码", result).group(1)
            elif re.search(r"招标人信息(.+?)社会信用代码", result):
                content['call_unit'] = re.search(r"招标人信息(.+?)社会信用代码", result).group(1)
            elif re.search(r"招标人(.+?)招标人", result):
                content['call_unit'] = re.search(r"招标人(.+?)招标人", result).group(1)
            elif re.search(r"比选人信息名称(.+?)社会信用代码", result):
                content['call_unit'] = re.search(r"比选人信息名称(.+?)社会信用代码", result).group(1)
            elif re.search(r"采购人(.+?)联系", result):
                content['call_unit'] = re.search(r"采购人(.+?)联系", result).group(1)
            elif re.search(r"采购人：(.+?)联系", result):
                content['call_unit'] = re.search(r"采购人：(.+?)联系", result).group(1)
            elif re.search(r"采购人：(.+?)采购", result):
                content['call_unit'] = re.search(r"采购人：(.+?)采购", result).group(1)
            elif re.search(r"项目法人(.+?)联系", result):
                content['call_unit'] = re.search(r"项目法人(.+?)联系", result).group(1)
            elif tree.xpath("//*[@id='mainContent']/p[15]/span/font/text()")[0]:
                content['call_unit'] = tree.xpath("//*[@id='mainContent']/p[15]/span/font/text()")[0].__str__().replace(
                    '采购人：', '')
            if re.search(r"中标人信息名称(.+?)社会信用代码", result):
                content['purchase_unit'] = re.search(r"中标人信息名称(.+?)社会信用代码", result).group(1)
            elif re.search(r"资格能力条件(.+?)招标文件", result):
                content['purchase_unit'] = re.search(r"资格能力条件(.+?)招标文件", result).group(1)
            elif re.search(r"中选人信息名称(.+?)社会信用代码", result):
                content['purchase_unit'] = re.search(r"中选人信息名称(.+?)社会信用代码", result).group(1)
            elif re.search(r"中标供应商名称：(.+?)地址", result):
                content['purchase_unit'] = re.search(r"中选人信息名称(.+?)社会信用代码", result).group(1)
            elif re.search(r"我单位确定：(.+?)为中标人", result):
                content['purchase_unit'] = re.search(r"我单位确定：(.+?)为中标人", result).group(1)
            elif re.search(r"预中标供应商名称：(.+?)；", result):
                content['purchase_unit'] = re.search(r"预中标供应商名称：(.+?)；", result).group(1)
            elif re.search(r"中标人名称：(.+?)中标人", result):
                content['purchase_unit'] = re.search(r"中标人名称(.+?)中标人", result).group(1)
            elif re.search(r"(?:第一名|第一中标候选人：)(.+?)(?:\d|社会信用代码)", result):
                content['purchase_unit'] = re.search(r"(?:第一名|第一中标候选人：)(.+?)(?:\d|社会信用代码)",
                                                     result).group(1)
            elif tree.xpath("//*[@id='mainContent']/p[7]/span[2]/font/text()"):
                content['purchase_unit'] = tree.xpath("//*[@id='mainContent']/p[7]/span[2]/font/text()")[
                    0].__str__().replace('供应商名称：', '')
            if re.search(r"等）(.+?)最高限价", result):
                content['actual_price'] = re.search(r"等）(.+?)最高限价", result).group(1)
            elif re.search(r"中选金额（元）(.+?)最高限价", result):
                content['actual_price'] = re.search(r"中选金额（元）(.+?)最高限价", result).group(1)
            elif re.search(r"中标金额（元）(.+?)最高限价", result):
                content['actual_price'] = re.search(r"中标金额（元）(.+?)最高限价", result).group(1)
            elif re.search(r"中标金额(.+?)最高限价", result):
                content['actual_price'] = re.search(r"中标金额(.+?)最高限价", result).group(1)
            elif re.search(r"\d+\.\d{2}", result):
                content['actual_price'] = re.search(r"\d+\.\d{2}", result).group()
            elif re.search(r"金额：(.+?)第二", result):
                content['actual_price'] = re.search(r"金额：(.+?)第二", result).group(1)
            elif tree.xpath("//*[@id='mainContent']/p[9]/span[2]/font/text()"):
                content['actual_price'] = tree.xpath("//*[@id='mainContent']/p[9]/span[2]/font/text()")[0]
            else:
                content['actual_price'] = ''
            if '元' not in content['actual_price']:
                content['actual_price'] += '元'
            content['price_info'] = content['actual_price']
            self.resolver_clickPage(tree, header=headers, content=content, url=self.response_url)
            page_attr = {'WB_G': content, 'code_dict': {}, 'at_dict': [], 'prov_dict': [],
                         'undefined_exp': [], 'experts': [], 'call_unit': {}, 'agent_unit': []}
            return page_attr
        except Exception as e:
            logging.error(e)

    # 解析跳转页面
    def resolver_clickPage(self, tree, header, content, url):
        link = tree.xpath("//*[@id='xggg']/li[last()]/a/@href")[0].__str__()
        click_link = 'https://www.cqggzy.com' + str(link)
        ran = random.random() * 20
        time.sleep(ran)
        resp2 = get(click_link, headers=header)
        resp2.encoding = 'utf-8'
        resp2 = resp2.text
        tree = etree.HTML(resp2)
        self.resolver_fundSource(content=content, tree=tree)
        self.resolver_region(content=content, tree=tree)
        content["web_site"] = "https://www.cqggzy.com"
        content["review_place"] = "重庆市公共资源交易中心"
        content["source_web_name"] = "重庆市公共资源交易网"
        content['sourse_url'] = url

    def resolver_fundSource(self, content, tree):
        str_array = ["//p", "//span"]
        for it in str_array:
            li = tree.xpath(it)
            result = ''
            for node in li:
                text_content = node.xpath('string(.)').__str__()
                result = result + text_content
            result = re.sub(r"\s+", "", result)
            # 使用正则表达式匹配
            if re.search(r"资金来自(.+?)[，。]", result):
                content['fund_source'] = re.search(r"资金来自(.+?)[，。]", result).group(1)
                return
            elif re.search(r"建设资金来源为(.+?)[，。]", result):
                content['fund_source'] = re.search(r"建设资金来源为(.+?)[，。]", result).group(1)
                return
            elif re.search(r"建设资金为(.+?)[，。]", result):
                content['fund_source'] = re.search(r"建设资金为(.+?)[，。]", result).group(1)
                return
            elif re.search(r"资金来源(.+?)[，。]", result):
                content['fund_source'] = re.search(r"资金来源(.+?)[，。]", result).group(1)
                return
            else:
                content['fund_source'] = ''

    def resolver_region(self, content, tree):
        str_array = ["//td", "//p", "//span"]
        region = ["渝中区", "大渡口区", "江北区", "沙坪坝区", "九龙坡区", "南岸区", "北碚区", "綦江区", "大足区",
                  "渝北区", "巴南区", "黔江区", "长寿区", "江津区", "合川区", "永川区", "南川区", "璧山区", "铜梁区",
                  "潼南区", "荣昌区", "开州区", "梁平区", "武隆区", "城口县", "丰都县", "垫江县", "忠县", "云阳县",
                  "奉节县", "巫山县", "巫溪县", "石柱土家族自治县", "秀山土家族苗族自治县", "酉阳土家族苗族自治县",
                  "彭水苗族土家族自治县", "涪陵区", "万州区"]
        for it in str_array:
            li = tree.xpath(it)
            result = ''
            for node in li:
                text_content = node.xpath('string(.)').__str__()
                result = result + text_content
            result = re.sub(r"\s+", "", result)
            # 使用正则表达式匹配
            if re.search(r"重庆市[\u4e00-\u9fa5]+区", result):
                content["region"] = re.search(r"重庆市[\u4e00-\u9fa5]+区", result).group()
                return
            else:
                for i in region:
                    pattern = i[0:2:]
                    if re.search(pattern, content['proj_name']):
                        content["region"] = "重庆市"+i
                        return
            content['region'] = "重庆市"