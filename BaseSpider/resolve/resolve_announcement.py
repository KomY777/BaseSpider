import json
import logging
import re
import sys
import threading
import time
# sys.path.append('C:\\Users\\pc\\Desktop\\project\\SpiderCilent\\BaseSpider')
from json import JSONDecodeError
from concurrent.futures.thread import ThreadPoolExecutor

from BaseSpider.tool import ClassReflection
from BaseSpider.tool.CountDownLatch import CountDownLatch
from BaseSpider.tool.RequestTool import HttpSession, HttpRequest
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

# 数据库加载配置信息
SPIDER_PARAMS_MAP = {
    # 爬虫名
    'NAME': 'BASE_SPIDER',
    # redis 键值
    'REDIS_KEY': 'temp_key',
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

    def __init__(self, spider_id, section):
        self.http = HttpSession()
        self.httpRequest = HttpRequest()
        self.spider_id = spider_id
        self.section = section  # 已入库数量(考虑是否放掉)
        self.thread_pool = ThreadPoolExecutor(max_workers=10)  # 线程池(最大线程数为10)
        self.count_down_latch = CountDownLatch(count=0)
        self.already_resolved_num = 0  # 已解析数量

    def load_resolver_path(self):
        """
        初始化组件信息
        :return:
        """
        READ_HM_TYPE = 'READ_HM'

        # 设置公告类型
        this_spider = self.httpRequest.request('GET', 'baseInfo', {'spider_id': self.spider_id}).json()['data']
        SPIDER_PARAMS_MAP['AN_TYPE'] = this_spider['info']['an_type']

        for resolve in this_spider['resolvers']:
            # 查询子组件信息
            sub_dict = self.get_sub_component(resolve['id'])

            # 更新版本号
            self.update_version_no(resolve, sub_dict['version_no'])

            SPIDER_PARAMS_MAP['ASSEMBLY_S'] = []

            # 设置组件路径
            SPIDER_PARAMS_MAP['ASSEMBLY_S'].append({'resolve': resolve,
                                                    'subcomponents': sub_dict['subcomponents'],
                                                    'path': 'http://localhost:9000/' +resolve['class_path'],
                                                    'class_name': resolve['class_name']})

    def update_version_no(self, resolve, version_no):
        """
        同步版本号
        :param resolve:
        :param version_no:
        :return:
        """
        if version_no != resolve['version_no']:
            self.http.request(r'resolver_update', {'resolver_id': resolve['id'], 'version_no': version_no})
            resolve['version_no'] = version_no

    def get_sub_component(self, par_comp_id):
        """
        通过父组件查询子组件
        :param par_comp_id:
        :return: {'version_no': new_version_no, 'subcomponents': response['sub_components']}
        """
        new_version_no = ''
        response = self.http.request(r'sub_comp_query_by_parent', {'par_comp_id': par_comp_id}).json()
        for item in response['sub_components']:
            new_version_no += item['version_no']
        return {'version_no': new_version_no, 'subcomponents': response['sub_components']}

    def data_load(self):
        """
        使用线程池加载页面进行解析
        :return:
        """
        response = self.http.request(r'chtml_query_by_spider_id', {'spider_id': self.spider_id,
                                                                   'section': self.section}).json()
        if len(response['data_list']) != 0:
            # 将这些页面id存入数据队列
            for item in response['data_list']:
                self.thread_pool.submit(self.parse_response_data, item).add_done_callback(self.call_back)

            # 设置同步锁
            self.count_down_latch.count = len(response['data_list'])

            # 等待所有加入才可结束
            self.count_down_latch.wait()

            # 递归遍历
            self.data_load()
        else:
            logging.info('no data to resolve')

    def parse_response_data(self, response_id):
        """
        线程方法
        :param response_id:
        :return:
        """
        ResolveResponse(self.spider_id).parse_response_data(response_id)

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

    def run(self):
        """
        启动方法
        :return:
        """
        #        while True:
        #            try:
        #                self.load_resolver_path()  # 更新父组件版本号
        #                self.data_load()
        #            except JSONDecodeError:
        #                continue

        self.load_resolver_path()  # 更新父组件版本号
        self.data_load()


class ResolveResponse:

    def __init__(self, spider_id):
        self.spider_id = spider_id
        self.http = HttpSession()

    def parse_response_data(self, response_id):
        """
        解析response起始方法
        :param response_id:
        :return:
        """
        response = self.get_response_data_by_id(response_id)  # 通过id得到response数据

        if self.judge_join_task_queue(response):
            self.parse_response_data1(response)

    def get_response_data_by_id(self, id):
        """
        根据id查询response数据
        :param id:
        :return:
        """
        result = self.http.request(r'chtml_query_by_id', {'id': id}).json()
        return result['html']

    def judge_join_task_queue(self, result):
        """
        函数：查询response数据-解析数据关联表判断是否加入任务队列,
        若关系表中不存在与该公告相关记录就解析该公告,若存在就判断版本号是否为最新,若不是最新就对该公告进行解析
        删除待更新公告管理信息
        :param result:
        :return:
        """
        rel_object = self.http.request(r'rdr_query_object', {'response_id': result['id']}).json()

        if not rel_object['rel']:  # 关联表是否存在相关信息
            return True
        else:
            version_no = None

            # 查询指定解析器版本号
            for assembly in SPIDER_PARAMS_MAP['ASSEMBLY_S']:
                if assembly['resolve']['priority'] == rel_object['rel'][0]['priority']:
                    version_no = assembly['resolve']['version_no']
                    break

            if rel_object['rel'][0]['version_no'] != version_no:  # 关联信息版本号表是否最新
                self.delete_data_rel(result['id'], rel_object['rel'][0])  # 删除关联信息
                return True

        return True

    # 删除response数据id相关解析数据
    def delete_data_rel(self, response_id, rel_object):
        # 删除关联表记录
        self.http.request(r'rdr_delete_all', {'response_id': response_id})
        # 删除数据表记录
        self.http.request(r'an_delete_all', {'cls_type': rel_object['type'], 'announce_id': rel_object['an_id']})

    def parse_response_data1(self, response):
        """
        数据解析、信息入库
        """
        try:
            page_attr = self.resolve_announce(response['content'], response['url'])  # 解析页面
        except Exception as e:
            self.http.request(r'chtml_update_section_neg', {'response_id': response['id'],
                                                            'section': (int(response['section']) - 1)})
            logging.info("Resolve    Error：" + str(e))
            logging.exception("Resolve    Error：")
            return None
        self.http.request(r'chtml_update_section_neg', {'response_id': response['id'],
                                                        'section': (int(response['section']) - 1)})
        logging.info(str(threading.currentThread().getName()) + ' start resolve, response_id: %s, an_type: %s' % (
            response['id'], SPIDER_PARAMS_MAP['AN_TYPE']))

        if not page_attr:
            page_attr = {}

        # 数据格式化
        if SPIDER_PARAMS_MAP['AN_TYPE'] in {'CB_G', 'WB_G'}:
            process_money(SPIDER_PARAMS_MAP['AN_TYPE'], page_attr)

        # 公告数据入库
        if len(page_attr) != 0:
            parent_component_id = page_attr['parent_component_id']

            write_recode = self.write_ann_to_db(page_attr)
            if write_recode['an_id']:
                hm_resolver = self.http.request(r'resolver_query_by_id',
                                                {'id': parent_component_id}).json()['resolvers'][0]

                self.write_ResolveDataRel(an_id=write_recode['an_id'], version_no=page_attr['version_no'],
                                          priority=hm_resolver['priority'], response_id=response['id'])
            else:
                if write_recode['exception_type'] == 'resolver exception':
                    self.write_ResolverExceptionRecord(crawl_url=response['url'],
                                                       reason=str(write_recode['reason'].args))
                else:
                    self.write_SpiderExceptionRecord(crawl_url=response['url'],
                                                     exception_type='mysql connect exception',
                                                     reason=str(write_recode['reason'].args))

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
        for index, item in enumerate(SPIDER_PARAMS_MAP['ASSEMBLY_S']):
            path = item['path']  # 父解析器路径
            class_name = item['class_name']
            sub_component_list = item['subcomponents']  # 子解析器列表

            # 装载解析器
            read_hm_resolver = ClassReflection.remote_import(path, class_name)
            setattr(read_hm_resolver, 'sub_component_list', sub_component_list)
            setattr(read_hm_resolver, 'response_url', response_url)
            setattr(read_hm_resolver, 'response_text', response_text)
            setattr(read_hm_resolver, 'annoucement_type', SPIDER_PARAMS_MAP['AN_TYPE'])

            # 调用resolver_page()方法解析页面
            page_attr = getattr(read_hm_resolver, 'resolver_page')()

            if page_attr == {} or page_attr == None:
                page_attr = {SPIDER_PARAMS_MAP['AN_TYPE']: {}}

            class_path = re.sub('BaseSpider.base_component.', '', path, 1)
            page_attr['parent_component_id'] = item['resolve']['id']

            # 判断数据是否合格
            calibrate = self.process_judge(SPIDER_PARAMS_MAP['AN_TYPE'], page_attr[SPIDER_PARAMS_MAP['AN_TYPE']])

            # 解析失败后判断是否进入下个解析器
            if not calibrate:
                if index == length - 1:
                    self.write_ResolverExceptionRecord(crawl_url=response_url, reason='解析失败1')
                    return {}
                continue
            # 解析成功
            if len(page_attr) != 0 and calibrate:
                # 判断公告标题是否存在
                _title = page_attr[SPIDER_PARAMS_MAP['AN_TYPE']]['title']
                if _title == '' or _title is None:
                    self.write_ResolverExceptionRecord(crawl_url=response_url, reason='公告未获取标题')
                    return {}
                page_attr['an_type'] = SPIDER_PARAMS_MAP['AN_TYPE']
                page_attr['version_no'] = item['resolve']['version_no']
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
            an_id = self.http.request(r'add_an_to_db', {'item': x}).json()
            an_id = an_id['an_id']
            types = ['CB_G', 'WB_G', 'FB_G', 'MB_G', 'CB_E']
            for type in types:
                if type in item.keys():
                    self.http.request(r'parse', {'id': an_id, 'type': type})
                    break
            return {'an_id': an_id, 'error': None}
        except AttributeError as abe:
            logging.error('Database connection error：' + str(abe.args))
            return {'an_id': None, 'exception_type': 'spider exception', 'reason': abe}
        except Exception as e:
            logging.warning('Data into inventory is error：' + str(e.args))
            return {'an_id': None, 'exception_type': 'resolver exception', 'reason': e}

    # 爬虫爬取历史与response关联信息入库
    def write_ResolveDataRel(self, version_no=None, priority=None, response_id=None, an_id=None):
        rel = {'class_type': 'db.sm', 'class_name': 'ResloveDataRel',
               'dict': str({'id': self.http.request(r'uuid').json()['uuid'], 'spider_id': self.spider_id,
                            'response_id': response_id, 'version_no': version_no, 'priority': priority,
                            'type': SPIDER_PARAMS_MAP['AN_TYPE'], 'an_id': an_id})}
        self.http.request(r'add_dict_to_sm', rel)

    # 解析器错误记录
    def write_ResolverExceptionRecord(self, crawl_url, reason):
        id = self.http.request(r'uuid').json()['uuid']
        rel = {'class_type': 'db.sm', 'class_name': 'ResolverExceptionRecord',
               'dict': str({'id': id, 'spider_id': self.spider_id,
                            'redis_key': '', 'crawl_url': crawl_url,
                            'server_id': 'test sever one', 'server_name': 'test sever one',
                            'crawl_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'reason': reason})}
        self.http.request(r'add_dict_to_sm', rel)
        return id

    # 爬虫异常引发公告爬取错误
    def write_SpiderExceptionRecord(self, crawl_url, exception_type, reason):
        id = self.http.request(r'uuid').json()['uuid']
        rel = {'class_type': 'db.sm', 'class_name': 'SpiderExceptionRecord',
               'dict': str({'id': id, 'spider_id': self.spider_id,
                            'redis_key': '', 'crawl_url': crawl_url,
                            'server_id': 'test sever one', 'server_name': 'test sever one',
                            'crawl_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'exception_type': exception_type, 'reason': reason})}
        self.http.request(r'add_dict_to_sm', rel)
        return id

    # 通过父组件路径查询到子组件列表
    def get_sub_component_by_hm_resolver(self, parent_component_id):
        return self.http.request(r'sub_comp_query_by_parent',
                                 {'par_comp_id': parent_component_id}).json()['sub_components']  # 返回子组件列表


if __name__ == '__main__':
    begin_time = time.time()
    MultithreadingAnalysis(int(sys.argv[1]), '-1').run()
    end_time = time.time()
    print('use', (end_time - begin_time))
