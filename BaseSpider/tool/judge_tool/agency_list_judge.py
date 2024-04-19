from BaseSpider.tool.judge_tool.content_count import content_count


class agency_list_judge(object):
    def __init__(self):
        self.type = 'AG_L'
    def judge(self,content):
        countlist = ["OrgName", "OrgCode", "UpId", "UpName", "IdentityState","ImportTime", "MainProperty", "BusTerm",
                     "FoundTime", "RegMoney", "Linkman", "LinkmanName", "LinkmanPhone", "Remark", "LocalProv",
                     "LocalProvName", "LocalCity", "LocalCityName", "LocalCounty", "LocalCountyName", "LocalAddr",
                     "PostCode", "MainScope", "ConcurrentlyScope", "TradeType", "TradeTypeName", "CompanyType",
                     "LegalPerson", "LegalPersonIdentity", "LegalPersonEmail", "LegalPersonPhone", "RegAddress",
                     "EffectAreaId", "EffectAreaName", 'web_site', 'source_web_name']

        if content_count(content, countlist) > 0.3:
            return True
        else:
            return False
