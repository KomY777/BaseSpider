import scrapy
from BaseSpider.base_component.entity.PageAttribute import PageAttribute
from enum import IntEnum
from scrapy import Request
from scrapy.http import Response

from BaseSpider.resolve.resolve_announcement import MultithreadingAnalysis


class CrawlMode(IntEnum):
    # 增量
    INCREMENT = 1
    # 范围
    RANGE = 2


class AnnouncementSpider(scrapy.Spider):
    name = 'announcement_spider'

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.task_id = kwargs.get('task_id')
        self.spider_id = kwargs.get('spider_id')
        self.range_start_time = kwargs.get('range_start_time')
        self.range_end_time = kwargs.get('range_end_time')
        self.mode = kwargs.get('mode')
        self.spider_info = get_spider_info(self.spider_id)

        self.page_resolver = None
        self.request_page_resolver = None
        self.request_detail_resolver = None

        self.start_page = 1
        self.end_page = 0
        self.cur_page = 1

        self.crawl_num = 0
        self.resolve_num = 0

        self.detail_url_list = []

    def start_requests(self):
        try:
            init_request = self.generate_page_request(self.cur_page)
            if self.mode == CrawlMode.INCREMENT:
                init_request.callback = self.crawl_page
            elif self.mode == CrawlMode.RANGE:
                init_request.callback = self.binary_search
            else:
                self.logger.error(f"mode error: {self.mode}")
                return

        except Exception as e:
            self.logger.error(f"parse error: {e}")
            return

    def binary_search(self, response: Response):
        try:
            page_attr = self.resolve_page(response)

            if self.end_page == 0:
                self.end_page = page_attr.largest_page

            if page_attr.newest_time >= self.range_start_time > page_attr.oldest_time:
                self.crawl_page(response)
            elif page_attr.newest_time < self.range_start_time:
                self.end_page = page_attr.cur_page
            else:
                self.start_page = page_attr.cur_page

            if self.start_page == self.end_page:
                self.logger.info(f"page not found: {self.range_start_time}")
                return

            self.cur_page = (self.start_page + self.end_page) // 2
            self.binary_search()
        except Exception as e:
            self.logger.error(f"binary_search error: {e}")
            return

    def crawl_page(self, response: Response):
        try:
            page_attr = self.resolve_page(response)
            if self.range_end_time > page_attr.newest_time:
                self.logger.info(f"crawl end: {self.range_end_time}")
                self.crawl_detail()
                return

            self.detail_url_list.extend(page_attr.urls)
            self.cur_page += 1
            request = self.generate_page_request(self.cur_page)
            request.callback = self.crawl_page
            yield request
        except Exception as e:
            self.logger.error(f"crawl_page error: {e}")
            return

    def crawl_detail(self):
        try:
            for url in self.detail_url_list:
                request = self.generate_detail_request(url)
                request.callback = self.after_crawl_detail
                yield request
        except Exception as e:
            self.logger.error(f"crawl_detail error: {e}")
            return

    def after_crawl_detail(self, response: Response):
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
            return getattr(self.page_resolver, 'resolver_page')()
        except Exception as e:
            self.logger.error(f"resolve_page error: {e}")

    def generate_page_request(self, page) -> Request:
        try:
            setattr(self.request_page_resolver, 'page', page)
            return getattr(self.request_page_resolver, 'create_request')()
        except Exception as e:
            self.logger.error(f"generate_page_request error: {e}")

    def generate_detail_request(self, url) -> Request:
        try:
            setattr(self.request_detail_resolver, 'url', url)
            return getattr(self.request_detail_resolver, 'create_request')()
        except Exception as e:
            self.logger.error(f"generate_detail_request error: {e}")
