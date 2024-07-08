import datetime
import random
import time
import traceback

import requests
from scrapy import FormRequest, Selector

from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver
# 初始网页请求
from BaseSpider.base_component.RequestResolver import RequestResolver
from BaseSpider.settings import USER_AGENTS


class ZGZF_I_G_ReqPageResolver(HtmlPageResolver):

    def resolver_page(self) -> dict:
        content = {
            'province': None, 'city': None, 'region': None, 'level': None, 'call_unit': None, 'purchase_unit': None,
            'title': None, 'acnm_time': None, 'total_budget': None, 'source_website': None, 'source_url': None
        }
        details = []
        page_attr = {}
        url_prefix = "http://cgyx.ccgp.gov.cn"
        total_budget = 0
        try:
            resp = Selector(text=self.response_text)
            content['title'] = resp.xpath("//h3/text()").extract_first()
            unit = resp.xpath("//table/thead/tr/td[6]/text()").extract()
            tr_list = resp.xpath("//table/tbody/tr").extract()
            for i in range(1, len(tr_list)+1):
                detail = {'proj_name': resp.xpath("//table/tbody/tr[" + str(i) + "]/td[3]/a/text()").get().strip(),
                          'survey': ''}
                # 获取项目详情
                url = url_prefix + resp.xpath("//table/tbody/tr[" + str(i) + "]/td[5]/a/@href").extract_first()
                # 请求前都先让线程睡眠一段时间防止并发封ip
                res = self.html_request(url, 1)
                detail_res = Selector(res)
                detail['budget'] = resp.xpath("//table/tbody/tr[" + str(i) + "]/td[6]/text()").extract_first()
                for item in unit:
                    if "万元" in item:
                        detail['budget'] = float(detail['budget']) * 10000
                detail['survey'] = detail_res.xpath("//table/tbody/tr[7]/td[2]/div/text()").extract_first()
                detail['other'] = detail_res.xpath("//table/tbody/tr[9]/td[2]/div/text()").extract_first()
                detail['purchase_time'] = detail_res.xpath(
                    "//table/tbody/tr[" + str(i) + "]/td[2]/text()").extract_first()
                total_budget += float(detail['budget'])
                details.append(detail)
            content['source_website'] = '中国政府采购网'
            content['source_url'] = self.response_url
            content['level'] = 1
            content['call_unit'] = resp.xpath("//table/tbody/tr[1]/td[2]/text()").get().strip()
            content['purchase_unit'] = content['call_unit']
            content['province'] = "全国"
            content['acnm_time'] = resp.xpath("//p/span[@id='pubTime']/text()") \
                .get() \
                .strip() \
                .replace("年", "-") \
                .replace("月", "-") \
                .replace("日", "")
            content['total_budget'] = total_budget
            page_attr = {'I_G': content, 'details': details}
        except Exception as e:
            traceback.print_exc()
        return page_attr

    def html_request(self, url, retry):
        if retry == 1:
            time.sleep(random.random() * 60)
            res = requests.get(url=url, headers={"User-Agent": random.choice(USER_AGENTS)})
            if res.status_code != 200:
                return self.html_request(url, retry + 1)
            return res
        if retry < 3:
            # 访问失败后访问下主页
            time.sleep(random.random() * 60)
            requests.get(url="http://www.ccgp.gov.cn/", headers={'User-Agent': random.choice(USER_AGENTS)})
            res = requests.get(url=url, headers={"User-Agent": random.choice(USER_AGENTS)})
            if res.status_code != 200:
                return self.html_request(url, retry + 1)
            return res
