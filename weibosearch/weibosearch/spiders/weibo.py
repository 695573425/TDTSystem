# -*- coding: utf-8 -*-
import re

import pymongo
import scrapy

from scrapy import FormRequest, Request

from weibosearch.items import *
from weibosearch.settings import *

class WeiboSpider(scrapy.Spider):
    """
    微博爬虫
    """
    name = 'weibo'
    allowed_domains = ['weibo.cn', 'weibo.com']
    search_rul = 'https://weibo.cn/search/mblog'
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]

    def __init__(self, keyword=None, start_page=None, end_page=None, sort=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword = keyword
        try:
            self.start_page = int(start_page)
        except:
            self.start_page = None
        try:
            self.end_page = int(end_page)
        except:
            self.end_page = None
        self.sort = sort
        pass

    def start_requests(self):
        if not self.keyword:
            self.keyword = '食品安全'
        if not self.start_page:
            self.start_page = 1
        if not self.end_page:
            self.end_page = 100
        if self.end_page < self.start_page:
            self.end_page = self.start_page
        if not self.sort or (self.sort != 'time' and self.sort != 'hot'):
            self.sort = 'hot'

        url = '{url}?keyword={keyword}&sort={sort}'.format(url=self.search_rul, keyword=self.keyword, sort=self.sort)

        for page in range(self.start_page, self.end_page + 1):
            data = {
                'mp': str(self.end_page),
                'page': str(page)
            }
            self.logger.debug('第' + str(page) + '页: keyword:' + self.keyword)
            yield FormRequest(url, formdata=data, callback=self.parse_index)

        # client = pymongo.MongoClient('localhost')
        # db = client['weibo']
        # collection = db['weibo']
        # dataset = collection.find(skip=225)
        # client.close()
        # for data in dataset:
        #     id = data['id']
        #     url = 'https://weibo.cn/comment/'+id
        #     yield Request(url, callback=self.parse_detail)

        # url = 'https://weibo.cn/comment/Hhu4X4VH6'
        # yield Request(url, callback=self.parse_detail)


    def parse_index(self, response):
        weibos = response.xpath('//div[@class="c" and contains(@id, "M_")]')
        for weibo in weibos:
            if bool(weibo.xpath('.//span[@class="cmt"]').extract_first()):
                detail_url = weibo.xpath('.//a[contains(., "原文评论[")]//@href').extract_first()
                yield Request(detail_url, callback=self.parse_detail)
                continue
            id = weibo.xpath('./@id').extract_first()
            id = re.search('M_([a-zA-Z0-9]+)', id).group(1)
            content = ''.join(weibo.xpath('.//text()').extract())
            content = re.search('.*?:(.*?)\xa0', content).group(1)
            comment_count = int(weibo.xpath('.//a[contains(., "评论[")]//text()').re_first('评论\[(.*?)\]', default=0))
            forward_count = int(weibo.xpath('.//a[contains(., "转发[")]//text()').re_first('转发\[(.*?)\]', default=0))
            like_count = int(weibo.xpath('.//a[contains(., "赞[")]//text()').re_first('赞\[(.*?)\]', default=0))
            posted_at = weibo.xpath('.//span[@class="ct"]//text()').extract_first(default=None)
            username = weibo.xpath('.//a[@class="nk"]/text()').extract_first(default=None)
            uid = weibo.xpath('.//a[contains(., "评论[")]//@href').extract_first()
            uid = re.search('uid=(\d+)', uid).group(1)
            if not self.db['user'].find_one({'uid': uid}):
                url = 'https://weibo.com/aj/v6/user/newcard?ajwvr=6&id={uid}&type=1'.format(uid=uid)
                yield Request(url, callback=self.parse_user)
            is_v = bool(weibo.xpath('.//img[@alt="V"]').extract_first())
            is_vip = bool(weibo.xpath('.//img[@alt="M"]').extract_first())
            # print(id, content, comment_count, forward_count, like_count, posted_at, username, uid, is_v, is_vip)
            weibo_item = WeiboItem()
            for field in weibo_item.fields:
                try:
                    weibo_item[field] = eval(field)
                except NameError:
                    self.logger.debug('Field is Not Defined' + field)
            yield weibo_item

    def parse_user(self, response):
        uid = re.search('id=(\d+)', response.url).group(1)
        text = response.text
        username = re.search('W_f14.*?>(.*?)<', text).group(1)
        username = username.encode('utf-8').decode('unicode_escape')
        if 'female' in text:
            sex = 'female'
        elif 'male' in text:
            sex = 'male'
        else:
            sex = None
        intro = re.search(r'intro.*?title=\\"(.*?)\\"', text).group(1)
        intro = intro.encode('utf-8').decode('unicode_escape')
        result = re.finditer('num +W_fb.*?>(.*?)<', text)
        counts = []
        area = re.search(r'interval.*?>(.*?)<', text).group(1)
        area = area.encode('utf-8').decode('unicode_escape')
        for item in result:
            count = item.group(1)
            if not count:
                count.append(0)
            else:
                if '\\u' in count:
                    count = count.encode('utf-8').decode('unicode_escape')
                counts.append(count)
        follow_count = counts[0]
        fans_count = counts[1]
        weibo_count = counts[2]
        user_item = UserItem()
        for field in user_item.fields:
            try:
                user_item[field] = eval(field)
            except NameError:
                self.logger.debug('Field is Not Defined' + field)
        yield user_item


    def parse_detail(self, response):
        id = re.search('comment\/([a-zA-Z0-9]*)', response.url).group(1)

        content_div = response.xpath('//div[@id="M_"]/div')[0]
        content = ''.join(content_div.xpath('.//text()').extract())
        content = re.match('.*?:(.*?) +\xa0', content).group(1)
        comment_count = int(response.xpath('//span[@class="pms"]//text()').re_first('评论\[(.*?)\]', default=0))
        forward_count = int(response.xpath('//a[contains(., "转发[")]//text()').re_first('转发\[(.*?)\]', default=0))
        like_count = int(response.xpath('//a[contains(., "赞[")]//text()').re_first('赞\[(.*?)\]', default=0))
        posted_at = response.xpath('//div[@id="M_"]//span[@class="ct"]//text()').extract_first(default=None)
        user = response.xpath('//div[@id="M_"]/div[1]')
        username = user.xpath('./a/text()').extract_first(default=None)
        uid = response.xpath('.//a[contains(., "操作")]//@href').extract_first()
        uid = re.search('uid=(\d+)', uid).group(1)
        is_v = bool(user.xpath('./img[@alt="V"]').extract_first())
        is_vip = bool(user.xpath('./img[@alt="M"]').extract_first())
        weibo_item = WeiboItem()
        for field in weibo_item.fields:
            try:
                weibo_item[field] = eval(field)
            except NameError:
                self.logger.debug('Field is Not Defined' + field)
        yield weibo_item
