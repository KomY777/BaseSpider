import json
import re
import traceback
import urllib.parse
import requests
import openpyxl
import os
from re import search
from datetime import datetime
from toollib.guid import SnowFlake
from BaseSpider.base_component.HtmlPageResolver import HtmlPageResolver


class CQGP_C_G_ReadHmResolver(HtmlPageResolver):
    # todo 转换设置定时器
    def resolver_page(self) -> dict:
        """
            解析网页的json数据以及PDF文件
            :return: page_attr 返回一个包括所有字段的对象
        """
        content = {'id': SnowFlake().gen_uid(),'contract_no': None, 'contract_name': None,
                   'project_code': None,
                   'project_name': None, 'region': None, 'category': None, 'resolve_status': None,
                   'purchase_directory': None, 'specification_and_model': None, 'purchase_time': None,
                   'purchase_method': None, 'purchase_number': None, 'win_bid_brand': None,
                   'unit_price': None, 'total_amount': None, 'import_and_export': None,
                   'manufacturer': None, 'warranty_period': None, 'maintenance_service': None, 'brief_info': None,
                   'contract_sign_date': None, 'contract_announcement_date': None,
                   'supplier': None, 'supplier_phone': None, 'supplier_address': None,
                   'agency': None, 'agency_phone': None, 'agency_address': None,
                   'purchaser': None, 'purchaser_phone': None, 'purchaser_address': None,
                   'tender_an_link': None, 'tender_an_enclosure': None, 'result_an_link': None,
                   'result_an_enclosure': None, 'contract_an_link': None, 'contract_an_enclosure': None,
                   }
        page_attr = {}
        try:
            url = 'https://www.ccgp-chongqing.gov.cn/contractpost/manage_getContractById.action?updateId='
            page_id = search(r'\?updateId=(.+)$', self.response_url).group(1)
            url = url + page_id
            resp = requests.get(url)
            resp.encoding = 'utf-8'
            resp = resp.text
            obj = json.loads(resp)
            data = obj['contract']
            content['title'] = data.get('contractName')  # 标题
            content['contract_no'] = data.get('contractNo')  # 合同编号
            content['contract_name'] = data.get('contractName')  # 合同名称
            content['project_code'] = data.get('itemNo')  # 项目编号
            content['project_name'] = data.get('itemName')  # 项目名称
            content['region'] = data.get('adminAreaName')  # 区域
            content['category'] = ''  # 合同类别
            content['resolve_status'] = '已打标'  # 解析状态
            content['purchase_directory'] = data.get('objectName')  # 采购目录
            content['specification_and_model'] = data.get('objectModel')  # 规格型号(pdf)
            content['purchase_time'] = data.get('signedDate')  # 采购时间
            content['purchase_method'] = data.get('purchaseWayName')  # 采购方式
            content['purchase_number'] = (data.get('objectNum') + data.get('objectUnit')) \
                if (data.get('objectNum') and data.get('objectUnit')) else None  # 采购数量
            content['win_bid_brand'] = ''  # 中标品牌(pdf)
            content['unit_price'] = data.get('objectUnitPrice')  # 中标单价
            content['total_amount'] = data.get('money')  # 中标总金额
            content['import_or_export'] = ''  # 进出口(pdf)
            content['manufacturer'] = ''  # 生产商(pdf)
            content['warranty_period'] = ''  # 质保期限(pdf)
            content['maintenance_service'] = ''  # 维修服务(pdf)
            content['brief_info'] = '详见合同附件'  # 简要信息
            content['contract_sign_date'] = data.get('signedDate')  # 合同签订时间
            content['contract_announcement_date'] = data.get('announcementTime')  # 合同公告时间
            content['supplier'] = data.get('providerOrgName')  # 供应商
            content['supplier_phone'] = data.get('providerOrgLinkTel')  # 供应商联系电话
            content['supplier_address'] = data.get('providerOrgAddress')  # 供应商地址
            content['agency'] = ''  # 代理机构
            content['agency_phone'] = ''  # 代理机构联系方式
            content['agency_address'] = ''  # 代理机构地址
            content['purchaser'] = data.get('stockOrgName')  # 采购人
            content['purchaser_phone'] = data.get('stockOrgLinkTel')  # 采购人联系电话
            content['purchaser_address'] = data.get('stockOrgAddress')  # 采购人地址
            content['tender_an_link'] = ''  # 招标公告链接(二次处理已补充)
            content['result_an_link'] = ''  # 结果公告链接(二次处理已补充)
            content['contract_an_link'] = self.response_url  # 合同公告链接
            content['tender_an_enclosure'] = ''  # 招标公告附件链接(二次处理已补充)
            content['result_an_enclosure'] = ''  # 结果公告附件链接(二次处理已补充)
            url_attachment = 'https://www.ccgp-chongqing.gov.cn/djc-gateway/files?filePath={}&fileName={}'
            if data.get('attachments'):
                url_attachment = url_attachment.format(data['attachments'][0]['filePath'],
                                                       urllib.parse.quote(data['attachments'][0]['attachName']))
                url_attachment += '&business={}'.format(data['attachments'][0]['business'])
            content['contract_an_enclosure'] = url_attachment  # 合同公告附件链接

            # read 医疗资源目录
            medical_resources = self.read_xlsx()
            for resource in medical_resources:
                # if resource in title and ('医疗' in purchaser or '卫生' in purchaser or '医药' in purchaser):
                if bool(re.search(r'{}'.format(re.escape(resource)), content['contract_name'])) and bool(
                        re.search(r'医院|卫生|医科|医药|医疗', content['purchaser'])):
                    content['category'] = '医疗'
                    content['resolve_status'] = '未解析'
                    # region
                    base_win_url = ('https://www.ccgp-chongqing.gov.cn/gwebsite/api/v1/notices/stable/new'
                                    '?__platDomain__=www.ccgp-chongqing.gov.cn&directoryCode=A&endDate={'
                                    '}&isResult=2&orBidProject=true&pi=1&projectCode={}&ps=20&startDate={}&type=300,'
                                    '302,304,3041,305,306,307,308,309,400')
                    # get 构造参数
                    date = datetime.strptime(content['contract_announcement_date'], '%Y-%m-%d %H:%M:%S').year
                    startDate1 = "{}-01-01".format(date)
                    startDate2 = "{}-01-01".format(str(int(date) - 1))
                    endDate1 = "{}-12-31".format(date)
                    endDate2 = "{}-12-31".format(str(int(date) - 1))
                    #  query 中标公告
                    win_url1 = base_win_url.format(endDate1, content['project_code'],
                                                   startDate1)  # endDate,proj_code,startDate
                    win_url2 = base_win_url.format(endDate2, content['project_code'],
                                                   startDate2)  # endDate,proj_code,startDate
                    print(content['project_code'], date, win_url1)
                    try:
                        win_resp1 = requests.get(win_url1).json()
                        win_resp2 = requests.get(win_url2).json()
                        if win_resp1['total'] != 0 or win_resp2['total'] != 0:
                            base_an_link = 'https://www.ccgp-chongqing.gov.cn/info-notice/procument-notice-detail/{}'
                            win_data = win_resp1['notices'][0] if win_resp1['total'] != 0 else win_resp2['notices'][0]
                            content['result_an_link'] = base_an_link.format(win_data['id'])
                            content['result_an_link_api'] = 'https://www.ccgp-chongqing.gov.cn/gwebsite/api/v1/notices/stable/{}?__platDomain__=www.ccgp-chongqing.gov.cn'.format(win_data['id'])
                            win_resp = requests.get(content['result_an_link_api']).json()
                            base_attach_url = 'https://www.ccgp-chongqing.gov.cn/gwebsite/files?filePath={}&fileName={}'
                            try:
                                content['result_an_enclosure'] = base_attach_url.format(
                                    json.loads(win_resp['notice']['attachments'])[0]['value'],
                                    json.loads(win_resp['notice']['attachments'])[0]['name'])
                            except Exception as e:
                                content['result_an_enclosure'] = ''
                            # get 招标公告
                            content['tender_an_link'] = base_an_link.format(win_resp['refers'][0]['target'])
                            content['tender_an_link_api'] = 'https://www.ccgp-chongqing.gov.cn/gwebsite/api/v1/notices/stable/{}?__platDomain__=www.ccgp-chongqing.gov.cn'.format(win_resp['refers'][0]['target'])
                            call_resp = requests.get(content['tender_an_link_api']).json()
                            try:
                                content['tender_an_enclosure'] = base_attach_url.format(
                                    json.loads(call_resp['notice']['attachments'])[0]['value'],
                                    json.loads(call_resp['notice']['attachments'])[0]['name'])
                            except Exception as e:
                                content['tender_an_enclosure'] = ''
                        break
                    except:
                        traceback.print_exc()
                    # endregion
            page_attr = {'C_G': content}
        except Exception as e:
            traceback.print_exc()

        return page_attr

    @staticmethod
    def read_xlsx() -> list:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'med_goods.xlsx')
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        data = []
        column_index = 2
        for row in sheet.iter_rows():
            cell = row[column_index - 1]
            data.append(cell.value)
        wb.close()
        return list(set(data))