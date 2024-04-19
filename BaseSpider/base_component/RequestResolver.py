from abc import abstractmethod, ABC

from ..base_component.entity import ReqParam

redis_key: str


# 该类为爬虫首页请求解析器基类
# 定义出第一次访问数据的所有参数
class RequestResolver(ABC):

    url: str
    body: dict
    method: str
    call_back: str
    dont_filter: bool
    meta: dict
    page_num: int

    redis_key: str

    # 传入redis所用：
    # 传入redis的依赖参数
    req_attr: ReqParam

    # 生成请求所用：
    # 从redis传入参数
    req_param = {}

    # 解析第一次请求方法
    # 延迟到子类实现
    @abstractmethod
    def create_request(self):
        self.configuration_parameter()

    # 生成参数
    # 延迟到子类实现
    @abstractmethod
    def general_param(self):
        self.url = self.req_attr.m_url
        self.page_num =self.req_attr.page_num
        self.call_back = self.req_attr.call_back

    # 进行类配置
    def configuration_parameter(self):
        # 请求规范检测
        self.detection_parameters()
        if self.req_param is None:
            raise Exception('该请求未定义任何参数')
        # 解析器赋值
        self.url = self.req_param.get('url')
        self.method = self.req_param.get('method')
        self.call_back = self.req_param.get('call_back')
        self.body = self.req_param.get('body')
        self.dont_filter = self.req_param.get('dont_filter')
        self.meta = self.req_param.get('meta')

    # 请求参数初始化
    # 默认为 GET 方法
    def detection_parameters(self):
        if not self.req_param.keys().__contains__('url'):
            raise Exception('该参数列表中必须添加url')
        if not self.req_param.keys().__contains__('method'):
            self.req_param['method'] = 'GET'
        if not self.req_param.keys().__contains__('call_back'):
            raise Exception('该参数列表中必须添加回调函数')
        if not self.req_param.keys().__contains__('body'):
            self.req_param['body'] = {}
        if not self.req_param.keys().__contains__('dont_filter'):
            self.req_param['dont_filter'] = True
        if not self.req_param.keys().__contains__('meta'):
            self.req_param['meta'] = {}
