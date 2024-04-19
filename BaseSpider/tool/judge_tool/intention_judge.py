from BaseSpider.tool.judge_tool.content_count import content_count

class intention_judge(object):
    def __init__(self):
        self.type = 'I_G'

    def judge(self, content):
        return self.judge_rate(content)

    @staticmethod
    def judge_rate(content):
        count_list = [
            'province', 'city', 'region', 'level', 'call_unit', 'purchase_unit',
            'title', 'acnm_time', 'total_budget', 'source_website', 'source_url'
        ]

        count = content_count(content, count_list)
        print(count)
        if count >= 0.75:
            return True
        else:
            return False
