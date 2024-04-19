from BaseSpider.tool.judge_tool.engineering_judge_call import engineering_judge_call
from BaseSpider.tool.judge_tool.process_judge_call import process_judge_call
from BaseSpider.tool.judge_tool.process_judge_fail import process_judge_fail
from BaseSpider.tool.judge_tool.process_judge_mo import process_judge_mo
from BaseSpider.tool.judge_tool.process_judge_win import process_judge_win
from BaseSpider.tool.judge_tool.engineering_judge_result import engineering_judge_result


class judge_adapter(object):

    def __init__(self, type,func):
        self.type = type
        self.__dict__.update(func)

    def judge(self,content):
        pass

# 不同公告类型选择不同适配器
def process_judge(type,content):
    judge_dict = {'CB_G':process_judge_call(),
                  'WB_G':process_judge_win(),
                  'FB_G':process_judge_fail(),
                  'MB_G':process_judge_mo(),
                  'CB_E':engineering_judge_call(),
                  'RB_E':engineering_judge_result()}
    judge_method = judge_dict[type]
    if content == {}:
        return False
    judge_content = judge_adapter(type,dict(judge=judge_method.judge))
    return judge_content.judge(content)
