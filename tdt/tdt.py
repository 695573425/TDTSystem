#!/usr/bin/python
# coding=utf-8
import codecs
import re
import sys
import time
from math import *

import pymongo
from gensim import corpora
from gensim.models import LdaModel
from lxml import etree
from pyecharts import options
from pyecharts.charts import Scatter, Line

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

import warnings

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

sys.path.append('E:\Python\workspace\TDTSystem')
from setting import *
from mongo import MongoDB
from text2vec.text2vec import Text2Vec
from ltp.ltp import Ltp


class Tdt:
    """
    话题检测与追踪算法类
    检测： 从数据流中识别出未知新话题
    追踪： 对后续数据判断是否属于某已有话题，对已有话题实时更新
    """
    model = None

    @staticmethod
    def get_object():
        if Tdt.model:
            print('Text2Vec Ready!')
            return Tdt.model
        else:
            print('Text2Vec init!')
            Tdt.model = Tdt()
            return Tdt.model

    def xml_analysis(self, xml_path):
        tree = etree.parse(xml_path)
        root = tree.getroot()
        f = codecs.open('txt/' + re.sub('\.xml', '.txt', xml_path), 'w', 'utf-8')
        for child in root:
            text = ''.join(child.xpath('.//text()'))
            text = re.sub('\n', '', text)
            id = child.attrib.get('id')
            f.write(id + '\t' + text + '\n')
        f.close()

    def tfidf_calculate(self, data):
        """
        tf.idf词频统计
        :param data: list, 文档集合，每个运算为一文档字符串
        :return: word: list, 词袋； weight：矩阵，weight[i][j]为词袋第i个词在文档集合data第j个文档的权重
        """
        corpus = []
        for line in data:
            corpus.append(line.strip())

        vectorizer = CountVectorizer()  # 该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
        transformer = TfidfTransformer()  # 该类会统计每个词语的tf-idf权值
        tfidf = transformer.fit_transform(
            vectorizer.fit_transform(corpus))  # 第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵
        word = vectorizer.get_feature_names()  # 获取词袋模型中的所有词语
        weight = tfidf.toarray()  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重

        return word, weight

    def get_timestamp(self, time_str):
        """
        时间字符串转化为时间戳，例："1970-01-02 00:00:00" -> 86400
        :param time_str: str
        :return: int
        """
        try:
            time_array = time.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None
        time_stamp = int(time.mktime(time_array))
        return time_stamp

    def datetime_update(self, datetime1, datetime2, num=None):
        """
        更新话题中心时间，等于话题所有文档发布时间的平均值
        :param datetime1: str, 原话题中心时间
        :param datetime2: str, 新加入文档的发布时间
        :param num: 原话题文档数量
        :return: str
        """
        if not num:
            num = 1

        time_stamp1 = self.get_timestamp(datetime1)
        time_stamp2 = self.get_timestamp(datetime2)
        if not time_stamp1 or not time_stamp2:
            return None
        time_stamp = (time_stamp1 * num + time_stamp2) / (num + 1)
        time_array = time.localtime(time_stamp)
        return time.strftime("%Y-%m-%d %H:%M:%S", time_array)

    def dict_combine(self, dict1, dict2, num):
        """
        字典合并，dict2合并到dict1
        :param dict1:
        :param dict2:
        :param num:
        :return:
        """
        for word in dict2:
            if word not in dict1:
                dict1[word] = 0.0
            dict1[word] = (dict1[word] * num + dict2[word]) / (num + 1)

    def single_pass(self, weibo, topic_table, ltp=None, text2vec=None):
        """
        Single-Pass聚类算法，微博weibo属于话题集topic_set某话题，则加入话题并更新话题，否则，自成一个话题加入话题库
        :param ltp: Ltp类实例
        :param text2vec: Text2Vec类实例
        :param topic_table: str, mongoDB话题库名
        :param weibo:dict, 微博数据
        :return:
        """
        if 'if_topic' in weibo and weibo['if_topic']:
            return
        if not ltp:
            ltp = Ltp.get_object()
        if not text2vec:
            model = Text2Vec.get_object()
        else:
            model = text2vec
        content = weibo['content']
        parser = ltp.text_parser(content)
        vector = model.text2dict(list(parser[0:3]))  # 微博切分: [标题, 正文, hashtag]
        entity = parser[3]  # 命名实体
        topic_collection = MongoDB.get_client()[MONGO_DB][topic_table]
        topic_set = topic_collection.find()
        similiratiy = []  # 存储微博与所有话题的相似度

        for topic in topic_set:
            # if cls > 0 and cls != topic['cls'] :
            #     continue
            keydict = topic['keywords']
            vector2 = {}
            count = 0
            for key, value in keydict.items():
                if len(vector2) > len(vector):
                    break
                vector2[key] = value
                count += value
            similar_score = model.similarity(vector2, vector)   # 计算相似度

            if similar_score < 0.4:  # 相似度低，微博不属于话题，判断是否将话题淘汰
                time_gip = (self.get_timestamp(weibo['posted_at']) -
                            self.get_timestamp(topic['latest_time'])) / 86400
                if topic['text_num'] < 5 and time_gip > 60:  # 话题微博数小于5且两个月得不到更新，淘汰
                    topic_collection.delete_one({'_id': topic['_id']})
                else:
                    similiratiy.append(similar_score)
            else:
                similiratiy.append(similar_score)

        try:
            score = max(similiratiy)
        except:
            score = 0.0

        if score >= 0.5:    # 微博加入话题，更新话题
            index = similiratiy.index(score)
            topic = topic_collection.find_one(skip=index)
            keywords = topic['keywords']
            text_num = topic['text_num']
            topic['text_id_list'].append(weibo['id'])
            topic['text_list'].append(weibo['content'])
            ltp.netag_dict_merge(topic['entity'], entity)
            self.dict_combine(keywords, vector, text_num)
            topic['keywords'] = dict(sorted(keywords.items(), key=lambda item: item[1], reverse=True))
            topic['heat'] += weibo['comment_count'] + sqrt(weibo['forward_count'] + weibo['like_count'])
            topic['text_num'] += 1
            if weibo['posted_at'] < topic['start_time']:
                topic['start_time'] = weibo['posted_at']
            elif weibo['posted_at'] > topic['latest_time']:
                topic['latest_time'] = weibo['posted_at']
            topic['central_time'] = self.datetime_update(topic['central_time'], weibo['posted_at'], text_num)
            topic_collection.update_one({'_id': topic['_id']}, {'$set': topic}, True)
        else:   # 微博自成一新话题
            one_topic = {
                'entity': {},
                'keywords': {},
                'text_id_list': [],
                'text_list': [],
                'text_num': 1,
                'heat': 0,
                'start_time': None,
                'latest_time': None,
                'central_time': None,
                # 'cls': cls
            }
            one_topic['text_id_list'].append(weibo['id'])
            one_topic['text_list'].append(weibo['content'])
            one_topic['entity'] = entity
            one_topic['heat'] = weibo['comment_count'] + sqrt(weibo['forward_count'] + weibo['like_count'])
            one_topic['start_time'] = one_topic['latest_time'] = one_topic['central_time'] = weibo['posted_at']
            one_topic['keywords'] = dict(sorted(vector.items(), key=lambda item: item[1], reverse=True))
            topic_collection.insert_one(one_topic)
        weibo['if_topic'] = True




