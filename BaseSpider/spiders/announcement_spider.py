import scrapy
from BaseSpider.base_component.entity.PageAttribute import PageAttribute
from BaseSpider.base_component.entity.ReqParam import ReqParam
from enum import IntEnum
from scrapy import Request
from scrapy.http import Response
from BaseSpider.api.admin import get_spider_info
from BaseSpider.tool import ClassReflection
import datetime

from BaseSpider.resolve.resolve_announcement import MultithreadingAnalysis


class CrawlMode(IntEnum):
    # 增量
    INCREMENT = 1
    # 范围
    RANGE = 2


DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class AnnouncementSpider(scrapy.Spider):
    name = 'AnnouncementSpider'

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.task_id = kwargs.get('task_id')
        self.spider_id = kwargs.get('spider_id')
        self.range_start_time = datetime.datetime.fromtimestamp(int(kwargs.get('range_start_time')))
        self.range_end_time = datetime.datetime.fromtimestamp(int(kwargs.get('range_end_time')))
        self.mode = int(kwargs.get('mode'))
        self.args = kwargs.get('args')
        self.spider_info = get_spider_info(self.spider_id)

        self.request_detail_resolver = ClassReflection.remote_import(self.spider_info.resolvers['REQ_URL'][0],
                                                                     self.spider_info.resolvers['REQ_URL'][1])
        self.request_page_resolver = ClassReflection.remote_import(
            self.spider_info.resolvers['REQ_NEXT_PAGE'][0], self.spider_info.resolvers['REQ_NEXT_PAGE'][1])
        self.page_resolver = ClassReflection.remote_import(self.spider_info.resolvers['READ_UL'][0],
                                                           self.spider_info.resolvers['READ_UL'][1])

        self.start_page = 1
        self.end_page = 0
        self.cur_page = 1

        self.crawl_num = 0
        self.resolve_num = 0

        self.detail_url_list = []

    def start_requests(self):
        try:
            self.crawler.settings.attributes['DOWNLOAD_DELAY'].value = 1
            call_back = None
            if self.mode == CrawlMode.INCREMENT:
                call_back = self.crawl_page
            elif self.mode == CrawlMode.RANGE:
                call_back = self.binary_search
            else:
                self.logger.error(f"mode error: {self.mode}")
                return
            init_request = self.generate_page_request(self.cur_page, call_back)
            yield init_request

        except Exception as e:
            self.logger.error(f"parse error: {e}")
            return

    def binary_search(self, response: Response):
        try:
            page_attr = self.resolve_page(response)
            self.logger.info(f'binary searching: ' +
                             f'start_page: {self.start_page},\n' +
                             f'end_page: {self.end_page},\n' +
                             f'cur_page: {self.cur_page},\n' +
                             f'cur_page_newest_time: {page_attr.newest_time}\n' +
                             f'cur_page_oldest_time: {page_attr.oldest_time}'
                             )

            if self.end_page == 0:
                self.end_page = page_attr.largest_page

            # 抓取顺序(由新到旧)： range_end_time ～ range_start_time
            # range_end_time 处于当前页
            if page_attr.newest_time >= self.range_end_time > page_attr.oldest_time:
                # yield self.generate_page_request(self.start_page, self.crawl_page)
                # return
                yield from self.crawl_page(response)
                return
            # 当前页最新时间晚于 range_end_time
            elif page_attr.newest_time < self.range_end_time:
                self.end_page = page_attr.cur_page
            else:
                self.start_page = page_attr.cur_page

            if self.start_page == self.end_page:
                self.logger.info(f"page not found: {self.range_start_time}")
                return

            self.cur_page = (self.start_page + self.end_page) // 2
            yield self.generate_page_request(self.cur_page, self.binary_search)
        except Exception as e:
            self.logger.error(f"binary_search error: {e}")
            return

    def crawl_page(self, response: Response):
        try:
            self.logger.info(f"crawl_page: {self.cur_page}")
            page_attr = self.resolve_page(response)
            if self.range_start_time > page_attr.newest_time:
                self.logger.info(f"crawl end: {self.range_end_time}")
                yield from self.crawl_detail()
                return

            self.detail_url_list.extend(page_attr.urls)
            self.cur_page += 1
            yield self.generate_page_request(self.cur_page, self.crawl_page)
        except Exception as e:
            self.logger.error(f"crawl_page error: {e}")
            return

    def crawl_detail(self):
        try:
            for url in self.detail_url_list:
                yield self.generate_detail_request(url, self.after_crawl_detail)
        except Exception as e:
            self.logger.error(f"crawl_detail error: {e}")
            return

    def after_crawl_detail(self, response: Response):
        self.logger.info(response.url)
        if response.status == 200:
            self.resolve_num += 1

    def start_resolve(self):
        resolver = MultithreadingAnalysis(int(self.spider_id), '0')
        resolver.run()
        self.resolve_num = resolver.already_resolved_num

    def close(spider, reason):
        # todo: 记录结果，变更状态
        pass

    # 解析列表页面信息
    def resolve_page(self, response) -> PageAttribute:
        try:
            setattr(self.page_resolver, 'response', response)
            page_attr: PageAttribute = getattr(self.page_resolver, 'resolver_page')()
            page_attr.newest_time = datetime.datetime.strptime(page_attr.newest_time, DATE_TIME_FORMAT)
            page_attr.oldest_time = datetime.datetime.strptime(page_attr.oldest_time, DATE_TIME_FORMAT)
            return page_attr
        except Exception as e:
            self.logger.error(f"resolve_page error: {e}")

    def generate_page_request(self, page, callback) -> Request:
        try:
            param = ReqParam(page_num=page)
            setattr(self.request_page_resolver, 'req_attr', param)
            request_param = getattr(self.request_page_resolver, 'general_param')()
            setattr(self.request_page_resolver, 'req_param', request_param)
            request = getattr(self.request_page_resolver, 'create_request')()
            request.callback = callback
            return request
        except Exception as e:
            self.logger.error(f"generate_page_request error: {e}")

    def generate_detail_request(self, url, callback) -> Request:
        try:
            param = ReqParam(m_url=url)
            setattr(self.request_detail_resolver, 'req_attr', param)
            request_param = getattr(self.request_detail_resolver, 'general_param')()
            setattr(self.request_detail_resolver, 'req_param', request_param)
            request = getattr(self.request_detail_resolver, 'create_request')()
            request.callback = callback
            return request
        except Exception as e:
            self.logger.error(f"generate_detail_request error: {e}")
