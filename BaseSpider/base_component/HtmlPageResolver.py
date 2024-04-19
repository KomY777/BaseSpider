import importlib
from abc import ABC, abstractmethod
from scrapy import Selector


# 父组件解析器基类


class HtmlPageResolver(ABC):
    BASE_PATH = 'BaseSpider.base_component.'
    sub_component_list: list
    response_text: str
    response_url: str
    annoucement_type: str

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

    def get_subcomponent_data(self):
        page_attr = {}
        for index, item in enumerate(self.sub_component_list):
            self.sub_resolver = self.resolver_loader(self.BASE_PATH + item['class_path'])
            setattr(self.sub_resolver, 'page_attr', page_attr)
            setattr(self.sub_resolver, 'response_url', self.response_url)
            setattr(self.sub_resolver, 'response_text', Selector(text=self.response_text))
            setattr(self.sub_resolver, 'annoucement_type', self.annoucement_type)
            # todo 判断达标率 用不用进入下一个子解析器
            page_attr = getattr(self.sub_resolver, 'resolver_page')()
        return page_attr

    # 解析页面
    # 延迟到子类实现
    @abstractmethod
    def resolver_page(self) -> dict:
        pass