if __name__ == '__main__':
    dirname, filename = os.path.split(os.path.abspath(__file__))  # 获取执行文件路径
    path = dirname + '\\data\\'  # 获取数据文件夹路径

    """single-pass"""
    # filename = r'data\weibo.cut'
    # fr = codecs.open(filename, 'r', 'utf-8')
    # lines = fr.readlines()
    # data = []
    # for line in lines:
    #     data.append(line)
    # (tfidf_words, tfidf_weight) = tfidf_calculate(data)
    # fr.close()

    ltp = Ltp(3)
    ltp.create_stopwordslist(STOPWORDS_DIR)
    # parser = ltp.text_parser('#成都七中实验学校食品安全问题# 哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈')
    # parser1 = ltp.text_parser('【网曝成都七中实验学校#给学生吃变质食品# 官方再次回应：已对8名负责人展开调查】据成都市温江区人民政府新闻办公室官方微博@金温江：温江区公安分局目前正在对掌握的成都七中实验学校负责食品安全的8名责任人开展全面深入的调查。区市场监管局对投诉反映的19个批次的食材进行了抽样，对所有冻库及库房内食材进行了查封，对新进食材进行全程监管。区市场监管局、区教育局举一反三，已组织开展全区大中小学和幼儿园食堂食品安全的专项检查，切实保障学生的身体健康。温江区委、区政府将依法依规对成都七中实验学校食品安全问题进行认真彻查，严肃处理相关责任人，及时公布调查处理结果。')
    # model = Text2Vec()
    # score = model.similarity(list(parser[0:3]), list(parser1[0:3]))
    # print(score)
    ttt = Tdt()
    # ttt.single_pass(ltp)
