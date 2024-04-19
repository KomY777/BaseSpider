from BaseSpider.tool.judge_tool.content_count import content_count


class engineering_judge_call(object):
    def __init__(self):
        self.type = 'CB_E'
    def judge(self,content):
        countlist = ['proj_name', 'title', 'proj_place', 'resource_from', 'ET', 'bid_sale_m',
                     'bid_sale_op_time','bid_sale_en_time', 'bid_price', 'bid_sale_place', 'proj_unit',
                     'proj_rel_p', 'proj_rel_m', 'agent_unit', 'agent_unit_p', 'agent_unit_m',
                     'ancm_time', 'sourse_url', 'source_web_name', 'web_site']

        if content_count(content, countlist) > 0.5:
            return True
        else:
            return False