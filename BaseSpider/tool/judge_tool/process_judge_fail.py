from BaseSpider.tool.judge_tool.content_count import content_count


class process_judge_fail(object):
    def __init__(self):
        self.type = 'FB_G'

    def judge(self, content):
        key_list = ['proj_code', 'purchasing_unit_name', 'agent_unit_name']

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
        count_list = ['proj_name', 'ancm_time', 'purchasing_unit_name', 'proj_rel_p', 'proj_rel_m', 'agent_unit_name',
                      'agent_unit_address', 'agent_unit_p', 'agent_unit_m', 'purchase_m', 'failure_content',
                      'sourse_url', 'web_site', 'source_web_name']

        count = content_count(content, count_list)
        # print('达标率：', count)
        if count >= 0.5:
            return True
        else:
            return False
