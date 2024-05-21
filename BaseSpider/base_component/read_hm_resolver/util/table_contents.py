from BaseSpider.base_component.utils.util import k_remove, remove


def transverse_table_contents(response) -> dict:
    """
    横向解析
    :param response:
    :return:
    """
    item = {}
    for re in response.xpath('.//table'):
        matrix = obtain_td_matrix(re)
        for tds in matrix:
            if len(tds) > 1:
                for index in range(len(tds) - 1):
                    item[k_remove(tds[index])] = remove(tds[index + 1])
    return item


def simple_direction_table_contents(response) -> dict:
    """
    纵向解析
    :param response:
    :return:
    """
    item = {}
    for re in response.xpath('.//table'):
        matrix = obtain_td_matrix(re)
        for i in range(len(matrix) - 1):
            td_key = matrix[i]
            td_value = matrix[i + 1]
            min_len = min(len(td_key), len(td_value))
            for j in range(min_len):
                key = td_key[j]
                value = td_value[j]
                item[key] = value
    return item


def two_dimensional_table(response) -> dict:
    """
    二维表格
    :param response:
    :return:
    """
    item = {}
    for re in response.xpath('.//table'):
        matrix = obtain_td_matrix(re)
        for i in range(len(matrix) - 1):
            td_key = matrix[i]
            td_value = matrix[i + 1:]
            for l in range(len(td_value)):
                min_len = min(len(td_value[l]), len(td_key))
                for j in range(min_len - 1):
                    for v in range(min_len - 1 - j):
                        v += j + 1
                        key1 = td_key[v]
                        key2 = td_value[l][j]
                        value = td_value[l][v]
                        item[str([key1, key2, v - j])] = value
    return item


def obtain_td_matrix(response) -> list:
    """
    获得td、th规则矩阵
    对colspan、rowspan自动扩充
    :param response:
    :return:
    """
    table = response
    li = []
    ths = table.xpath('./th')
    if ths:
        td_contents = []
        for one in ths:
            td_contents.append(''.join(one.xpath('.//text()').extract()))
        li.append(td_contents)

    tr = table.xpath('.//tr')

    # 处理
    if len(tr) == 1:
        pass

    rowspan = {}

    for i in tr:
        td = i.xpath("./td|./th")
        td_contents = []
        colspan = {}
        for ia in td:
            td_contents.append(''.join(ia.xpath('.//text()').extract()))

        # col_rew = i.xpath("./td[@colspan]//text()|./th[@colspan]//text()").extract()
        # for val in col_rew:
        #     for ia in range(len(td_contents)):
        #         if val == td_contents[ia]:
        #             count = i.xpath('(//*[contains(.,\'' + val + '\')][@colspan])[1]/@colspan').get()
        #             colspan[val] = [ia, int(count) - 1]
        #
        # for val in colspan:
        #     ic = colspan[val]
        #     for ib in range(ic[1]):
        #         td_contents.insert(ic[0], val)
        # em_list = []
        # for val in rowspan:
        #     td_contents.insert(rowspan[val][0], val)
        #     rowspan[val][1] -= 1
        #     if rowspan[val][1] == 0:
        #         em_list.append(val)
        # for val in em_list:
        #     rowspan.pop(val)
        #
        # se_row = i.xpath("./td[@rowspan]//text()|./th[@rowspan]//text()").extract()
        # for val in se_row:
        #     for ia in range(len(td_contents)):
        #         if val == td_contents[ia]:
        #             count = i.xpath('(//*[contains(.,\'' + val + '\')+@rowspan])[1]/@rowspan').get()
        #             if count is None:
        #                 count = 2
        #             rowspan[val] = [ia, int(count) - 1]
        li.append([remove_empty_space(i) for i in td_contents])
    return li


def remove_empty_space(s):
    return s.replace(' ', '').replace('\t', '').replace('\r', '').replace('\n', '')
