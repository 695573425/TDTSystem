# -*- coding: utf-8 -*-
import re

import pymongo
import scrapy
from scrapy import Request
from weibosearch.items import RepostItem
from weibosearch.settings import *

class RepostSpider(scrapy.Spider):
    """
    微博转发爬虫
    """
    name = 'repost'
    allowed_domains = ['weibo.cn']
    start_url = 'https://weibo.cn'
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db['weibo']
    topic_collection = db['topic']

    def start_requests(self):
        dataset = self.topic_collection.find(skip=10).sort('text_num', pymongo.DESCENDING)
        for data in dataset:
            if data['text_num'] < 4:
                continue
            for id in data['text_id_list']:
                url = '{url}/repost/{id}'.format(url=self.start_url, id=id)
                yield Request(url, callback=self.parse2)
        #
        # id = 'HtIlkjqb4'
        # url = '{url}/repost/{id}'.format(url=self.start_url, id=id)
        # yield Request(url, callback=self.parse2)
    def parse2(self, response):
        id = re.search('repost\/([a-zA-Z0-9]*)', response.url).group(1)
        div = response.xpath('//div[@id="M_"]/div')
        if div:
            uid = div[0].xpath('./a')[0].xpath('./@href').extract_first()
            area = None
            repost_item = RepostItem()
            for field in repost_item.fields:
                try:
                    repost_item[field] = eval(field)
                except NameError:
                    self.logger.debug('Field is Not Defined' + field)
            yield repost_item
            yield Request('https://weibo.cn' + uid+'?', callback=self.parse3)

    def parse3(self, response):
        print(response.url)
        uid = re.search('weibo.cn\/(.*?)\?', response.url)
        if not uid:
            uid = re.search('weibo.cn(.*)', response.url)
        uid = uid.group(1)
        print(uid)

        temp = ''.join(response.xpath('//div[@class="ut"]//text()').extract())
        area = re.search('/(.*?)\xa0', temp).group(1).strip()
        print(area)
        id = None
        repost_item = RepostItem()
        for field in repost_item.fields:
            try:
                repost_item[field] = eval(field)
            except NameError:
                self.logger.debug('Field is Not Defined' + field)
        yield repost_item


    def parse(self, response):
        id = re.search('repost\/([a-zA-Z0-9]*)', response.url)

        page = re.search('page', response.url)
        if not id:
            return
        uid = response.xpath('//div[@id="M_"]/div')[0].xpath('./a')[0].xpath('./@href').extract_first()
        print(uid)
        id = id.group(1)
        if not page:
            pid = response.xpath('//a[@class="cc"][contains(., "原文评论[")]/@href').extract_first()
            if pid:
                pid = re.search('/comment\/([a-zA-Z0-9]*)', pid).group(1)
                content_div = response.xpath('//div[@id="M_"]/div')[-1]
                content = ''.join(content_div.xpath('.//text()').extract())
                content = re.match('.*?:\s*(.*?) +\xa0', content).group(1)
            else:
                content_div = response.xpath('//div[@id="M_"]/div')[0]
                content = ''.join(content_div.xpath('.//text()').extract())
                content = re.match('.*?:(.*?) +\xa0', content).group(1)
            forward_count = response.xpath('//span[@class="pms"]//text()').re_first('转发\[(.*?)\]')
            if not forward_count:
                forward_count = 0
            else:
                forward_count = int(forward_count)
            comment_count = response.xpath('//a[contains(., "评论[")]//text()').re_first('^评论\[(.*?)\]')
            if not comment_count:
                comment_count = 0
            else:
                comment_count = int(comment_count)
            like_count = response.xpath('//a[contains(., "赞[")]//text()').re_first('赞\[(.*?)\]')
            if not like_count:
                like_count = 0
            else:
                like_count = int(like_count)
            posted_at = response.xpath('//div[@id="M_"]//span[@class="ct"]//text()').extract_first(default=None)
            user = response.xpath('//div[@id="M_"]/div[1]')
            username = user.xpath('./a/text()').extract_first(default=None)
            is_v = bool(user.xpath('./img[@alt="V"]').extract_first())
            is_vip = bool(user.xpath('./img[@alt="M"]').extract_first())
            repost_item = RepostItem()

            for field in repost_item.fields:
                try:
                    repost_item[field] = eval(field)
                except NameError:
                    self.logger.debug('Field is Not Defined' + field)
            yield repost_item
        repost_list = []

        for item in response.xpath("//span[@class='cc']"):
            repost_list.append(re.search('attitude/(.*?)/', item.xpath('./a/@href').extract_first()).group(1))
        for rid in repost_list:
            url = '{url}/repost/{id}'.format(url=self.start_url, id=rid)
            yield Request(url, callback=self.parse)
        next_page_url = response.xpath('//div[@id="pagelist"]//a[contains(.,"下页")]/@href').extract_first()
        if next_page_url:
            next_page_url = self.start_url + next_page_url
            yield Request(next_page_url, callback=self.parse)
        else:
            data = self.collection.find_one({'id': id})
            if data:
                data['if_repost'] = True
                self.collection.update({'id': data['id']}, {'$set': data}, True)
