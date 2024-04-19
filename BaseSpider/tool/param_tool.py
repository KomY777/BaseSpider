import re


def process_dict(type, content):
    if type == 'CB_G':
        return process_dict_call(content)
    elif type == 'WB_G':
        return process_dict_win(content)
    elif type == 'FB_G':
        return process_dict_fail(content)
    elif type == 'MB_G':
        return process_dict_mo(content)
    elif type == 'CB_E':
        return engineering_dict_call(content)
    elif type == 'RB_E':
        return engineering_dict_result(content)
    elif type == 'AG_L':
        return agency_list_dict_result(content)


# 采购公告key匹配
def process_dict_call(content):
    item = {}
    item['proj_name'] = result(content, ['项目名称', '采购项目名称'])
    item['proj_code'] = result(content, ['项目编号', '机构项目编号'])
    item['proj_item'] = result(content, ['品目'])
    item['call_unit'] = result(content, ['采购单位', '采购人单位名称'])
    item['call_unit_address'] = result(content, ['采购单位地址', '采购人地址'])
    item['region'] = result(content, ['行政区域'])
    item['ancm_time'] = result(content, ['公告时间', '公告发布时间', '发布日期'])
    item['budget'] = result(content, ['预算金额', '采购项目预算金额(万元)'])
    item['proj_rel_p'] = result(content, ['项目联系人'])
    item['proj_rel_m'] = result(content, ['项目联系电话'])
    item['agent_unit_name'] = result(content, ['代理机构名称', '代理机构'])
    item['agent_unit_address'] = result(content, ['代理机构地址'])
    item['agent_unit_p'] = result(content, ['代理机构联系人'])
    item['agent_unit_m'] = result(content, ['代理机构联系方式'])
    item['tender_place'] = result(content, ['投标地点', '响应文件递交地点', '资格审查地点', '询价响应文件递交地点', '开标地点', '谈判响应文件递交地点'])
    item['bid_sale_m'] = result(content, ['标书发售方式', '获取询价文件方式', '获取资格预审文件/招标文件/谈判文件/磋商文件/询价文件的方式', '获取资格预审文件的方式'])
    item['bid_sale_op_time'] = result(content,
                                      ['标书发售时间', '获取磋商文件时间', '获取资格预审文件的时间', '获取资格预审文件/招标文件/谈判文件/磋商文件开始时间或者询价公告报名开始时间',
                                       '获取采购文件时间', '获取文件期限', '获取招标文件时间'])
    item['bid_sale_en_time'] = result(content, ['标书发售截止时间', '获取资格预审文件的时间', '获取资格预审文件/招标文件/谈判文件/磋商文件结束时间或者询价公告报名结束时间'])
    item['bid_sale_place'] = result(content,
                                    ['标书发售地点', '获取磋商文件地点', '谈判响应文件递交地点/获取询价文件地点', '获取资格预审文件的地点', '获取采购文件的地点', '获取文件地点',
                                     '获取招标文件的地点'])
    item['bid_price'] = result(content, ['标书售价', '获取询价文件文件售价', '招标文件/谈判文件/磋商文件/询价文件售价(元)', '文件购买费', '售价', '获取谈判文件文件售价'])
    item['bid_place'] = result(content,
                               ['获取招标文件的地点', '开标地点/获取谈判文件地点/竞争性磋商响应文件开启地点/拟定的唯一供应商名称及其地址/报名地点', '获取询价文件地点', '响应文件开启地点',
                                '资格审查地点', '谈判响应文件开启地点', '获取文件地点', '开标地点'])
    item['other_ex'] = result(content, ['其他说明', '其它补充事宜'])
    item['purchase_m'] = result(content, ['采购方式'])
    item['sourse_url'] = result(content, ['公告网页URL'])
    item['bid_time'] = result(content, ['开标时间', '响应文件开启时间', '开标时间/谈判时间/响应文件开启时间', '询价响应文件递交开始时间', '谈判响应文件开启时间'])
    item['title'] = result(content, ['公告标题'])
    item['bid_end_time'] = result(content, ['投标结束时间', '响应文件递交结束时间', '谈判响应文件递交截止时间'])
    return item


