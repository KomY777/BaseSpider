# import json
# from collections import Iterable
# from enum import Enum
# from random import random
# from re import sub, search
#
# import redis
# import logging
#
# from scrapy_redis.spiders import RedisSpider
# from scrapy_redis.utils import bytes_to_str
# from BaseSpider.base_component.RequestResolver import RequestResolver
# from BaseSpider.base_component.entity.PageAttribute import PageAttribute
# from BaseSpider.base_component.entity.ReqParam import ReqParam
# from BaseSpider.resolve.resolve_announcement import MultithreadingAnalysis
# from BaseSpider.spiders import spider_db_datas
# from BaseSpider.tool import ClassReflection
# import traceback
#
# rd = redis.Redis('127.0.0.1', port=6379, db=0, password='Abc785342')
#
#
# def param_to_redis(spider_id, url, body, callback, method, base_key):
#     req_param = {}
#
#     req_param['url'] = url
#     req_param['body'] = body
#     req_param['call_back'] = callback
#     req_param['method'] = method
#
#     if spider_id in ['1104', '1105']:
#         fix_body = sub(r'<random>', str(random()), req_param['body'])
#         req_param['body'] = fix_body
#
#     try:
#         back = rd.lpush(
#             base_key + ":LIST",
#             json.dumps(
#                 req_param
#             )
#         )
#
#         return {'status': True, 'redis-back': back}
#     except Exception as ex:
#         return {'status': False, 'error': ex.args}
#
#
# ONCE_CRAWL = 100
#
#
# class BaseSpider(RedisSpider):
#     rd = rd
#     name = "BASE_SPIDER"
#     redis_key = "REDIS_KEY"
#
#     class CallBack(Enum):
#         BINARY_SEARCH = 'binary_search'
#         CHOOSE_PAGE = 'choose_page'
#         GET_URLS = 'get_urls_of_announce'
#         GET_ANN = 'get_announce_data'
#
#     def __init__(self, **kwargs):
#         """
#         :param id:
#         :param kwargs:
#         """
#         self.spider_id = kwargs.get('spider_id')
#         self.task_id = kwargs.get('id')
#
#         self.spider_info = spider_db_datas.get_all_spider_info(self.spider_id)
#         param_to_redis(self.spider_id, self.spider_info.url, self.spider_info.body, self.spider_info.call_back,
#                        self.spider_info.method,
#         self.spider_info.redis_key)
#         # self.spider_info = spider_db_datas.get_spider_info(self.spider_id)
#         self.spider_info.start_time = kwargs.get('range_start_time')
#         self.spider_info.earliest_time = kwargs.get('range_start_time')
#         self.spider_info.end_time = kwargs.get('range_end_time')
#         self.spider_info.mode = kwargs.get('mode')
#         self.always_new = False
#         # self.spider_info.body = fixedBody(self.spider_info.body)
#         if search('ZGZF', self.spider_info.name):
#             self.always_new = True
#         self.aim_num = 0
#         self.ann_number = 0
#         # redis_key
#         self.base_redis_key = self.spider_info.redis_key
#         self.redis_list_key = self.base_redis_key + ':LIST'
#         self.redis_page_key = self.base_redis_key + ':HM'
#         self.redis_key = self.redis_list_key
#         self.idle_count = 0
#         self.idle_number = 25
#         self.idle_list = []
#
#         super().__init__(**kwargs)
#         self.data_attr = {}  # 爬虫状态数据集
#         self.list_status = None
#         # 加载解析器
#         self.req_url_resolver = ClassReflection.remote_import(self.spider_info.resolvers['REQ_URL'][0],
#                                                               self.spider_info.resolvers['REQ_URL'][1])
#         self.read_ul_resolver = ClassReflection.remote_import(self.spider_info.resolvers['READ_UL'][0],
#                                                               self.spider_info.resolvers['READ_UL'][1])  # 列表请求
#         self.req_next_page_resolver = ClassReflection.remote_import(
#             self.spider_info.resolvers['REQ_NEXT_PAGE'][0], self.spider_info.resolvers['REQ_NEXT_PAGE'][1])  # 换页请求
#
#         # self.req_url_resolver = ClassReflection.instantiation_by_path(self.spider_info.resolvers['REQ_URL'][0])
#         # self.read_ul_resolver = ClassReflection.instantiation_by_path(self.spider_info.resolvers['READ_UL'][0])  # 列表请求
#         # self.req_next_page_resolver = ClassReflection.instantiation_by_path(
#         #     self.spider_info.resolvers['REQ_NEXT_PAGE'][0])  # 换页请求
#         self.once_crawl_to_resolve = ONCE_CRAWL
#
#     """ ''''''''''''''''''''''''''''''''''''''''''''' 改写爬虫运行流程 ''''''''''''''''''''''''''''''''''''''''''''' """
#
#     def start_requests(self):
#         """
#         请求开始
#         :return:
#         """
#         # 爬虫启动参数
#         self.crawler.settings.attributes['DOWNLOAD_DELAY'].value = self.spider_info.list_download_speed
#         return self.next_requests()
#
#     def make_request_from_data(self, data):
#         """
#         继承自源文件scrapy_redis.spiders：根据回调参数生成请求
#         :param data:
#         :return:
#         """
#         m_dict = dict(**json.loads(bytes_to_str(data, self.redis_encoding)))
#         for m_key in m_dict.keys():
#             if isinstance(m_dict[m_key], list):
#                 m_dict[m_key] = list(m_dict[m_key])[0]
#
#         self.data_attr = m_dict
#         if self.CallBack.GET_ANN.value == m_dict.get('call_back'):
#             request = self.set_request(self.req_url_resolver, m_dict)
#         else:
#             request = self.set_request(self.req_next_page_resolver, m_dict)
#         return request
#
#     def set_request(self, resolve_obj, m_dict):
#         """
#         生成请求并设置回调
#         :param m_dict: 放于redis内的请求信息
#         :return 请求信息
#         """
#         setattr(resolve_obj, 'req_param', m_dict)
#         request = getattr(resolve_obj, 'create_request')()
#         m_call_back = getattr(resolve_obj, 'call_back')
#         request.callback = getattr(self, m_call_back)
#         request.errback = self.next_page_err
#         return request
#
#     """ '''''''''''''''''''''''''''''''''''''''''''''' 以下为回调方法 '''''''''''''''''''''''''''''''''''''''''''''' """
#
#     def next_page_err(self, failure):
#         """
#          错误回调: 翻页请求失败
#         :param failure:
#         :return:
#         """
#         self.crawler.engine.close_spider(self, {'istrue_end': 'false', 'url': failure.request.url, 'status': 0,
#                                                 'result': '翻页请求失败'})
#
#     def parse(self, response):
#         """
#         爬虫初始回调
#         :param response:
#         :return:
#         """
#         try:
#             spider_attr = self.check_parse_result(self.resolve_urls(response))  # 验证采集结果
#
#             self.data_attr['earliest_time'] = self.spider_info.earliest_time if self.spider_info.earliest_time else ''
#
#             if self.spider_info.mode == 1:  # 创建新任务
#                 self.spider_info.history_id = None
#                 if spider_attr.urls[0] == self.spider_info.latest_url \
#                         or (self.spider_info.latest_time and spider_attr.newest_time < self.spider_info.latest_time):
#                     # 网站未更新数据
#                     self.crawler.engine.close_spider(self,
#                                                      {'istrue_end': 'true', 'status': 1, 'result': '网站未更新数据'})
#                     return
#                 self.spider_info.latest_time = spider_attr.newest_time
#                 self.spider_info.latest_url = spider_attr.urls[0]
#                 if not self.always_new:
#                     spider_db_datas.set_spider_status(self.spider_id, 2)
#                     self.spider_info.status = 2  # fixme 修改爬虫状态
#                 self.choose_page(response)  # 任务回调 page:1
#             else:
#                 self.data_attr['binary_start_page'] = 1
#                 self.data_attr['binary_end_page'] = spider_attr.largest_page
#                 self.data_attr['aim_time'] = self.spider_info.end_time
#                 self.assign_page_back(redis_key=self.redis_list_key, call_back=self.CallBack.BINARY_SEARCH.value,
#                                       url=response.url, page=spider_attr.largest_page // 2)  # 二分法查找开始页
#         except Exception as e:
#             traceback.print_exc()
#             self.crawler.engine.close_spider(self, {'istrue_end': 'true', 'status': 1, 'result': '解析错误'})
#
#     def binary_search(self, response):
#         """
#         二分法查找指定时间所在公告的页号
#         根据查询结果设置本地爬取的页码
#         :param response:
#         :return:
#         """
#         aim_time = self.data_attr['aim_time'] if self.data_attr['aim_time'] else self.spider_info.latest_time
#         start_page = self.data_attr['binary_start_page']
#         end_page = self.data_attr['binary_end_page']
#
#         try:
#             spider_attr = self.check_parse_result(self.resolve_urls(response))
#
#             if spider_attr.newest_time >= aim_time > spider_attr.oldest_time:  # 位于本页内
#                 return self.choose_page(response)  # 从当前页开始执行爬取
#             elif spider_attr.newest_time < aim_time:  # 当前页最大的时间依旧小于目标时间
#                 end_page = spider_attr.cur_page
#                 if start_page == end_page:  # 翻页错误、目标时间错误，公告最新时间落后于目标时间
#                     self.crawler.engine.close_spider(self, {'istrue_end': 'false', 'status': 0,
#                                                             'result': '翻页错误、目标时间错误，公告最新时间落后于目标时间'})
#                     return
#             else:
#                 if start_page != spider_attr.cur_page:
#                     start_page = spider_attr.cur_page
#                 else:  # 二分结束
#                     return self.assign_page_back(redis_key=self.redis_list_key,
#                                                  call_back=self.CallBack.CHOOSE_PAGE.value,
#                                                  url=response.url, page=spider_attr.cur_page + 1)
#
#             # 回调本身，对mid_page继续二分检查
#             self.data_attr['binary_start_page'] = start_page
#             self.data_attr['binary_end_page'] = end_page
#             self.assign_page_back(redis_key=self.redis_list_key, call_back=self.CallBack.BINARY_SEARCH.value,
#                                   url=response.url, page=(start_page + end_page) // 2)
#         except Exception as e:
#             traceback.print_exc()
#             if self.ann_number and self.ann_number > 0:
#                 self.redis_key = self.redis_page_key
#             else:
#                 self.crawler.engine.close_spider(self, {'istrue_end': 'true', 'status': 1, 'result': '解析错误'})
#
#     # 获取公告详情
#     def choose_page(self, response):
#         try:
#             spider_attr = self.check_parse_result(self.resolve_urls(response))  # 验证采集结果
#             #  发送url到redis
#             for m_url in spider_attr.urls:
#                 self.assign_page_back(redis_key=self.redis_page_key, url=m_url, call_back=self.CallBack.GET_ANN.value,
#                                       is_next_page=False)
#                 self.data_attr['ann_number'] = self.data_attr.get('ann_number', 0) + 1
#             self.ann_number = self.data_attr['ann_number']
#             self.aim_num = self.data_attr['ann_number']
#             # 修改参数
#             self.data_attr['crawl_page'] = self.data_attr.get('crawl_page', 0) + 1
#             if spider_attr.cur_page >= spider_attr.largest_page or spider_attr.oldest_time < self.data_attr.get(
#                     'earliest_time', ''):
#                 # 本次任务结束
#                 self.spider_info.earliest_time = self.spider_info.latest_time
#                 self.spider_info.cur_time = None
#                 self.spider_info.status = 1
#                 self.change_spider_status(list_status={'istrue_end': 'true', 'status': 1, 'result': '本次任务结束'})
#             elif self.data_attr['crawl_page'] > self.spider_info.section_page_size:
#                 # 本段结束
#                 self.spider_info.cur_time = spider_attr.oldest_time
#                 self.spider_info.status = 2
#                 self.change_spider_status()
#             else:
#                 # 请求下一页
#                 self.assign_page_back(redis_key=self.redis_list_key, call_back=self.CallBack.CHOOSE_PAGE.value,
#                                       url=response.url, page=spider_attr.cur_page + 1)
#         except Exception as e:
#             traceback.print_exc()
#             if self.ann_number and self.ann_number > 0:
#                 self.redis_key = self.redis_page_key
#             else:
#                 self.crawler.engine.close_spider(self, {'istrue_end': 'true', 'status': 1, 'result': '解析错误'})
#
#     def get_urls_of_announce(self, response):
#         """
#         回调函数：进行公告url列表获取,第一段爬取的回调
#         :param response:
#         :return:
#         """
#         # 调用页面解析器进行数据采集
#         spider_attr = self.check_parse_result(self.resolve_urls(response))
#         if spider_attr.oldest_time < self.spider_info.earliest_time:
#             # todo 任务完成爬取结束
#             pass
#         else:
#             # todo 产生新请求
#             pass
#
#     def get_announce_data(self, response):
#         """
#         获取公告response数据, crawl_html表入库
#         :param response:
#         """
#         # 创建response数据
#         crawl_html = {'id': spider_db_datas.get_uuid(), 'spider_id': self.spider_id, 'url': response.url,
#                       'content': response.text, 'type': self.spider_info.an_type,
#                       'section': 0}
#
#         message = spider_db_datas.write_response_to_db(crawl_html)  # 调用方法使response数据入库
#         if message['code'] != '200':
#             logging.info(message)
#             # todo 入库失败
#         self.ann_number -= 1
#         if self.ann_number <= 0:
#             self.crawl_ann_close()
#
#     @staticmethod
#     def close(spider, reason):
#         rd.delete(spider.redis_list_key)  # 清空换页redis
#
#
#     """ ''''''''''''''''''''''''''''''''''''''''''' 回调处理方法/工具方法 ''''''''''''''''''''''''''''''''''''''''''' """
#
#     def resolve_urls(self, response) -> PageAttribute:
#         """
#         解析页面：URL列表解析器解析页面获得数据
#         :param response: 当前列表页面的信息
#         :return: 某页面的全部公告url,以及当前页数、网页最大页数、页大小、当页最新url
#         """
#         try:
#             setattr(self.read_ul_resolver, 'response', response)
#             return getattr(self.read_ul_resolver, 'resolver_page')()
#         except Exception as e:
#             if self.ann_number and self.ann_number > 0:
#                 self.redis_key = self.redis_page_key
#             else:
#                 self.crawler.engine.close_spider(self, {'istrue_end': 'false', 'status': 0, 'result': '换页解析报错'})
#
#     @staticmethod
#     def check_parse_result(spider_attr):
#         """
#         验证首页数据爬取是否成功且规范
#         :param spider_attr:
#         :return:
#         """
#         if not isinstance(spider_attr.cur_latest_url, str) \
#                 or spider_attr.cur_latest_url is None or spider_attr.cur_latest_url == '':
#             raise Exception('Failed to get the latest URL on the homepage')
#         elif not isinstance(spider_attr.largest_page, int):
#             try:
#                 spider_attr.largest_page = int(spider_attr.largest_page)
#             except:
#                 raise Exception('The maximum page is not obtained or the maximum page type is not：int')
#         elif not isinstance(spider_attr.page_size, int):
#             try:
#                 spider_attr.page_size = int(spider_attr.page_size)
#             except:
#                 raise Exception('Page size not obtained or page size or type is not：int')
#         else:
#             return spider_attr
#
#     def assign_page_back(self, redis_key, url, call_back, page=None, is_next_page=True):
#         """
#         将指定页码(page)的页面信息存入redis并调用不同的回调(call_back)
#         :param is_next_page: 是否为换页请求
#         :param url:
#         :param call_back: 调用的回调函数
#         :param page: 指定页码
#         :return:
#         """
#         if is_next_page:
#             url_attr = self.generate_redis_param(self.req_next_page_resolver, url, call_back, page,
#                                                  params=self.spider_info.param, data_attr=self.data_attr)
#         else:
#             self.data_attr['body'] = {}
#             url_attr = self.generate_redis_param(self.req_url_resolver, url, call_back, page,
#                                                  params=self.spider_info.param, data_attr=self.data_attr)
#         self.send_attr_to_redis(redis_key, url_attr)
#
#     @staticmethod
#     def generate_redis_param(resolver: RequestResolver, m_url, m_call_back, page_num, params=None,
#                              data_attr=None):
#         """
#         设置向redis传入的参数
#         :param params: 解析器运行参数
#         :param resolver: which resolver generate
#         :param m_url: 传入的url
#         :param m_call_back: 传入回调函数
#         :param page_num: 传入当前网址页号
#         :param data_attr: redis 附加参数
#         :return:
#         """
#         if params is None:
#             params = {}
#         ClassReflection.dictionary_assignment(resolver, params)
#
#         req_p = ReqParam(page_num, m_url, m_call_back)
#         setattr(resolver, 'req_attr', req_p)
#         url_attr = getattr(resolver, 'general_param', req_p)()
#         data_attr.update(url_attr)
#         return data_attr
#
#     @staticmethod
#     def send_attr_to_redis(redis_key, m_dict: dict):
#         """
#         向redis发送的请求参数
#         :param m_dict: 放于redis内的请求信息
#         """
#         for m_key in m_dict.keys():
#             if isinstance(m_dict[m_key], Iterable) and not isinstance(m_dict[m_key], str):
#                 m_dict[m_key] = ''.join(m_dict[m_key])
#         data = json.dumps(m_dict)
#         rd.lpush(redis_key, data)
#
#     def change_spider_status(self, list_status=None):
#         """
#         urls获取完成修改爬虫信息
#         :param list_status:
#         :return:
#         """
#         self.list_status = list_status
#         self.redis_key = self.redis_page_key
#         self.crawler.settings.attributes['DOWNLOAD_DELAY'].value = self.spider_info.page_download_speed
#
#
#     def crawl_ann_close(self):
#         """
#         公告爬取结束处理
#         :return:
#         """
#         try:
#             resolver = MultithreadingAnalysis(int(self.spider_id), '0')
#             resolver.run()
#             self.crawler.engine.close_spider(self, {'istrue_end': 'true', 'status': 2, 'result': '本段结束'})
#         except Exception as e:
#             self.crawler.engine.close_spider(self, {'istrue_end': 'false', 'status': 1, 'result': f'解析器异常{e}'})
#
