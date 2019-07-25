#!/usr/bin/env python3
# coding: utf-8

import pymongo

from setting import *


class MongoDB:
    client = None

    # 连接mongoDB
    @staticmethod
    def get_client():
        if MongoDB.client:
            return MongoDB.client
        else:
            MongoDB.client = pymongo.MongoClient(host=MONGO_URI, port=MONGO_PORT)
            print('mongo link')
            return MongoDB.client

    # 断开mongoDB连接
    @staticmethod
    def close_client():
        if MongoDB.client:
            print('MongoDB已关闭')
            MongoDB.client.close()
            MongoDB.client = None


if __name__ == '__main__':

    db = MongoDB.get_client()['weibo']
    topic_collection = db['topic']
    weibo_collection = db['weibo']
    food_collection = db['food']
    new_food = db['new_food']
    food_0_10 = db['food_0_10']
    food_10_100 = db['food_10_100']
    food_100 = db['food_100']

    comment_collection = db['comment']
    new_comment = db['new_comment']

    import csv

    topic_set = topic_collection.find().sort('text_num', pymongo.DESCENDING)
    # fr = open('test1.csv', encoding='utf-8')
    # reader = csv.reader(fr)
    # for row in reader:
    #     print(row)
    with open('test2.csv', 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['话题ID', '微博ID', '用户名', '内容', '评论数', '转发数', '点赞数', '发布时间'])
        topic_id = ''
        for topic in topic_set:
            if topic['text_num'] < 5:
                continue
            topic_id = str(topic['_id'])
            weibo_id_list = topic['text_id_list']
            for weibo_id in weibo_id_list:
                weibo = weibo_collection.find_one({'id': weibo_id})
                row = [topic_id, weibo_id, weibo['username'], weibo['content'], weibo['comment_count'],
                       weibo['forward_count'], weibo['like_count'], weibo['posted_at']]
                writer.writerow(row)

    # topicset = topic_collection.find().sort('text_num',pymongo.DESCENDING)
    # for topic in topicset:
    #     if 'score' not in topic or not topic['score']:
    #         data = [0, 0, 0]
    #         for weibo_id in topic['text_id_list']:
    #             comments = comment_collection.find({'id': weibo_id})
    #             for comment in comments:
    #                 if 'score' not in comment:
    #                     continue
    #                 score = comment['score']
    #                 if score[0] - score[1] > 2:
    #                     data[0] += 1
    #                 elif score[0] - score[1] < 0:
    #                     data[1] += 1
    #                 else:
    #                     data[2] += 1
    #         topic['score'] = data
    #         topic_collection.update_one({'_id': topic['_id']}, {'$set': topic}, True)
    # dataset = new_food.find()
    # count = 0
    # for data in dataset:
    #     if re.match('\d+$', data['key']):
    #         new_food.delete_one({'key': data['key']})
    # for data in dataset:
    #     count += 1
    #     print(count)
    #     key = ''
    #     for char in data['key']:
    #         asc = ord(char)
    #         if asc < 48 or 57 < asc < 65 or 90 < asc < 97 or 122 < asc < 128:
    #             continue
    #         else:
    #             key = key + char
    #     num = data['num']
    #     flag = True
    #     for new_data in new_food.find():
    #         new_key = new_data['key']
    #         new_num = new_data['num']
    #         if key in new_key:
    #             new_data['num'] = num + new_num
    #             new_data['key'] = key
    #             new_food.update_one({'key': new_key}, {'$set': new_data}, True)
    #             flag = False
    #             break
    #         elif new_key in key:
    #             new_data['num'] = num + new_num
    #             new_food.update_one({'key': new_key}, {'$set': new_data}, True)
    #             flag = False
    #             break
    #     if flag:
    #         new_food.insert_one(data)

    # num = data['num']
    # if num < 10:
    #     food_0_10.update_one({'key': data['key']}, {'$set': data}, True)
    # elif 10 <= num < 100:
    #     food_10_100.update_one({'key': data['key']}, {'$set': data}, True)
    # else:
    #     food_100.update_one({'key': data['key']}, {'$set': data}, True)

    # 清空话题
    # topic_collection.remove()
    # dataset = weibo_collection.find()
    # for data in dataset:
    #     data['if_topic'] = False
    #     weibo_collection.update_one({'id': data['id']}, {'$set': data}, True)
    #
    # MongoDB.close_client()
