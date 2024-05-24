import numpy
import re
from decimal import Decimal

from BaseSpider.base_component.read_hm_resolver.util.table_contents import obtain_td_matrix
from BaseSpider.base_component.utils.util import provide_unit_address_remove


def dictionary_dict(*li):
    # li = li[::-1]
    di = {}
    for m in li[::-1]:
        di.update(m)
    return di


# 时间转换
def change_time_str(old):
    time_change = re.findall(r"\d+\.?\d*", old)
    t = None

    if len(time_change) > 2:
        t = time_change[0]
        t += '-' + time_change[1]
        t += '-' + time_change[2]
    return t


# 存在查询
def search_similar_val(s, li):
    all_val = {}
    for key in li:
        if key.find(s) != -1:
            all_val[key] = li[key]
    return all_val


# 获得字典中的一个值
def get_one_from_dict(d):
    for i in d.values():
        return i
    return ''


# 金额转换为具体数值
def change_money(money):
    if not money:
        return money
    money = re.sub(r'[,， ]', '', money)
    number = re.findall(r"\d+\.?\d*", money)
    if len(number) < 1:
        return ''
    elif len(number) > 1:
        return money
    return str(Decimal(number[0]) * Decimal(get_money_suffix(money)))


# 金额单位解析
def get_money_suffix(money):
    suffix = 1
    if '亿' in money:
        suffix *= 100000000
    if '万' in money:
        suffix *= 10000
    if '千' in money:
        suffix *= 1000
    if '百' in money:
        suffix *= 100
    if '十' in money:
        suffix *= 10
    return suffix


def is_number(s):
    """
    判断是不是数字
    :param s:
    :return:
    """
    if s is None:
        return False
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata  # 处理ASCii码的包
        unicodedata.numeric(s)  # 把一个表示数字的字符串转换为浮点数返回的函数
        return True
    except (TypeError, ValueError):
        pass
    return False


def get_proj_code(response):
    """
    项目编号解析
    """

    try:
        all_text = response.xpath('//div[@class="vF_detail_content_container"]').get()
        # 去除多余字符
        result = re.compile(r'<[^>]+>|\n|\t| |\xa0|\r', re.S).sub('', all_text)

        # 初步匹配
        result = re.findall(
            r'(?:项目编号|项目号|采购编号|招标编号)(?:（.*?）)?[ :：]?(.*?)[,，。；; ]?(?:项目名称|(?:（?采购)?计划编号|采购(?:人名称|方式|需求|计划备案号)|[二三四][.、：:])',
            result)
        result = result[0] if len(result) > 0 else ''

        # 按'（）()'拆分开，保留前3段的内容，在项目编号中有需保留括号的情况下，去除其他无用部分
        result_split = re.split(r'[（）()]', result)
        if len(result_split) > 2:
            result = result_split[0] + '（' + result_split[1] + '）' + result_split[2]

        # 从连续10个中文及指定标点符号开始向后删完
        result = re.compile(r'([（）():：\u4E00-\u9FA5\[\]]{10,}.*$)', re.S).sub('', result)

        # 不包含**号，和一些特定字符的编号，从（字母、数字）与（汉字,，）的交接处往后删完，$表示字符串结尾是（字母、数字）与（汉字,，）交接的模式
        if re.search(r'[0-9a-zA-Z]号|[0-9a-zA-Z\[\]](?:[\u4E00-\u9FA5（）\[\]]{2,4})[\[\]0-9a-zA-Z]', result) is None:
            result = re.compile(r'(?<=[0-9a-zA-Z])([\u4E00-\u9FA5,，]{2,}.*)$', re.S).sub('', result)
            # 不包含**号、**工**，的编号，项目编号里存在“公告”、“公示”字样，从（字母、数字）与（三种括号、汉字）的交界处往后删完
            if re.search(r'公告|公示|编号|如下|（）|。', result) is not None:
                result = re.compile(r'(?<=[A-Za-z0-9])([（）()\u4E00-\u9FA5].*)', re.S).sub('', result)
        # 包含**号的编号，若'号'后第一个字符为中文，则从该中文开始向后删完
        else:
            result = re.compile(r'(?<=\d号)([\u4E00-\u9FA5,，].*)$', re.S).sub('', result)

        # 编号整体在括号内，例：（招标文件编号：JCY-CG-20201005）、（招标文件编号：JFD-20201016，第二个例子是上面的步骤截断了后括号
        if re.search(r'^[（(].*编号[:：].*[）)]?$', result) is not None:
            result = re.findall(r'编号[:：](.*)[）)]?', result)
            result = result[0] if len(result) > 0 else ''
        # 编号括号内为无用注释类，例如：20工080420（代理机构内部编号）、清设招第2020217号（招标文件编号，删除括号内容
        elif re.search(r'（.*(?:公告|公示|编号|如下|文号).*', result) is not None:
            result = re.compile(r'（.*(?:公告|公示|编号|如下|文号).*', re.S).sub('', result)

        # 处理特殊字符和数字编号的情况
        if re.search(r'项目序列号|\d[．.、]$|\d[．.、][\u4E00-\u9FA5（）()]{4,}.*', result) is not None:
            result = re.compile(r'(?:项目序列号|\d[．.、]$|\d[．.、][\u4E00-\u9FA5（）()]{4,}.*)', re.S).sub('', result)

        # 最后删除一些不符合的编号（None、编号中数字和字母都没、以/开头）
        if result is None or re.search(r'[0-9a-zA-Z]', result) is None or re.search(r'^/', result) is not None:
            result = ''
    except Exception as e:
        return ''

    return result


