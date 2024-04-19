"""
名称格式转换
"""
import re


def getLowerCaseName(string):
    """
    驼峰转下划线
    :param string:
    :return:
    """
    lst = []
    for index, char in enumerate(string):
        if char.isupper() and index != 0:
            lst.append("_")
        lst.append(char)

    return "".join(lst).lower()


def getHumpCaseName(string):
    """
    下划线转驼峰式
    :param string:
    :return:
    """
    s = ""
    re_lst = re.split('_', string)
    for l in re_lst:
        s += l.capitalize()
    return s
