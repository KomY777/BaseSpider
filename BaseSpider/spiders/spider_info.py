class SpiderInfo:
    id: str  # id
    name: str  # 名字
    status: int  # 状态
    an_type: str  # 公告类型

    url: str  # url
    body: str  # 请求体
    call_back: str  # 回调
    method: str  # 请求方法
    param: str  # 运行参数

    mode: int #爬取模式(0 按照当前时间段爬取，1 忽略爬取时间爬取最新的)

    list_download_speed = 1  # list下载速度
    page_download_speed = 1  # 页面下载速度

    resolvers: list

    start_time: str