# 公共资源招标公告key匹配
def process_dict_call_GGZY(content):
    item = {}
    item['proj_code'] = match(content, ['编号'])
    # item['proj_item'] = match(content,['品目'])
    item['call_unit'] = match(content, ['招标人'])
    item['call_unit_address'] = ''
    item['region'] = match(content, ['建设地点|建设位置'])
    # item['ancm_time'] = match(content,['公告时间','公告发布时间','发布日期'])
    item['budget'] = match(content, ['估算|预算|控制价|投资|限价'])
    item['proj_rel_p'] = ''
    item['proj_rel_m'] = ''
    item['agent_unit_name'] = match(content, ['代理机构'])
    item['agent_unit_address'] = ''
    item['agent_unit_p'] = ''
    item['agent_unit_m'] = ''
    item['tender_place'] = match(content, ['投标地点'])
    item['bid_sale_m'] = match(content, ['取方法'])
    item['bid_sale_op_time'] = match(content, ['取时间'])
    item['bid_sale_en_time'] = match(content, ['取截止时间'])
    item['bid_sale_place'] = match(content, ['取地址'])
    item['bid_price'] = match(content, ['文件价格', '标书售价'])
    item['bid_place'] = match(content, ['取地点'])
    item['other_ex'] = ''
    item['purchase_m'] = match(content, ['采购方式'])
    # item['sourse_url'] = match(content,['公告网页URL'])
    item['bid_time'] = match(content, ['开标时间'])
    # item['title'] = match(content,['公告标题'])
    item['bid_end_time'] = match(content, ['投标结束时间'])
    return item


# 中标公告key匹配
def process_dict_win(content):
    item = {}
    item['proj_name'] = result(content, ['项目名称', '采购项目名称'])
    item['proj_code'] = result(content, ['项目编号', '机构项目编号', '二采购项目编号'])
    item['proj_item'] = result(content, ['品目'])
    item['call_unit'] = result(content, ['采购单位', '采购人单位名称'])
    item['call_unit_address'] = result(content, ['采购单位地址', '采购人地址'])
    item['region'] = result(content, ['行政区域'])
    item['ancm_time'] = result(content, ['公告时间', '公告发布时间', '发布日期'])
    item['actual_price'] = result(content, ['中标金额', '总中标金额/总成交金额(万元)', '总中标金额', '总成交金额'])
    item['proj_rel_p'] = result(content, ['项目联系人'])
    item['proj_rel_m'] = result(content, ['项目联系电话'])
    item['agent_unit_name'] = result(content, ['代理机构名称', '代理机构'])
    item['agent_unit_address'] = result(content, ['代理机构地址'])
    item['agent_unit_p'] = result(content, ['代理机构联系人'])
    item['agent_unit_m'] = result(content, ['代理机构联系方式'])
    item['other_ex'] = result(content, ['其他说明', '其它补充事宜'])
    item['purchase_m'] = result(content, ['采购方式'])
    item['sourse_url'] = result(content, ['公告网页URL'])
    item['bid_time'] = result(content, ['开标时间', '开标日期'])
    item['provide_unit'] = result(content, ['供应商', '中标供应/成交供应商名称', '中标供应商名称'])
    item['provide_address'] = result(content, ['供应商地址'])
    item['review_time'] = result(content, ['评审时间', '评审日期'])
    item['review_place'] = result(content, ['评审地点'])
    item['pxy_fee_standard'] = result(content, ['本项目代理费收费标准', '代理机构收费标准', '收费标准', '本项目招标代理费收费标准'])
    item['pxy_fee'] = result(content, ['本项目代理费总金额', '代理机构收费金额', '收费金额', '本项目招标代理费总金额'])
    item['title'] = result(content, ['公告标题'])
    return item


