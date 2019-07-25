# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html


from scrapy import Item, Field

class FoodItem(Item):
    table_name = 'food_keywords'
    key = Field()
    num = Field()

class MidItem(Item):
    table_name = 'mid'
    id = Field()
    mid = Field()

class UserItem(Item):
    table_name = 'user'

    uid = Field()
    username = Field()
    sex = Field()
    intro = Field()
    area = Field()
    follow_count = Field()
    fans_count = Field()
    weibo_count = Field()

class WeiboItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    table_name = 'weibo'

    id = Field()
    content = Field()
    forward_count = Field()
    comment_count = Field()
    like_count = Field()
    posted_at = Field()
    username = Field()
    uid = Field()
    is_v = Field()
    is_vip = Field()

class CommentItem(Item):

    table_name = 'comment'
    mid = Field()
    comment_id = Field()
    uid = Field()
    is_v = Field()
    is_vip = Field()
    username = Field()
    content = Field()
    posted_at = Field()
    like_count = Field()

class RepostItem(Item):

    table_name = 'repost'

    # id = Field()
    # uid = Field()
    # pid = Field()
    # content = Field()
    # forward_count = Field()
    # comment_count = Field()
    # like_count = Field()
    # posted_at = Field()
    # username = Field()
    # is_v = Field()
    # is_vip = Field()

    area = Field()
    uid = Field()
    id = Field()

