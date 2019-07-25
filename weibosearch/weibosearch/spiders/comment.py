# -*- coding: utf-8 -*-
import re

import pymongo
import scrapy
from scrapy import FormRequest, Request
from weibosearch.settings import *

from weibosearch.items import *
from lxml import etree

class CommentSpider(scrapy.Spider):
    """
    微博评论爬虫
    """
    name = 'comment'
    allowed_domains = ['weibo.com']
    start_url = 'https://weibo.com/aj/v6/comment/big?ajwvr=6&id={mid}&page={page}&filter=hot&filter_tips_before=0&from=singleWeiBo'
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]


    def start_requests(self):
        dataset = self.db['weibo'].find()

        for data in dataset:
            if 'if_comment' not in data or not data['if_comment']:
                url = 'https://weibo.com/{uid}/{id}'.format(uid=data['uid'], id=data['id'])
                yield Request(url, callback=self.parse)


    def parse(self, response):
        id = re.search('.*/(.*)', response.url).group(1)
        text = response.text
        mid = re.search('&act=(\d+)', text).group(1)
        if not self.db['mid'].find_one({'mid': mid}):
            mid_item = MidItem()
            for field in mid_item.fields:
                try:
                   mid_item[field] = eval(field)
                except NameError:
                    self.logger.debug('Field is Not Defined' + field)
            yield mid_item

        url = self.start_url.format(mid=mid, page='1')
        yield Request(url, callback=self.parse_detail)

    def is_all_comment(self, mid):
        id = self.db['mid'].find_one({'mid': mid})['id']
        weibo = self.db['weibo'].find_one({'id': id})
        weibo['if_comment'] = True
        self.db['weibo'].update_one({'_id': weibo['_id']}, {'$set': weibo}, True)


    def parse_detail(self, response):
        mid = re.search('id=(\d+)', response.url).group(1)
        page = re.search('page=(\d+)', response.url).group(1)
        print(mid, page)
        text = response.text
        text = re.sub(r'list_box_in S_bg3.*?\\u5982\\u679c\\u8fd4\\u56de\\u6709\\u4e8c\\u7ea7\\u8bc4\\u8bba', '', text)
        result = []
        id_list = re.finditer(r'comment_id=\\"(\d+)\\"', text)

        count = 0
        for item in id_list:
            if not item.group(1).strip():
                print(mid, page, 'yes0')
                self.is_all_comment(mid)
                return
            if self.db['comment'].find_one({'comment_id': item.group(1)}):
                print(mid, page, 'yes')
                self.is_all_comment(mid)
                return
            count += 1
            result.append([item.group(1)])

        finditer = re.finditer(r'(<div class=\\"WB_text.*?/div>)', text)
        count = 0
        for item in finditer:
            item_text = item.group(1)
            uid = re.search('id=(\d+)', item_text).group(1)
            result[count].append(uid)
            if 'icon_approve' in item_text:
                result[count].append(True)
            else:
                result[count].append(False)
            if 'vip' in item_text:
                result[count].append(True)
            else:
                result[count].append(False)
            content = re.sub('<.*?>', '', item_text)

            content = content.encode('utf-8').decode('unicode_escape').strip()
            content = content.split('：')
            username = content[0]
            content = content[1]
            result[count].append(username)
            result[count].append(content)
            count += 1

        posted_times = re.finditer(r'WB_from S_txt2.*?>(.*?)<', text)
        count = 0
        for item in posted_times:
            result[count].append(item.group(1).encode('utf-8').decode('unicode_escape').strip())
            count += 1
        like_counts = re.finditer(r'like_status.*?em><em>(.*?)<', text)
        count = 0
        for item in like_counts:
            like_count = item.group(1)
            if 'u8d5e' in like_count:
                like_count = 0
            else:
                like_count = int(like_count)
            result[count].append(like_count)
            count += 1
        print(result)

        if not result:
            print(mid, page, 'yes2')
            self.is_all_comment(mid)
            return
        for item in result:
            if self.db['comment'].find_one({'comment_id': item[0]}):
                continue
            comment_item = CommentItem()
            comment_item['mid'] = mid
            comment_item['comment_id'] = item[0]
            comment_item['uid'] = item[1]
            comment_item['is_v'] = item[2]
            comment_item['is_vip'] = item[3]
            comment_item['username'] = item[4]
            comment_item['content'] = item[5]
            comment_item['posted_at'] = item[6]
            comment_item['like_count'] = item[7]
            yield comment_item

        url = self.start_url.format(mid=mid, page=str(int(page) + 1))
        yield Request(url, callback=self.parse_detail)