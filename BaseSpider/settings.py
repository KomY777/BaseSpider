# -*- coding: utf-8 -*-
import random
from BaseSpider.tool.RequestTool import HttpSession

import warnings

# 忽略来自scrapy.selector.unified模块的UserWarning
warnings.filterwarnings('ignore', category=UserWarning, module='scrapy.selector.unified')

BOT_NAME = 'BaseSpider'

SPIDER_MODULES = ['BaseSpider.spiders']
NEWSPIDER_MODULE = 'BaseSpider.spiders'

ROBOTSTXT_OBEY = False
DOWNLOAD_TIMEOUT = 120
DOWNLOAD_DELAY = 1  # 时间间隔

addcycleurl = "http://127.0.0.1:8100/scheduler/add?spider_id="
removecycleurl = "http://127.0.0.1:8100/scheduler/remove?spider_id="

REDIS_URL = 'redis://root:Abc785342@127.0.0.1:6379 '

REDIS_CONFIG = {
    'HOST': "127.0.0.1",
    'PORT': 6379,
    'USERNAME': 'root',
    'PASSWORD': 'Abc785342'
}

#
USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20"
]

USER_AGENT = random.choice(USER_AGENTS)

http = HttpSession()
DOWNLOADER_MIDDLEWARES = {
    'BaseSpider.middlewares.BasespiderDownloaderMiddleware': 100
}
REDIRECT_ENABLED = False

PROXIES = ["http://127.0.0.1:5010", None]

RETRY_ENABLED = False

SCHEDULE_ADMIN_SERVER_URL = 'http://localhost:2024/api'
ANNOUNCEMENT_DB_SERVER_URL = 'http://localhost:8000/databaseOperate'
