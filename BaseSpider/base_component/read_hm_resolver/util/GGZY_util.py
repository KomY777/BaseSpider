from html.parser import HTMLParser
import re
import traceback

import cpca


class _DeHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = []
        self.last_start_tag = '???'

    def handle_data(self, data):
        text = data.strip()
        if len(text) > 0:
            self.__text.append(text + ' ')

    def handle_starttag(self, tag, attrs):
        if tag in ['p', 'div'] and not self.last_start_tag == 'td':
            self.__text.append('\n\n')
        elif tag in ['br', 'tr', 'li', 'dt', 'dd', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.__text.append('\n')
        elif tag == 'style' or tag == 'script':
            self.__text.append('<ignore>')

        self.last_start_tag = tag

    def handle_endtag(self, tag):
        if tag == 'style' or tag == 'script':
            self.__text.append('</ignore>')

    def text(self):
        return re.sub(r'<ignore>([\s\S]*?)</ignore>', '', ''.join(self.__text).strip())


def parseHtml(html):
    try:
        parser = _DeHTMLParser()
        parser.feed(html)
        parser.close()
        return parser.text()
    except Exception:
        traceback.print_exc()
        return ''


def parseHtml_list(html):
    text = parseHtml(html)
    return re.split('\n+', text)


def parse2dict(list, split=r'(?<!\d{2})[：:]+'):
    dict = {}
    for row in list:
        data = re.split(split, row, 1)
        if len(data) >= 2:
            key = re.sub(r'\s+', '', data[0])
            if key in dict:
                # 如果有同名则视为无效数据
                dict[key] = ''
            else:
                dict[key] = data[1]
    return dict


def parse2dict_title(list, regx=r'^[一二三四五六七八九十](?:\s||一|二|三)、', except_regx=''):
    dict = {}
    last_index = -1
    last_title = ''
    for index, row in enumerate(list):
        if re.search(regx, row) and (except_regx == '' or not re.search(except_regx, row)):
            if not last_index == -1:
                dict[last_title] = list[last_index + 1:index]
            last_index = index
            last_title = re.sub(r'\s+', '', row)
    if not last_index == -1:
        dict[last_title] = list[last_index + 1:]
    return dict


def parse2dict_title_gcjs(list, regx=r'^[一二三四五六七八九十\d](?:\d|\s|一|二|三|)[、\.．]', except_regx=r'^\d+\.\d+'):
    dict = {}
    last_index = -1
    last_title = ''
    flag_upper_title = False
    for index, row in enumerate(list):
        if re.search(regx, row) and (except_regx == '' or not re.search(except_regx, row)):
            if not last_index == -1:
                dict[last_title] = list[last_index + 1:index]
            last_index = index
            last_title = re.sub(r'\s+', '', row)
            if not flag_upper_title and re.search(r'^[一二三四五六七八九十]', last_title):
                flag_upper_title = True
                except_regx = r'^\d'

    if not last_index == -1:
        dict[last_title] = list[last_index + 1:]
    return dict


def search_code(list):
    for row in list:
        if re.search('电话|联系方式', row):
            continue
        codes = re.search(r'[0-9A-Z()（）\-/\]\[]{9,}', row)
        if codes:
            code = codes.group()
            if (re.search('[A-Z]', code) or len(code) > 11) and not re.search('[:：.]', code):
                # 和时间格式区分开
                clean_code = re.findall(r'^[(（](.*)[)）]$', code)
                if len(clean_code) > 0:
                    code = clean_code[0]
                return code
    return ''


def match(dict: dict, match_keys):
    for dict_key in dict.keys():
        if re.findall(match_keys, dict_key):
            return dict.get(dict_key)
    return ''


def clean_dict(dict: dict):
    for key in list(dict.keys()):
        if not dict[key] or dict[key] == '':
            del dict[key]
    return dict


def clean_contact(dict: dict):
    for key in list(dict.keys()):
        if re.search(r'单位章', dict[key]):
            del dict[key]
    return dict


def process_callbid_file(dict: dict):
    if not dict:
        return {}
    for key in dict.keys():
        if re.search('标书|招标文件|获取.*文件', key):
            return __process_callbid_file_from_list(dict[key])
    return {}


def __process_callbid_file_from_list(list):
    dict1 = parse2dict(list)
    item = dict()
    item['bid_sale_m'] = match(dict1, '方')
    item['bid_sale_op_time'] = match(dict1, '时间')
    item['bid_sale_en_time'] = match(dict1, '止时间')
    item['bid_sale_place'] = match(dict1, '地点|地址')
    item['bid_price'] = match(dict1, '价格|售价')
    temp_bid_time = item['bid_sale_op_time']
    if temp_bid_time and '至' in temp_bid_time:
        # 标书发售开始时间
        item['bid_sale_op_time'] = re.split(r'至', temp_bid_time)[0]
        # 标书发售结束时间
        item['bid_sale_en_time'] = re.split(r'至', temp_bid_time)[1]
    else:
        # 标书发售开始时间
        item['bid_sale_op_time'] = temp_bid_time
        # 标书发售结束时间
        item['bid_sale_en_time'] = temp_bid_time
    if item['bid_price'] and not item['bid_price'] == '':
        money = re.findall(r'([\d.,，]+元)', item['bid_price'])
        if money and not len(money) == 0:
            item['bid_price'] = money.pop()

    if item['bid_sale_m'].strip() == '':
        for row in list:
            method = re.findall(r'(?:携|持|通过|使用|登录|从|在|地点[：:]).*?(?:下载|取)', row)
            if len(method) > 0:
                item['bid_sale_m'] = method[0]
    if item['bid_sale_place'].strip() == '':
        item['bid_sale_place'] = item['bid_sale_m']

    clean_dict(item)
    return item


def process_callbid_tender(dict: dict):
    if not dict:
        return {}
    for key in dict.keys():
        if re.search('投标(?!人|须知|说明)|提交', key):
            return __process_callbid_tender_from_list(dict[key])
    return {}


def __process_callbid_tender_from_list(list):
    dict1 = parse2dict(list)
    item = dict()
    item['bid_end_time'] = match(dict1, '时间')
    item['tender_place'] = match(dict1, '地点|地址')

    temp_time = item['bid_end_time']
    if temp_time and '至' in temp_time:
        item['bid_end_time'] = re.split(r'至', temp_time)[1]
    clean_dict(item)
    return item


def process_callbid_open(dict: dict):
    if not dict:
        return {}
    for key in dict.keys():
        if re.search('开标|开启', key):
            return __process_callbid_open_from_list(dict[key])
    return {}


def __process_callbid_open_from_list(list):
    dict1 = parse2dict(list)
    item = dict()
    item['bid_time'] = match(dict1, '时间')
    item['bid_place'] = match(dict1, '地点|地址')

    temp_time = item['bid_time']
    if temp_time and '至' in temp_time:
        item['bid_time'] = re.split(r'至', temp_time)[1]
    clean_dict(item)
    return item


def process_callbid_other_ex(dict: dict):
    item = {}
    if not dict:
        return item
    for key in dict.keys():
        if re.search('其他|补充', key):
            item['other_ex'] = ' '.join(dict[key])
            break
    clean_dict(item)
    return item


def process_callbid_money(dict: dict):
    if not dict:
        return {}
    for key in dict.keys():
        if re.search('(?=项目|工程|基本).*(?=概况|信息|情况)', key):
            return __process_callbid_money_from_list(dict[key])
    return {}


def __process_callbid_money_from_list(list):
    item = {}
    for row in list:
        money = re.findall('(?=估算|预算|额|价).*?([\d.,，]+[万元])', row)
        if money and len(money) >= 1:
            if re.search('百万', row):
                item['budget'] = money[0] + '百万'
            elif re.search('万', row):
                item['budget'] = money[0] + '万'
            elif re.search('亿', row):
                item['budget'] = money[0] + '亿'
            else:
                item['budget'] = money[0]
            break
    clean_dict(item)
    return item


def process_callbid_contact(dict: dict):
    if not dict:
        return {}
    for key in dict.keys():
        if re.search('联系', key):
            return __process_callbid_contact_from_list(dict[key])
    return {}


def __process_callbid_contact_from_list(list):
    dict1 = parse2dict_title(list, r'^[\t ]*[\d（(]|采购|釆购|招标|项目', r':|：|地址|电话|邮箱')
    item = {}
    if len(dict1) >= 2:
        for key in dict1.keys():
            if 'agent_unit_name' not in item and re.search('机构|代理', key):
                dict2 = parse2dict(dict1[key])
                item['agent_unit_name'] = match(dict2, '名|机构|代理')
                item['agent_unit_address'] = match(dict2, '地')
                item['agent_unit_p'] = match(dict2, '人')
                item['agent_unit_m'] = match(dict2, '方|电话|邮箱')
            elif 'call_unit' not in item and re.search('(?:采购|釆购|招标)人', key):
                dict2 = parse2dict(dict1[key])
                item['call_unit'] = match(dict2, '人|名')
                item['call_unit_address'] = match(dict2, '地')
            elif 'proj_rel_p' not in item and re.search('项目联系', key):
                dict2 = parse2dict(dict1[key])
                item['proj_rel_p'] = match(dict2, '人|名')
                item['proj_rel_m'] = match(dict2, '方|电话|邮箱')
        if 'proj_rel_m' in item.keys() and 'agent_unit_m' in item.keys():
            if item['proj_rel_m'] == item['agent_unit_m'] and item['agent_unit_p'] == '':
                item['agent_unit_p'] = item['proj_rel_p']

    clean_contact(item)
    clean_dict(item)
    return item


# 工程建设方法

def parse2dict_contact_gcjs(list, regx=r'^[\t ]*[\d（(]|采购人|釆购人|招标人|项目联系|代理|机构'):
    dict = {}
    last_index = -1
    last_title = ''
    with_first_line = False
    for index, row in enumerate(list):
        row = re.sub(r'\s+', '', row)
        if re.search(regx, row) and not re.search(r'地址|电话|邮箱', row):
            if not with_first_line and len(re.split(r'[：:]', row)) == 2:
                with_first_line = True
            if not last_index == -1:
                dict[last_title] = list[last_index:index] if with_first_line else list[last_index + 1:index]
            last_index = index
            last_title = row
    if not last_index == -1:
        dict[last_title] = list[last_index:] if with_first_line else list[last_index + 1:]
    return dict


def process_callbid_contact_gcjs(dict: dict):
    if not dict:
        return {}
    for key in dict.keys():
        if re.search('联系', key):
            flag_2col = False
            line_limit = 4
            for row in dict[key]:
                line_limit -= 1
                if line_limit <= 0:
                    break
                if len(re.findall(r'[:：]', row)) >= 2:
                    flag_2col = True
                    break
            if flag_2col:
                return __process_callbid_contact_from_2col_gcjs(dict[key])
            else:
                return __process_callbid_contact_from_list_gcjs(dict[key])

    return {}


def __process_callbid_contact_from_list_gcjs(list):
    dict1 = parse2dict_contact_gcjs(list)
    item = {}
    if len(dict1) >= 1:
        for key in dict1.keys():
            if 'agent_unit' not in item and re.search('机构|代理', key):
                dict2 = parse2dict(dict1[key])
                item['agent_unit'] = match(dict2, '名|机构|代理')
                item['agent_unit_address'] = match(dict2, '地')
                item['agent_unit_p'] = match(dict2, '联系人')
                item['agent_unit_m'] = match(dict2, '方式|方法|电话|邮箱')

            elif 'proj_unit' not in item and re.search('(?:采购|釆购|招标)人', key):
                dict2 = parse2dict(dict1[key])
                item['proj_unit'] = match(dict2, '招标人|名')
                item['proj_unit_address'] = match(dict2, '地')
                item['proj_rel_p'] = match(dict2, '联系人')
                item['proj_rel_m'] = match(dict2, '方式|方法|电话|邮箱')

    clean_contact(item)
    clean_dict(item)
    return item


def __process_callbid_contact_from_2col_gcjs(list):
    item = {}
    call_col = 1
    agent_col = 2
    for row in list:
        row = re.sub(r'\s+', '', row)
        names = re.split(r'招标.*?[:：]', row)
        if len(names) >= 3:
            if re.search(r'代理|机构', names[1]):
                call_col = 2
                agent_col = 1
            item['proj_unit'] = names[call_col]
            item['agent_unit'] = names[agent_col]
            break
    for row in list:
        row = re.sub(r'\s+', '', row)
        if 'call_unit_address' not in item:
            addresses = re.split(r'地.*?[:：]', row)
            if len(addresses) >= 3:
                item['proj_unit_address'] = addresses[call_col]
                item['agent_unit_address'] = addresses[agent_col]
                continue

        if 'agent_unit_m' not in item:
            methods = re.split(r'(?:电话|邮箱|联系方式).*?[:：]', row)
            if len(methods) >= 3:
                item['proj_rel_m'] = methods[call_col]
                item['agent_unit_m'] = methods[agent_col]
                continue

        if 'agent_unit_p' not in item:
            persons = re.split(r'联系人.*?[:：]', row)
            if len(persons) >= 3:
                item['proj_rel_p'] = persons[call_col]
                item['agent_unit_p'] = persons[agent_col]
                continue

    clean_contact(item)
    clean_dict(item)

    return item


def process_callbid_tender_gcjs(dict: dict):
    item = {}
    if not dict:
        return item
    for key in dict.keys():
        if re.search('投标(?!人|须知|说明|保)|提交|递交', key):
            for row in dict[key]:
                row = re.sub(r'\s+', '', row)
                end_time = re.findall(r'(?=截至|截止|至|时间[：:]).*(\d{4}[-年]\d+[-月]\d+(?:日|)(?:\s|)(?:\d+[时:：]\d+|))', row)

                if len(end_time) > 0:
                    item['bid_end_time'] = end_time[0]

                place = re.findall(r'(?:携|持|通过|使用|登录|地点[：:]).*?(?=提交|投递|递交|进行|上传|参与|投标|，|。)', row)
                if len(place) > 0:
                    item['tender_place'] = place[0]
            return item

    clean_dict(item)

    return item


def process_callbid_file_gcjs(dict: dict):
    item = {}
    if not dict:
        return item
    for key in dict.keys():
        if re.search('标书|招标文件|获取.*文件', key):
            for row in dict[key]:
                row = re.sub(r'\s+', '', row)
                sentences = re.split(r'[,，。；;]', row)
                # 分句
                for st in sentences:
                    if 'bid_sale_op_time' not in item or 'bid_sale_en_time' not in item:
                        time = re.findall(r'\d{4}[-年]\d+[-月]\d+(?:日|)(?:\s|)(?:\d+[时:：]\d+|)', st)

                        if len(time) >= 2 and re.search(r'至', st):
                            item['bid_sale_op_time'] = time[0]
                            item['bid_sale_en_time'] = time[1]
                        elif len(time) == 1:
                            if re.search(r'截至|结束', st):
                                item['bid_sale_end_time'] = time[0]
                            if re.search(r'开始|取|下载|', st):
                                item['bid_sale_op_time'] = time[0]

                    if 'bid_sale_m' not in item:
                        method = re.findall(r'(?:携|持|通过|使用|登录|从|在|地点[：:]).*?(?:下载|取)', row)
                        if len(method) > 0:
                            item['bid_sale_m'] = method[0]
                            item['bid_sale_place'] = method[0]

                money = re.search(r'([\d.,，]+元)', row)
                if money:
                    item['bid_price'] = money.group()

            return item

    clean_dict(item)

    return item


# 工程建设中标方法
def process_winbid_common_GCJS(list):
    item = {}
    for row in list:
        row = re.sub(r'\s+', '', row)

        if 'price_ceiling' not in item:
            money = re.findall('(?=限价|报价)(?:：|:|).*?([\d.,，]+(?:万元|万|元|))', row)
            if len(money) > 0:
                item['price_ceiling'] = money[0]
                continue

        if 'opening_time' not in item:
            opening_time = re.findall(r'(?:开标|公式|开始|开启)时间.*?(\d{4}[-年/]\d+[-月/]\d+(?:日|)(?:\s|)(?:\d+[时:：]\d+|))', row)
            if len(opening_time) > 0:
                item['opening_time'] = opening_time[0]
                continue

        if 'notice_period' not in item:
            if re.search('公示期', row):
                notice_period = re.findall(r'(\d{4}[-年/]\d+[-月/]\d+(?:日|)(?:\s|)(?:\d+[时:：]\d+|))', row)
                if len(notice_period) >= 2:
                    item['notice_period'] = notice_period[0] + '至' + notice_period[1]
                    continue

    clean_dict(item)
    return item


def get_wb_supplier(list):
    item = {}
    for row in list:
        row = re.sub(r'\s+', '', row)

        if 'supp_amount' not in item:
            money = re.findall('(?=中标价|中标金|成交价|成交金)(?:：|:|).*?([\d.,，]+(?:万元|万|元|))', row)
            if len(money) > 0:
                item['supp_amount'] = money[0]
                continue

        if 'supp_name' not in item:
            name = re.findall('中标(?:人|单位|公司).*[:：](.*?)(?:，|。|；|$)', row)
            if len(name) > 0:
                item['supp_name'] = name[0]
                item['supp_code'] = name[0]
                item['supp_ranking'] = 1
                continue
    clean_dict(item)

    return item


def is_table(html):
    table = html.xpath("//div[@class='detail']/div[@id='mycontent']/div[@class='detail_content']/table")
    trs = table.xpath('./tr')

    if table and len(trs) >= 5:
        return True
    else:
        return False


def get_region_from_str(string: str, ex=''):
    if not string:
        return ''
    pro = cpca.transform([string]).loc[0, "省"] or ''
    city = cpca.transform([string]).loc[0, "市"] or ''
    area = cpca.transform([string]).loc[0, "区"] or ''

    region = pro + '.' + city + '.' + area

    return region

    # partten = re.compile(
    #     r'([\u4e00-\u9fa5]{2,5}?(?:省|自治区|市)){0,1}([\u4e00-\u9fa5]{2,5}?(?:市)){0,1}([\u4e00-\u9fa5]{2,7}?(?:区|县|州)){0,1}([\u4e00-\u9fa5]{2,7}?(?:镇)){0,1}')
    # region = partten.search(string)
    #
    # if not region:
    #     return ''
    #
    # parts = []
    # for part in region.groups():
    #     if part and isinstance(part, str):
    #         parts.append(part)
    #
    # res = '.'.join(parts)
    #
    # if not re.search('市', res) and not ex == '':
    #     s = re.findall('^[\u4e00-\u9fa5]{2,5}?(?:市)', ex)
    #     if len(s) == 1:
    #         if res == '':
    #             res = s[0]
    #         else:
    #             res = s[0] + '.' + res
    #
    # if not re.search('省', res) and not ex == '':
    #     p = get_province_from_str(ex)
    #     if not p == '':
    #         if res == '':
    #             res = p[0]
    #         else:
    #             res = p + '.' + res
    #
    # return res

def get_province_from_str(string: str):
    if not string:
        return ''
    region = re.findall(
        r'(湖南|湖北|广东|广西|河南|河北|山东|山西|江苏|浙江|江西|黑龙江|新疆|云南|贵州|福建|吉林|安徽|四川|西藏|宁夏|辽宁|青海|甘肃|陕西|内蒙古|台湾|北京|上海|天津)',
        string)

    if len(region) > 0:
        return region[0] + '省'

    return ''
