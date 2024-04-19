from abc import ABC, abstractmethod

from scrapy.http import Response

from ..base_component.entity.PageAttribute import PageAttribute


# 列表页面解析器基类
class PageResolver(ABC):
    response: Response

    x_base_url: str  # 当前网址公告URL前缀
    x_largest_page: str  # 当前最大页
    x_cur_latest_page: str  # 当前页最新URL
    x_link_hrefs: str  # 当前页URL列表
    x_aim_crawl_page: str  # 当前页页码

    # 解析页面
    # 延迟到子类实现
    @abstractmethod
    def resolver_page(self) -> PageAttribute:
        pass

