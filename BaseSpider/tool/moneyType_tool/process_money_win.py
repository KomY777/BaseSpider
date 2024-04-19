from BaseSpider.tool.moneyType_tool.MoneyType import change_money


class process_money_win(object):
    def __init__(self):
        self.type = 'WB_G'
    def judge(self,type,page_attr):
        content = page_attr[type]
        page_attr[type]['actual_price'] = change_money(content['actual_price'])