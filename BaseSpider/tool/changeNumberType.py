# 基础数字
cn_base_number = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
alb_base_number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']


# 将字符串中的数字改成阿拉伯数字
def change_number_in_str(string):
    str_list = list(string)
    for index in range(len(str_list) - 1):
        if str_list[index] in cn_base_number:
            str_list[index] = str(change_number_type(str_list[index]))
        elif str_list[index] == '十':
            if index != 0 and str_list[index - 1] in alb_base_number:
                if index != len(str_list) and str_list[index + 1] in cn_base_number:
                    str_list[index] = ''
                else:
                    str_list[index] = '0'
            else:
                if index != len(str_list) and str_list[index + 1] in cn_base_number:
                    str_list[index] = '1'
                else:
                    str_list[index] = '10'
    return ''.join(str_list)


# 将中文数字改成阿拉伯数字
def change_number_type(string):
    zhong = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
    danwei = {'十': 10, '百': 100, '千': 1000, '万': 10000}
    num = 0
    if len(string) == 0:
        return 0
    if len(string) == 1:
        if string == '十':
            return 10
        num = zhong[string]
        return num
    temp = 0
    if string[0] == '十':
        num = 10
    for i in string:
        if i == '零':
            temp = zhong[i]
        elif i == '一':
            temp = zhong[i]
        elif i == '二':
            temp = zhong[i]
        elif i == '三':
            temp = zhong[i]
        elif i == '四':
            temp = zhong[i]
        elif i == '五':
            temp = zhong[i]
        elif i == '六':
            temp = zhong[i]
        elif i == '七':
            temp = zhong[i]
        elif i == '八':
            temp = zhong[i]
        elif i == '九':
            temp = zhong[i]
        if i == '十':
            temp = temp * danwei[i]
            num += temp
        elif i == '百':
            temp = temp * danwei[i]
            num += temp
        elif i == '千':
            temp = temp * danwei[i]
            num += temp
        elif i == '万':
            temp = temp * danwei[i]
            num += temp
    if string[len(string) - 1] != '十' and string[len(string) - 1] != '百' and string[len(string) - 1] != '千' and \
            string[
                len(string) - 1] != '万':
        num += temp
    return num
