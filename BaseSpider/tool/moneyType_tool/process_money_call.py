from BaseSpider.tool.moneyType_tool.MoneyType import change_money


class process_money_call(object):
    def __init__(self):
        self.type = 'CB_G'
    def judge(self,type,page_attr):
        content = page_attr[type]
        page_attr[type]['budget'] = change_money(content['budget'])
