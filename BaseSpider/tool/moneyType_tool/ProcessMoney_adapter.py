from BaseSpider.tool.moneyType_tool.process_money_call import process_money_call
from BaseSpider.tool.moneyType_tool.process_money_win import process_money_win


class ProcessMoney_adapter(object):

    def __init__(self, type,func):
        self.type = type
        self.__dict__.update(func)

    def judge(self,type,page_attr):
        pass

def process_money(type,page_attr):
    judge_dict = {'CB_G':process_money_call(),
                  'WB_G':process_money_win()}
    if page_attr and page_attr != {}:
        judge_method = judge_dict.get(type)
        judge_content = ProcessMoney_adapter(type,dict(judge=judge_method.judge))
        judge_content.judge(type,page_attr)