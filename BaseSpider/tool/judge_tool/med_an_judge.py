from BaseSpider.tool.judge_tool.content_count import content_count

class med_an_judge(object):
    def __init__(self):
        self.type = 'MED_AN'

    def judge(self, content):
        return self.judge_rate(content)

    @staticmethod
    def judge_rate(content):
        return True
        # if content.get('catalog'):
        #     return True
        # else:
        #     return False