# 终止公告key匹配
def process_dict_fail(content):
    item = {}
    item['proj_name'] = result(content, ['项目名称', '采购项目名称'])
    item['proj_code'] = result(content, ['项目编号', '机构项目编号'])
    item['proj_item'] = result(content, ['品目'])
    item['call_unit'] = result(content, ['采购单位', '采购人单位名称'])
    item['call_unit_address'] = result(content, ['采购单位地址', '采购人地址'])
    item['region'] = result(content, ['行政区域'])
    item['ancm_time'] = result(content, ['公告时间', '公告发布时间', '发布日期'])
    item['purchasing_unit_name'] = result(content, ['采购单位名称', '采购人单位名称', '采购单位'])
    item['proj_rel_p'] = result(content, ['项目联系人'])
    item['proj_rel_m'] = result(content, ['项目联系电话'])
    item['agent_unit_name'] = result(content, ['代理机构名称', '代理机构'])
    item['agent_unit_address'] = result(content, ['代理机构地址'])
    item['agent_unit_p'] = result(content, ['代理机构联系人'])
    item['agent_unit_m'] = result(content, ['代理机构联系方式'])
    item['other_ex'] = result(content, ['其他说明', '其它补充事宜'])
    item['purchase_m'] = result(content, ['采购方式'])
    item['sourse_url'] = result(content, ['公告网页URL'])
    item['bid_time'] = result(content, ['废标日期', '废标/终止日期', '中标日期/成交日期/废标、流标日期', '公告时间'])
    item['title'] = result(content, ['公告标题'])
    item['failure_content'] = result(content, ['流标内容', '拟采购的货物或者服务的说明/废标流标的原因', '流标原因'])
    return item


# 更正公告key匹配
def process_dict_mo(content):
    item = {}

    item['proj_name'] = result(content, ['项目名称', '采购项目名称'])
    item['proj_code'] = result(content, ['项目编号', '机构项目编号', '原公告项目编号', '原公告的采购项目编号'])
    item['proj_item'] = result(content, ['品目'])
    item['region'] = result(content, ['行政区域'])
    item['ancm_time'] = result(content, ['公告时间', '公告发布时间', '发布日期'])
    item['purchasing_unit_name'] = result(content, ['采购单位名称', '采购人单位名称', '采购单位'])
    item['call_unit_address'] = result(content, ['采购单位地址', '采购人地址'])
    item['proj_rel_p'] = result(content, ['项目联系人'])
    item['proj_rel_m'] = result(content, ['项目联系电话'])
    item['agent_unit_name'] = result(content, ['代理机构名称', '代理机构'])
    item['agent_unit_address'] = result(content, ['代理机构地址'])
    item['agent_unit_p'] = result(content, ['代理机构联系人'])
    item['agent_unit_m'] = result(content, ['代理机构联系方式'])
    item['other_ex'] = result(content, ['其他说明', '其它补充事宜'])
    item['purchase_m'] = result(content, ['采购方式'])
    item['sourse_url'] = result(content, ['公告网页URL'])
    item['title'] = result(content, ['公告标题'])
    item['modify_content'] = result(content, ['更正内容', '采购项目需要落实的政府采购政策/采用单一来源采购方式的原因及相关说明/更正事项内容'])
    item['origin_announce_time'] = result(content, ['首次公告日期', '公告时间'])
    return item


def engineering_dict_call(content):
    item = {}

    item['proj_name'] = result(content, ['项目名称', '招标项目名称'])
    item['proj_code'] = result(content, ['项目编号'])
    item['resource_from'] = result(content, ['资源来源', '资金来源'])
    item['ET'] = result(content, ['计划工期', '计划工期(日历天)'])
    item['region'] = result(content, ['行政区域'])
    item['proj_unit'] = result(content, ['采购单位名称'])
    item['proj_unit_address'] = result(content, ['采购单位地址'])
    item['proj_rel_p'] = result(content, ['项目联系人'])
    item['proj_rel_m'] = result(content, ['项目联系电话'])
    item['agent_unit'] = result(content, ['代理机构名称'])
    item['agent_unit_address'] = result(content, ['代理机构地址'])
    item['agent_unit_p'] = result(content, ['代理机构'])
    item['agent_unit_m'] = result(content, ['代理机构联系方式'])
    item['tender_place'] = result(content, ['投标地点', '投标文件递交地点'])
    item['bid_sale_m'] = result(content, ['标书发售方式', '招标文件/资格预审文件获取方式'])
    item['bid_sale_op_time'] = result(content, ['标书发售起止时间', '公告发布开始时间', '招标文件获取开始时间'])
    item['bid_sale_en_time'] = result(content, ['标书发售起止时间', '招标文件获取截止时间', '资审文件获取截止时间', '投标报名截止时间', '公告发布结束时间'])
    item['bid_price'] = result(content, ['标书售价'])
    item['bid_sale_place'] = result(content, ['标书发售地点'])
    item['bid_end_time'] = result(content, ['投标截止时间', '递交投标文件截止时间', '递交资格申请文件截止时间'])
    item['other_ex'] = result(content, ['其他说明', '其他'])
    item['sourse_url'] = result(content, ['公告网页URL'])
    item['title'] = result(content, ['公告标题'])
    item['proj_place'] = result(content, ['项目地点', '项目现场的具体位置和周边环境'])
    item['ancm_time'] = result(content, ['发布时间'])
    return item