def get_provide_unit_and_address(response) -> dict:
    """
    供应商解析（仅供应商名称和地址同时能取值时才算匹配成功）
    """
    provide_unit = ''
    provide_address = ''

    '''非表格情况'''
    provide_address_mark = '，'.join(
        response.xpath(
            '//p[contains(.,"供应商名称") or contains(.,"中标供应商") or (contains(.,"供应商") and contains(.,"地址"))]').getall())
    if provide_address_mark is not None and provide_address_mark != []:
        provide_address_mark = provide_unit_address_remove(provide_address_mark)
        provide_unit = re.findall(r'(?:供应商名称|中标供应商).??(?:（.*?）|\(.*?\))?[:：]?([^，。;；]{4,}.*?)[，。;；]?',
                                  provide_address_mark)
        provide_address = re.findall(r'(?:供应商地址|地址).??(?:（.*?）|\(.*?\))?[:：]?([^，。;；]{2,}.*?)[，。;；]?',
                                     provide_address_mark)

        # 仅取供应商名称和地址一一匹配的，能剔除一些意外情况
        min_len = min(len(provide_unit), len(provide_address))
        # 供应商名称和地址不能存在，但有可能出现的词
        regex = re.compile(r'中标|成交|详见|见附件|地址|联系|null')
        provide_unit = '，'.join(unit for unit in provide_unit[:min_len] if unit != '' and not re.search(regex, unit))
        provide_address = '，'.join(
            address for address in provide_address[:min_len] if address != '' and not re.search(regex, address))

    '''表格情况'''

    # xpath提取表格内容
    # 三层表格嵌套
    provide_table = response.xpath(
        '//table//table//table[contains(.,"供应商名称") or contains(.,"中标供应商") or contains(.,"成交供应商")]')
    if provide_table is None or provide_table == []:
        # 两层表格嵌套
        provide_table = response.xpath(
            '//table//table[contains(.,"供应商名称") or contains(.,"中标供应商") or contains(.,"成交供应商")]')
    if provide_table is None or provide_table == []:
        # 一层表格
        provide_table = response.xpath(
            '//table[contains(.,"供应商名称") or contains(.,"中标供应商") or contains(.,"成交供应商")]')

    # 表格解析
    if provide_table is not None and provide_table != []:

        for provide_table_item in provide_table:
            item4 = obtain_td_matrix(provide_table_item)
            provide_table_numpy_temp = numpy.array(item4)

            # 每行元素个数可能不同，循环时会超出范围，这里每行个数相同的个数，去除其他不相同的
            # 获取每行长度
            each_length = []
            for item in provide_table_numpy_temp:
                each_length.append(len(item))

            # 获取出现次数最多的长度
            max_appear = max(set(each_length), key=each_length.count)

            # 只取长度为该值的行
            provide_table_numpy = []
            for item in provide_table_numpy_temp:
                if len(item) == max_appear:
                    provide_table_numpy.append(item)
            provide_table_numpy = numpy.array(provide_table_numpy)

            # 纵向解析的标志
            isLongitudinal = None

            # 从表格第一行和所有列检验“供应商名称”、“供应商地址”判断是纵向解析还是横向解析
            first_row = ' '.join(provide_table_numpy[0]) if len(provide_table_numpy) > 0 else ''

            # 纵向：
            if '供应商名称' in first_row or '中标供应商' in first_row or '成交供应商' in first_row in first_row:
                isLongitudinal = True
            # 横向（基本没有横向表格，且存在很多全篇表格的公告形成二维数组后每行长度不同，数组循环时容易超出范围，故不处理）
            # elif len(provide_table_numpy) > 0:
            #     for y, item in enumerate(provide_table_numpy[0]):
            #         # some_col = ' '.join(provide_table_numpy[:, y])
            #         some_col = ' '.join([i[y] for i in provide_table_numpy])
            #         if ('供应商名称' in some_col or '中标供应商' in some_col or '成交供应商' in some_col) and '地址' in some_col:
            #             isLongitudinal = False
            #             break

            # 纵向解析
            if isLongitudinal and len(provide_table_numpy) > 0:

                # 不能仅有地址而无公司名称
                if not provide_unit:
                    provide_address = ''

                for index, item in enumerate(provide_table_numpy[0]):
                    if ('供应商名称' in item or '中标供应商' in item or '成交供应商' in item) and '地址' not in item and not provide_unit:
                        provide_unit = '，'.join(
                            ''.join(i.split()) for i in provide_table_numpy[:, index]
                            if '供应商名称' not in i and '中标供应商' not in i and '成交供应商' not in i and i != '')

                    if '地址' in item and not provide_address:
                        provide_address = '，'.join(
                            ''.join(i.split()) for i in provide_table_numpy[:, index] if '地址' not in i and i != '')

            # print()

    '''规范化处理'''

    # 用于删除特定字符
    regex = re.compile(
        r'【.*】|详见|(?:中标|成交)?供应商|名称|公告|.?附件|地址|联系|品牌|null|补充事宜|[(（].*?[包型0-9a-zA-Z].*?[）)]|[？?∶:：…— 　]|'
        r'[(（]?第?(?:[一二三四五六七八九十\-— a-zA-Z\d]*)?(标段|标包|分标|包组|包件|包|候选人)(?:[一二三四五六七八九十\-— a-zA-Z\d]*)?[）)]?|'
        r'[一二三四五六七八九十\-— a-zA-Z0-9]+[标.]', re.S)

    # 用于供应商名开头标准化
    start_standardization_regex = re.compile(r'^第?[一二三四五六七八九十a-zA-Z0-9]*([、:：]|中标|成交)+|^[0-9a-zA-Z]+[）) ]*', re.S)

    # 用于供应商名称结尾标准化
    end_standardization_regex = re.compile(r'^((?!(公司|中心|[(（]*(?:联合体|牵头人|牵头单位|主体单位|.*(?:公司|中心|院))[）)]*|'
                                           r'厂|社|所|行|院|部|校|店|学|场|会|局|室|处|队|楼|馆|站|台|团|城|园|坊|房|区|厅|庄|库|'
                                           r'政府|基地|大厦|超市|科技|企业|农家乐|商贸|公寓|园艺|家具|电器|服饰)$).)*$', re.S)

    # 供应商名称规范化处理
    # 通过[/,，]拆分成列表，并将列表中每个？?:：以及类似【**】、第.*候选人、（*标段*）、（*包*）等的元素去除，后面两个没有括号也会匹配
    # 例：'一标段：标包【1】天水三和数码测绘院有限公司，二标段：北京新兴华安智慧科技有限公司'
    #      --> ['天水三和数码测绘院有限公司', '北京新兴华安智慧科技有限公司']
    #      --> '天水三和数码测绘院有限公司，北京新兴华安智慧科技有限公司'

    # 先删除特定字符
    provide_unit = [regex.sub('', i).strip() for i in re.split('[/,，]', provide_unit)]
    # 开头标准化
    provide_unit = [start_standardization_regex.sub('', i) for i in provide_unit]
    # 结尾标准化
    provide_unit = [end_standardization_regex.sub('', i) for i in provide_unit]
  # # 整个供应商名称被括号包围
  #   provide_unit = [i[1:-1] for i in provide_unit if re.search(r'^（.*）$|^\(.*\)$', i)]


    # 供应商地址规范化处理
    provide_address = [regex.sub('', i).strip() for i in re.split('[/,，]', provide_address)]

    # 不能仅有地址而无公司名称
    for i in range(min(len(provide_unit), len(provide_address))):
        if not provide_unit[i]:
            provide_address[i] = ''

    # 最后拼接成字符串，按中文逗号隔开
    provide_unit = '，'.join(i for i in provide_unit if i)
    provide_address = '，'.join(i for i in provide_address if i)

    # 去除字符串最后可能存在的逗号
    if provide_unit and provide_unit[-1] == '，':
        provide_unit = provide_unit[:-1]
    if provide_address and [-1] == '，':
        provide_address = provide_address[:-1]

    # 去重，以供应商名称为标准（上面的处理不会出现没有名称而有地址的情况），名称、地址同时去重
    provide_unit_list = [i for i in re.split('[/,，]', provide_unit)]
    provide_address_list = [i for i in re.split('[/,，]', provide_address)]
    provide_unit_list_single = []
    provide_address_list_single = []
    for index, item in enumerate(provide_unit_list):
        if item not in provide_unit_list_single:
            provide_unit_list_single.append(provide_unit_list[index])
            if len(provide_address_list) > index:
                provide_address_list_single.append(provide_address_list[index])
    provide_unit_string_single = '，'.join(provide_unit_list_single)
    provide_address_string_single = '，'.join(provide_address_list_single)

    if provide_unit_string_single == '':
        provide_unit_string_single = None
    if provide_address_string_single == '':
        provide_address_string_single = None

    # print(provide_unit_string_single)
    # print(provide_address_string_single)
    # print()
    return {'provide_unit': provide_unit_string_single, 'provide_address': provide_address_string_single}


