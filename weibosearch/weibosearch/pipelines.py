# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging

import pymongo
import re
import time

from weibosearch.items import *

class WeiboPipeline(object):

    def parse_time(self, datetime):
        if '\xa0' in datetime:
            datetime = re.search('(.*?)\xa0', datetime).group(1)
        if re.match('\d+月\d+日', datetime):
            datetime = datetime.replace('月', '-')
            datetime = datetime.replace('日', '')
            datetime = time.strftime('%Y-', time.localtime()) + datetime + ':00'
        if re.match('\d+分钟前', datetime):
            minute = re.match('(\d+)', datetime).group(1)
            datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - float(minute) * 60))
        if re.match('今天.*', datetime):
            datetime = re.match('今天(.*)', datetime).group(1).strip()
            datetime = time.strftime('%Y-%m-%d', time.localtime()) + ' ' + datetime + ':00'

        return datetime

    def process_item(self, item, spider):
        if isinstance(item, WeiboItem) or isinstance(item, CommentItem):
            if item.get('content'):
                item['content'] = item['content'].lstrip(':').strip()
            if item.get('posted_at'):
                item['posted_at'] = item['posted_at'].strip()
                item['posted_at'] = self.parse_time(item['posted_at'])
        return item


class MongoPipeline():
    def __init__(self, mongo_uri, mongo_db):
        self.logger = logging.getLogger(__name__)
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.weibo_count = 0
        self.comment_count = 0

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, WeiboItem):
            self.db[item.table_name].update({'id': item.get('id')}, {'$set': dict(item)}, True)
            self.weibo_count += 1
            self.logger.debug('get total count:' + str(self.weibo_count))
        elif isinstance(item, CommentItem):
            self.db[item.table_name].update({'comment_id': item.get('comment_id'), 'mid': item.get('mid')}, {'$set': dict(item)}, True)
            self.comment_count += 1
            self.logger.debug('get total count:' + str(self.comment_count))
        elif isinstance(item, FoodItem):
            self.db[item.table_name].update({'key': item.get('key')}, {'$set': dict(item)}, True)
        elif isinstance(item, RepostItem):
            # self.db[item.table_name].update({'id': item.get('id')}, {'$set': dict(item)}, True)
            self.db[item.table_name].insert_one(dict(item))
        elif isinstance(item, UserItem):
            self.db[item.table_name].update({'uid': item.get('uid')}, {'$set': dict(item)}, True)
        elif isinstance(item, MidItem):
            self.db[item.table_name].update({'id': item.get('id')}, {'$set': dict(item)}, True)
        return item

