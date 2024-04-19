from BaseSpider.tool.judge_tool.content_count import content_count
import logging

class process_judge_call(object):
    def __init__(self):
        self.type = 'CB_G'

    def judge(self, content):
        key_list = ['proj_code', 'call_unit', 'agent_unit_name']

        if not content.get('proj_name', None) or not content.get('ancm_time', None):
            return False

        for i in range(len(key_list)):
            if not content.get(key_list[i], None):
                if self.judge_rate(content):
                    return True
                else:
                    return False
        return True

    @staticmethod
    def judge_rate(content):
        count_list = ['proj_name', 'call_unit', 'ancm_time', 'budget', 'proj_rel_p', 'proj_rel_m', 'agent_unit_name',
                      'agent_unit_address', 'agent_unit_p', 'agent_unit_m', 'tender_place', 'bid_sale_m',
                      'bid_sale_op_time', 'bid_sale_en_time', 'bid_sale_place', 'bid_price', 'sourse_url', 'bid_time',
                      'title', 'web_site', 'source_web_name']

        count = content_count(content, count_list)
        if count >= 0.42:
            return True
        else:
            return False
