class SpiderInfo:
    id: str  # id
    name: str  # 名字
    redis_key: str  # redis_key
    status: int  # 状态
    an_type: str  # 公告类型

    url: str  # url
    body: str  # 请求体
    call_back: str  # 回调
    method: str  # 请求方法
    param: str  # 运行参数

    section_page_size: int  # 段页数/段长
    mode: int #爬取模式(0 按照当前时间段爬取，1 忽略爬取时间爬取最新的)

    latest_url: str
    latest_time: str  # 数据库最新时间 （数据库任务的开始时间）
    cur_time: str  # 当前爬取到的时间（下段爬取的开始时间）
    earliest_time: str  # 已爬取的最早时间（用于作为本次任务截至时间）

    list_download_speed = 1  # list下载速度
    page_download_speed = 1  # 页面下载速度

    resolvers: list

    start_time: str
