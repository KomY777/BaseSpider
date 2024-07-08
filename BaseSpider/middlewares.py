# -*- coding: utf-8 -*-
import datetime
import json
# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import random
import re
import time
from collections import defaultdict

import copy

import requests
import scrapy
from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse, Response

from BaseSpider import settings
from BaseSpider.settings import USER_AGENT, USER_AGENTS


class BasespiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class BasespiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self):
        self.errorcount = 0
        self.retry_http_codes = [302, 403, 400, 405, 404, 504, 503]
        # 预先保留在settings中的代理IP列表
        self.proxies = settings.PROXIES
        self.proxy = None

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        if "website" in request.meta:
            if request.meta["website"] == 'cqggzy':
                request.headers = {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Connection': 'keep-alive',
                    'Content-Length': '634',
                    'Content-Type': 'application/json; charset=UTF-8',
                    'Cookie': '__jsluid_s=f99184e462faaff73e9e2cfda7245477; cookie_www=36802747; '
                              'Hm_lvt_3b83938a8721dadef0b185225769572a=1683686568,1684137937; '
                              'Hm_lpvt_3b83938a8721dadef0b185225769572a=1684150785',
                    'Host': 'www.cqggzy.com',
                    'Origin': 'https://www.cqggzy.com',
                    'Referer': 'https://www.cqggzy.com/jyjg/transaction_detail.html',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/113.0.0.0 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest',
                    'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': "Windows"
                }
                if len(request.body) == 0:
                    now_time = datetime.datetime.now() - datetime.timedelta(days=90)
                    start_time = now_time.strftime("%Y-%m-%d " + "23:59:59")
                    end_time = datetime.datetime.now().strftime("%Y-%m-%d " + "23:59:59")
                    body = '{"token":"","pn":0,"rn":20,"sdt":"","edt":"","wd":"","inc_wd":"",' \
                           '"exc_wd":"","fields":"","cnum":"001",' \
                           '"sort":"{\\"istop\\":\\"0\\",\\"ordernum\\":\\"0\\",' \
                           '\\"webdate\\":\\"0\\",\\"rowid\\":\\"0\\"}",' \
                           '"ssort":"","cl":10000,"terminal":"","condition":[{' \
                           '"fieldName":"categorynum","equal":"014001004",' \
                           '"notEqual":null,"equalList":null,"notEqualList":[' \
                           '"014001018","004002005","014001015","014005014",' \
                           '"014008011"],"isLike":true,"likeType":2}],' \
                           '"time":[{"fieldName":"webdate",' \
                           '"startTime":"' + start_time + '",' \
                                                          '"endTime":"' + end_time + '"}],"highlights":"",' \
                                                                                     '"statistics":null,"unionCondition":[],"accuracy":"",' \
                                                                                     '"noParticiple":"1","searchRange":null,"noWd":true} '
                    response = requests.post(url=request.url, headers=request.headers, json=json.loads(body),
                                             timeout=120)
                    resp = Response(url=request.url, body=response.content, request=request)
                    return resp

                response = requests.post(url=request.url, headers=request.headers, json=json.loads(request.body),
                                         timeout=120)
                resp = Response(url=request.url, body=response.content, request=request)
                return resp
        if self.proxy:
            request.meta['proxy'] = self.proxy

    def process_response(self, request, response, spider):
        """当下载器完成http请求，返回响应给引擎的时候调用process_response"""

        if response.status in self.retry_http_codes:
            self.errorcount += 1
            if request.meta.get('middleware') == "requests":
                requests.get(url="http://www.ccgp.gov.cn/", headers={'User-Agent': random.choice(USER_AGENTS)})
            time.sleep(random.random() * 10)
            if self.errorcount > 3:
                logging.error('error status' + str(response.status), exc_info=True)
                raise IgnoreRequest("Ignoring this request")
            return request
        if re.search("频繁访问", response.text):
            self.errorcount += 1
            print("频繁访问, 等待20s")
            time.sleep(20)
            if self.errorcount > 5:
                logging.error('error status' + str(response.status), exc_info=True)
                return response
            return request

        return response

    def process_exception(self, request, exception, spider):
        if self.errorcount < 5:
            self.errorcount += 1
            return request
        if isinstance(exception, TimeoutError):
            return request
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        # pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def getHtml(self, request, body):
        # ....
        retry_count = 50
        while retry_count > 0:
            try:
                if self.proxy is None:
                    self.proxy = get_proxy().get("proxy")
                print(self.proxy)
                if body is not None:
                    html = requests.post(url=request.url, headers=request.headers,
                                         proxies={"https": "http://{}".format(self.proxy)}, json=json.loads(body),
                                         timeout=120)
                else:
                    html = requests.get(url=request.url, headers={'User-Agent': random.choice(USER_AGENTS)},
                                        proxies={"https": "http://{}".format(self.proxy)}, timeout=30)
                if html.status_code != 200:
                    raise Exception
                return html
            except Exception as e:
                print(e)
                retry_count -= 1
                # 删除代理池中代理
                delete_proxy(self.proxy)
                self.proxy = None
        return None


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


class requestsMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self):
        self.errorcount = 0
        self.retry_http_codes = [302, 403, 400, 405, 404, 504, 503]
        # 预先保留在settings中的代理IP列表
        self.proxies = settings.PROXIES
        self.proxy = None

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        if request.meta.get('middleware') == "requests":
            time.sleep(random.random() * 5)
            if request.method == 'GET':
                response = requests.get(request.url, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=120)
                resp = HtmlResponse(url=request.url, body=response.content, request=request,
                                    status=response.status_code, encoding='utf-8')
            else:
                response = requests.post(request.url, headers={'User-Agent': USER_AGENT}, data=json.loads(request.body),
                                         timeout=120)
                resp = Response(url=request.url, body=response.content, status=response.status_code, request=request)

            return resp

    def process_exception(self, request, exception, spider):
        if self.errorcount < 5:
            self.errorcount += 1
            return request
        if isinstance(exception, TimeoutError):
            return request
        # Called when a download handler or a process_request()+
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        # pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
