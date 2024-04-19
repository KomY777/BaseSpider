import re
from decimal import Decimal


# 金额转换为具体数值
def change_money(money):
    money = str(money)
    money = money.replace(',', '').replace('，', '')  # 移除中英文逗号
    number = re.findall(r"\d+\.?\d*", money)
    if len(number) < 1:
        return ''
    elif len(number) > 1:
        return money
    return float(Decimal(number[0])*Decimal(get_money_suffix(money)))


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