from BaseSpider.tool.judge_tool.content_count import content_count


class process_judge_win(object):
    def __init__(self):
        self.type = 'WB_G'

    def judge(self, content):
        key_list = ['call_unit', 'agent_unit_name', 'provide_unit']

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
        count_list = ['proj_name', 'call_unit', 'ancm_time', 'actual_price', 'proj_rel_p',
                      'proj_rel_m', 'agent_unit_name', 'agent_unit_address', 'agent_unit_p',
                      'agent_unit_m', 'sourse_url', 'bid_time', 'provide_unit', 'review_time',
                      'review_place', 'title', 'web_site', 'source_web_name']
        count = content_count(content, count_list)
        # print('达标率：', count)
        if count >= 0.4:
            return True
        else:
            return False


