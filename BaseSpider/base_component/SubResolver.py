from abc import ABC, abstractmethod


# 子组件解析器基类
from scrapy import Selector


class SubResolver(ABC):
    response_text: Selector
    response_url: str
    annoucement_type: str
    page_attr: dict


    # 解析页面
    # 延迟到子类实现
    @abstractmethod
    def resolver_page(self) -> dict:
        pass
