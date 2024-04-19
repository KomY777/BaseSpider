# -*- coding: UTF-8 -*-
import json,sys
from random import random

import redis
from re import sub
from datetime import datetime

from BaseSpider.settings import http

rd = redis.Redis('127.0.0.1', port=6379, db=0, password='Abc785342')

id = sys.argv[1]
spider_message = http.request(r'spider_init_query', {'spider_id': id}).json() # 从spider_initialize表读取加载信息

req_param = {}
url = spider_message['url']
body = spider_message['body']
callback = spider_message['callback']
method = spider_message['method']


req_param['url'] = url
req_param['body'] = body
req_param['call_back'] = callback
req_param['method'] = method
base_key = sys.argv[2]

# GGZY_END_TIME = datetime.now().strftime('%Y-%m-%d')
# if id in ['1001', '1002', '1003', '1004']:
#     fix_body = sub(r'(?<=TIMEEND=)\d{4}-\d{2}-\d{2}(?=&)', GGZY_END_TIME, req_param['body'])
#     fix_body = sub(r'(?<=TIMEEND_SHOW=)\d{4}-\d{2}-\d{2}(?=&)', GGZY_END_TIME, fix_body)
#     req_param['body'] = fix_body

if id in ['1104', '1105']:
    fix_body = sub(r'<random>', str(random()), req_param['body'])
    req_param['body'] = fix_body

print(req_param)


rd.lpush(
    base_key+':LIST',
    json.dumps(
        req_param
    )
)
