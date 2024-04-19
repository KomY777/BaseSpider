from BaseSpider.tool.judge_tool.content_count import content_count


class dishonest_list_judge(object):
    def __init__(self):
        self.type = 'DL'

    def judge(self, content):
        return True
