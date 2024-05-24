import importlib
from abc import ABC, abstractmethod
from scrapy import Selector


# 父组件解析器基类


class HtmlPageResolver(ABC):
    BASE_PATH = 'BaseSpider.base_component.'
    sub_component_list: list
    response_text = None
    response_url: str
    annoucement_type: str
    page_attr = {}

    @staticmethod
    def resolver_loader(classpath):
        # 将全路径类名切割获得类名及类路径
        ret, cls_name = classpath.rsplit(".", maxsplit=1)
        # 导入文件模块
        m = importlib.import_module(ret)
        # 通过getattr()获取模块内容，获取类名
        m_class = getattr(m, cls_name)
        obj = m_class()
        return obj

    # 解析页面
    # 延迟到子类实现
    @abstractmethod
    def resolver_page(self) -> dict:
        pass
