# -*- coding: utf-8 -*-


# 公告列表页数据对象
class PageAttribute:
    def __init__(self, largest_page, cur_latest_url, page_size, cur_page, urls: list, newest_time, oldest_time):
        self.largest_page = largest_page
        self.cur_latest_url = cur_latest_url
        self.cur_page = cur_page
        self.page_size = page_size
        self.urls = urls
        self.newest_time = newest_time
        self.oldest_time = oldest_time
