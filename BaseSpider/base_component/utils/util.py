# -*- coding: utf-8 -*-
import re


def k_remove(orstr: str) -> str:
    regex = re.compile(r'(^[一二三四五六七八九十]+)、|\d+|\n|\t| |\xa0|、|:|：|\r|\u3000', re.S)
    return regex.sub('', orstr)


def remove(orstr: str) -> str:
    regex = re.compile(r'|\n|\t| |\xa0|\r', re.S)
    return regex.sub('', orstr)


def remove1(orstr: str) -> str:
    regex = re.compile(r'|\n|\t|\r', re.S)
    return regex.sub('', orstr)


def AG_L_remove(orstr: str) -> str:
    regex = re.compile(r'<[^>]+>|\n|\t| |\xa0|\r', re.S)
    return regex.sub('', orstr)


def provide_unit_address_remove(orstr: str) -> str:
    # 将特殊字符替换成中文逗号
    orstr = re.sub(r'<[^>]+>|&amp;|\n|\t|\xa0|\r|中标供应商名称、联系地址及中标金额', '，', orstr)
    # 将多个逗号相连的地方换成一个中文逗号
    orstr = re.sub(r'[， ]{2,}', '，', orstr)
    # 将冒号和逗号相连处换成冒号
    orstr = re.sub(r'[,，]*[:：][,，]*', '：', orstr)
    return orstr


def pxy_fee_and_standard_remove(orstr: str) -> str:
    # 将特殊字符替换成中文逗号
    orstr = re.sub(r'<[^>]+>|&amp;|\t|\xa0|\r', '，', orstr)
    # 将多个逗号相连的地方换成一个中文逗号
    orstr = re.sub(r'[， ]{2,}', '，', orstr)
    # 将冒号和逗号相连处换成冒号
    orstr = re.sub(r'[,，]*[:：][,，]*', '：', orstr)
    return orstr