def engineering_dict_result(content):
    item = {}

    item['title'] = result(content, ['公告标题'])
    item['proj_name'] = result(content, ['项目名称', '标段名称'])
    item['proj_code'] = result(content, ['项目编号', '标段编号'])
    item['proj_unit'] = result(content, ['采购单位'])
    item['proj_unit_address'] = result(content, ['采购单位地址'])
    item['opening_time'] = result(content, ['开标时间'])
    item['notice_period'] = result(content, ['公示期'])
    item['price_ceiling'] = result(content, ['最高限价'])
    item['proj_rel_p'] = result(content, ['招标人联系人'])
    item['proj_rel_m'] = result(content, ['招标人联系方式'])
    item['agent_unit_p'] = result(content, ['招标代理机构联系人'])
    item['agent_unit_address'] = result(content, ['代理机构地址'])
    item['agent_unit_m'] = result(content, ['招标代理机构联系方式'])
    item['other_ex'] = result(content, ['其它说明', '备注说明'])
    item['ancm_time'] = result(content, ['发布时间'])

    return item


# 代理机构名单
def agency_list_dict_result(content):
    item = {}
    # item['OrgName'] = result(content,['代理机构名称'])
    # item['OrgCode'] = result(content,['统一社会信用代码(或组织机构代码)'])
    # item['UpId'] = result(content,['项目编号', '标段编号'])
    # item['UpName'] = result(content, ['采购单位'])
    # item['IdentityState'] = result(content,['采购单位地址'])
    # item['ImportTime'] = result(content,['开标时间'])
    # item['MainProperty'] = result(content,['公示期'])
    # item['BusTerm'] = result(content,['最高限价'])
    # item['FoundTime'] = result(content,['招标人联系人'])
    # item['RegMoney'] = result(content,['招标人联系方式'])
    # item['Linkman'] = result(content,['招标代理机构联系人'])
    # item['LinkmanName'] = result(content, ['代理机构地址'])
    # item['LinkmanPhone'] = result(content,['招标代理机构联系方式'])
    # item['Remark'] = result(content,['其它说明', '备注说明'])
    # item['LocalProv'] = result(content,['发布时间'])
    # item['LocalProvName'] = result(content,['发布时间'])
    # item['LocalCity'] = result(content,['发布时间'])
    # item['LocalCityName'] = result(content,['发布时间'])
    # item['LocalCounty'] = result(content,['发布时间'])
    # item['LocalCountyName'] = result(content,['发布时间'])
    # item['LocalAddr'] = result(content,['发布时间'])
    # item['PostCode'] = result(content,['发布时间'])
    # item['MainScope'] = result(content,['发布时间'])
    # item['ConcurrentlyScope'] = result(content,['发布时间'])
    # item['TradeType'] = result(content,['发布时间'])
    # item['TradeTypeName'] = result(content,['发布时间'])
    # item['CompanyType'] = result(content,['发布时间'])
    # item['LegalPerson'] = result(content,['发布时间'])
    # item['LegalPersonIdentity'] = result(content,['发布时间'])
    # item['LegalPersonEmail'] = result(content,['发布时间'])
    # item['LegalPersonPhone'] = result(content,['发布时间'])
    # item['RegAddress'] = result(content,['发布时间'])
    # item['EffectAreaId'] = result(content,['发布时间'])
    # item['EffectAreaName'] = result(content,['发布时间'])

    return item


def result(the_dict: dict, the_keys) -> str:
    for the_key in the_keys:
        if the_dict.keys().__contains__(the_key):
            return the_dict.get(the_key)

    return ''


def match(dict: dict, match_keys) -> str:
    for dict_key in dict.keys():
        for match_key in match_keys:
            if re.findall(match_key, dict_key):
                return dict.get(dict_key)
    return ''
