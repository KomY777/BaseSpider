from BaseSpider.tool.judge_tool.content_count import content_count


class engineering_judge_result(object):
    def __init__(self):
        self.type = 'RB_E'
    def judge(self,content):
        countlist = ['title', 'proj_name', 'proj_code', 'opening_time', 'notice_period', 'price_ceiling',
                     'proj_rel_p','proj_rel_m', 'agent_unit_p', 'agent_unit_m', 'ancm_time', 'web_site', 'source_web_name']

        if content_count(content, countlist) > 0.3:
            return True
        else:
            return False