def get_pxy_fee_and_standard(response) -> dict:
    """
    获取代理机构收费标准及金额
    :return:
    """
    pxy_fee_standard = None
    pxy_fee = None

    # 去除html标签
    response = re.sub(r'<[^>]+>|&amp;|\n|\t|\xa0|\r| ', '', response)

    # 获取代理机构收费标准及金额（常规情况）
    regex_result = re.search(
        r'(?:(?:代理|收费)[\u4E00-\u9FA5]{0,6}标准)[：: ]'
        r'(.*?)'
        r'(?:(?:本项目)?(?:代理|收费)[\u4E00-\u9FA5]{0,6}金额(?:（.*?）)?|收费金额（元）|评审专家名单|项目用途)[：: ]'
        r'(.*?)'
        r'(?:（人民币）|元|[四五六七八九]、)', response)

    if regex_result:
        # 获取代理机构收费标准
        pxy_fee_standard = ''.join(regex_result.group(1))

        # 获取代理机构收费金额
        pxy_fee = change_money(''.join(regex_result.group(2)))

    # 特殊情况1：
    # 金额特殊格式
    # 例：合同包[350322]zhx[GK]2020020-1包1：8670
    if pxy_fee_standard and pxy_fee and re.findall(r'.*[：:](\d+\.?\d*)$', pxy_fee):
        pxy_fee = ''.join(re.findall(r'.*[：:](\d+\.?\d*)$', pxy_fee))

    # 特殊情况2：
    # 标准和金额写反了
    # 例：本项目代理费总金额： 按三河市人民政府建设项目中介服务费收费标准计算
    #     本项目代理费收费标准： 9800
    if not pxy_fee and not pxy_fee_standard:
        regex_result = re.search(
            r'(?:(?:代理|收费)[\u4E00-\u9FA5]{0,6}金额)[：: ]'
            r'(.*?)'
            r'(?:(?:本项目)?(?:代理|收费)[\u4E00-\u9FA5]{0,6}标准(?:（.*?）)?|收费金额（元）|评审专家名单|项目用途)[：: ]'
            r'(.*?)'
            r'(?:（人民币）|元|[四五六七八九]、)', response)

        if regex_result:
            # 获取代理机构收费标准
            pxy_fee_standard = ''.join(regex_result.group(1))

            # 获取代理机构收费金额
            pxy_fee = change_money(''.join(regex_result.group(2)))

    # 如果金额不是数字，置为None
    if not is_number(pxy_fee):
        pxy_fee = None

    # change_money后因浮点数原因，0有时会变成0E-7，重置为0
    if '0E-' in str(pxy_fee):
        pxy_fee = 0.0

    return {'pxy_fee': pxy_fee, 'pxy_fee_standard': pxy_fee_standard}


def standardization(content):
    """
    各个字段规格化
    :return:
    """
    for key in content.keys():
        regex = re.compile(r'^(null|详见.*|无|\\|-|)$')
        if content[key] and re.search(regex, content[key]):
            content[key] = None

    return content


def unit_name_standardization(unit_name):
    """
    采购单位、代理机构名称统一化处理
    :param unit_name:
    :return:
    """
    unit_name = re.sub(r'^((采购人)?名.*?称|招.*?标.*?人|主办单位|采购单位|采.*?购.*?人|代建单位)[:：]|（.*?）$', '', unit_name).strip()
    unit_name = re.sub(r'(^[?？∶:： 　]*)|([?？∶:： 　]*$)', '', unit_name).strip()
    return unit_name
