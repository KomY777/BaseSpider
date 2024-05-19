import json
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from BaseSpider.tool.CountDownLatch import CountDownLatch
from BaseSpider.tool.RequestTool import HttpSession
from BaseSpider.tool.classpath_get_obj import resolver_loader
from BaseSpider.tool.judge_tool.agency_list_judge import agency_list_judge
from BaseSpider.tool.judge_tool.dishonest_list_judge import dishonest_list_judge
from BaseSpider.tool.judge_tool.engineering_judge_call import engineering_judge_call
from BaseSpider.tool.judge_tool.engineering_judge_result import engineering_judge_result
from BaseSpider.tool.judge_tool.judge_adapter import judge_adapter
from BaseSpider.tool.judge_tool.process_judge_call import process_judge_call
from BaseSpider.tool.judge_tool.process_judge_fail import process_judge_fail
from BaseSpider.tool.judge_tool.process_judge_mo import process_judge_mo
from BaseSpider.tool.judge_tool.process_judge_win import process_judge_win
from BaseSpider.tool.judge_tool.intention_judge import intention_judge
from BaseSpider.tool.judge_tool.med_an_judge import med_an_judge
from BaseSpider.tool.moneyType_tool.ProcessMoney_adapter import process_money
from BaseSpider.api.admin import get_spider_info
from BaseSpider.api.announcement_db import instance as AnnouncementDBRequest

# 数据库加载配置信息
SPIDER_PARAMS_MAP = {
    # 爬虫名
    'NAME': 'BASE_SPIDER',
    # 爬虫公告类型
    'AN_TYPE': 'the announcement type of spider',
    # 解析器基础路径
    'BASE_PATH': 'BaseSpider.base_component.',
    # 公告页面解析器
    'PATH_READ_HM_RESOLVER': [],
    'ASSEMBLY_S': [],  # 解析器信息 : [{'resolve':resolve,'subcomponents':subcomponents,'path':path}]
}


class MultithreadingAnalysis:
    logging.getLogger().setLevel(logging.INFO)  # 设置日志级别为info

    def __init__(self, spider_id):
        self.http = AnnouncementDBRequest
        self.spider_id = spider_id
        self.thread_pool = ThreadPoolExecutor(max_workers=5)  # 线程池(最大线程数为10)
        self.count_down_latch = CountDownLatch(count=0)
        self.already_resolved_num = 0  # 已解析数量

    def load_resolver_path(self):
        """
        初始化组件信息
        :return:
        """
        # 设置公告类型
        this_spider = get_spider_info(self.spider_id)
        SPIDER_PARAMS_MAP['AN_TYPE'] = this_spider.an_type
        SPIDER_PARAMS_MAP['ASSEMBLY_S'] = []
        for resolve in this_spider.resolvers.get('READ_HM'):
            # 设置组件路径
            SPIDER_PARAMS_MAP['ASSEMBLY_S'].append(resolve)

    def data_load(self, data):
        """
        使用线程池加载页面进行解析
        :return:
        """
        if len(data) != 0:
            # 将这些页面id存入数据队列
            for item in data:
                self.thread_pool.submit(self.parse_response_data, item).add_done_callback(self.call_back)
            self.count_down_latch.count = len(data)
            self.count_down_latch.wait()
        else:
            logging.info('no data to resolve')

    def call_back(self, res):
        """
        回调函数,同步锁剩余值修改
        :param res:
        :return:
        """
        res_exception = res.exception()
        if res_exception:
            logging.exception("Worker return exception: {}".format(res_exception))
        self.count_down_latch.count_down()
        self.already_resolved_num += 1
        logging.info(str(self.already_resolved_num) + ' resolve finished')

    def parse_response_data(self, data):
        """
        数据解析、信息入库
        """
        try:
            page_attr = self.resolve_announce(data['content'], data['url'])  # 解析页面
        except Exception as e:
            logging.error("Resolve    Error：" + str(e))
            logging.exception("Resolve    Error：")
            return None

        if not page_attr:
            page_attr = {}

        # 数据格式化
        if SPIDER_PARAMS_MAP['AN_TYPE'] in {'CB_G', 'WB_G'}:
            process_money(SPIDER_PARAMS_MAP['AN_TYPE'], page_attr)

        # 公告数据入库
        if len(page_attr) != 0:
            self.write_ann_to_db(page_attr)

    def resolve_announce(self, response_text, response_url) -> dict:
        """
        解析公告
        :param response_text:
        :param response_url:
        :return:
        """
        # 解析器个数
        length = len(SPIDER_PARAMS_MAP['ASSEMBLY_S'])
        # 解析器循环调用
        for index, path in enumerate(SPIDER_PARAMS_MAP['ASSEMBLY_S']):
            # 装载解析器
            read_hm_resolver = resolver_loader(path)
            setattr(read_hm_resolver, 'response_url', response_url)
            setattr(read_hm_resolver, 'response_text', response_text)
            setattr(read_hm_resolver, 'annoucement_type', SPIDER_PARAMS_MAP['AN_TYPE'])

            # 调用resolver_page()方法解析页面
            page_attr = getattr(read_hm_resolver, 'resolver_page')()

            if page_attr == {} or page_attr == None:
                page_attr = {SPIDER_PARAMS_MAP['AN_TYPE']: {}}

            # 判断数据是否合格
            calibrate = self.process_judge(SPIDER_PARAMS_MAP['AN_TYPE'], page_attr[SPIDER_PARAMS_MAP['AN_TYPE']])

            # 解析失败后判断是否进入下个解析器
            if not calibrate:
                if index == length - 1:
                    return {}
                continue
            # 解析成功
            if len(page_attr) != 0 and calibrate:
                # 判断公告标题是否存在
                _title = page_attr[SPIDER_PARAMS_MAP['AN_TYPE']]['title']
                if _title == '' or _title is None:
                    return {}
                page_attr['an_type'] = SPIDER_PARAMS_MAP['AN_TYPE']

                return page_attr

    # 不同公告类型选择不同适配器
    def process_judge(self, type, content):
        judge_dict = {'CB_G': process_judge_call(),
                      'WB_G': process_judge_win(),
                      'FB_G': process_judge_fail(),
                      'MB_G': process_judge_mo(),
                      'CB_E': engineering_judge_call(),
                      'RB_E': engineering_judge_result(),
                      'AG_L': agency_list_judge(),
                      'DL': dishonest_list_judge(),
                      'I_G': intention_judge(),
                      'MED_AN': med_an_judge()}
        judge_method = judge_dict[type]
        if content == {}:
            return False
        judge_content = judge_adapter(type, dict(judge=judge_method.judge))
        return judge_content.judge(content)

    # 公告数据入库
    def write_ann_to_db(self, item):
        try:
            x = json.dumps(item)
            an_id = self.http.request(r'/add_an_to_db', {'item': x}).json()
            an_id = an_id['an_id']
            return {'an_id': an_id, 'error': None}
        except AttributeError as abe:
            logging.error('Database connection error：' + str(abe.args))
            return {'an_id': None, 'exception_type': 'spider exception', 'reason': abe}
        except Exception as e:
            logging.warning('Data into inventory is error：' + str(e.args))
            return {'an_id': None, 'exception_type': 'resolver exception', 'reason': e}

    def run(self, data):
        """
        启动方法
        :return:
        """
        self.load_resolver_path()  # 更新父组件版本号
        self.data_load(data)
