import re

from BaseSpider.base_component.utils.util import k_remove, remove


# 按指定标签拆解内容
# response:请求返回参数
# typed：用于分解的标签
# d_str: 键值分隔符
def dismantling(response, typed, d_str):
    t = response.xpath("//" + typed)
    val = []
    # 形成按标签分解的列表
    for i in t:
        content = i.xpath('.//text()').extract()
        content = ''.join(content)
        val.append(remove1(content))  # 删除无效字符
    return row_class_separation(val, d_str)


# 通过文本解析匹配
def search_all_by_text(start, end, response, d_str, search_type=1):
    contents = response.xpath('//text()').extract()
    recode = False
    r = []
    for c in contents:
        if c.find(end) != -1 and end != '':
            recode = False
        if recode:
            r.append(c)
        if c.find(start) != -1:
            recode = True
    if d_str == '':
        return '\n'.join(r)
    if search_type == 1:
        return row_class_separation(r, d_str)
    elif search_type == 2:
        return cross_label(r, d_str)


# 通过指定标签匹配
# start：开始标志
# end:结束标志
# response:请求返回信息
# typed:标签类型
# d_str:分隔符，为''时返回整个str
# search_type:查询的内容位置，按行查询，跨行(下一行）
def search_all_by_xpath(start, end, response, typed, d_str, search_type=1, ones=False):
    t = response.xpath("//" + typed)
    r = []
    recode = False
    for i in t:
        c = i.xpath('.//text()').extract()
        c = ''.join(c)
        if c.find(end) != -1 and end != '':
            recode = False
            if ones: break
        if recode:
            r.append(c)
        if c.find(start) != -1:
            recode = True
    if d_str == '':
        return '\n'.join(r)
    if search_type == 1:
        return row_class_separation(r, d_str)  # 当前行解析
    elif search_type == 2:
        return cross_label(r, d_str)  # 跨行（跨标签）


def search_all(start, end, response, typed, d_str, search_type=1):
    t = response.xpath("//" + typed)
    r = []
    recode = False
    for i in t:
        c = i.xpath('.//text()').extract()
        c = ''.join(c)
        if c.find(start) != -1:
            recode = True
        if c.find(end) != -1 and end != '':
            recode = False
        if recode:
            r.append(c)
    if d_str == '':
        return '\n'.join(r)
    if search_type == 1:
        return row_class_separation(r, d_str)  # 当前行解析
    elif search_type == 2:
        return cross_label(r, d_str)  # 跨行（跨标签）


# 跨行（跨标签）解析
def cross_label(val, d_str):
    li = []
    ls = division(val, d_str)
    ls = [i for i in ls if i is not None]
    for l in ls:
        li += l
    item = {}
    if len(li) > 1:
        for index in range(len(li) - 1):
            item[k_remove(li[index])] = remove(li[index + 1])
    return item


def row_class_separation(val, d_str):
    li = division(val, d_str)  # 按分隔符分割内容
    li = [i for i in li if i != [''] and i is not None]  # 去除空列表
    # 生成重叠式字典 {1:2,2:3,3:4...}
    item = {}
    for i in li:
        if len(i) > 1:
            for index in range(len(i) - 1):
                item[k_remove(i[index])] = remove(i[index + 1])
        if len(i) == 1:
            item[k_remove(i[0])] = ''
    return item


# 删除无效字符
def remove1(string):
    regex = re.compile(r'|\n|\t| |\xa0|\u3000', re.S)
    return regex.sub('', string)



# 按指定分隔符分隔文本
# old：待分割str
# d_str：分隔符
def division(old, d_str):
    new = []
    if isinstance(old, list):
        for s in old:
            new.append(division(s, d_str))
        return new
    elif isinstance(old, str):
        for i in old:
            return re.split(d_str, remove1(old))
