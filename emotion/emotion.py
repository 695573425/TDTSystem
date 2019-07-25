# -*- coding: utf-8 -*-

import codecs
import re

import sys

from lxml import etree

import matplotlib.pyplot as plt
import numpy as np

from setting import *


sys.path.append('E:\Python\workspace\TDTSystem')
from ltp.ltp import Ltp


# 文本情感分析类
class EmotionAnalysis:

    def __init__(self, ltp):
        """
        init class
        :param ltp: Ltp类实例
        """
        self.ltp = ltp
        self.postive_list = []
        self.negative_list = []
        self.deny_list = []
        self.degree_list = []

        if POSTIVE_DICT_PATH:  # 载入正向情感词典
            self.postive_list = self.open_dict(POSTIVE_DICT_PATH)
        if NEGATIVE_DICT_PATH:  # 载入负向情感词典
            self.negative_list = self.open_dict(NEGATIVE_DICT_PATH)
        if DENY_DICT_PATH:  # 载入否定词典
            self.deny_list = self.open_dict(DENY_DICT_PATH)
        if DEGREE_DICT_PATH:  # 载入程度副词词典
            self.degree_list = self.open_dict(DEGREE_DICT_PATH)

    def open_dict(self, file_path):
        """
        载入词典
        :param file_path: str, 词典路径
        :return: list, 词列表
        """
        dict = []
        with open(file_path, encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip()
                if line:
                    dict.append(line)
        return dict

    def judgeodd(self, num):
        """
        判断整数奇偶性
        :param num: int
        :return:
        """
        if (num % 2) == 0:
            return False
        else:
            return True

    def get_degree_score(self, word):
        """
        获取程度副词的权重
        :param word: str
        :return: float
        """
        try:
            index = self.degree_list.index(word)
            print('d:', word)
            for i in range(len(DEGREE_SCORE[0])):
                if index < DEGREE_SCORE[0][i]:
                    return DEGREE_SCORE[1][i]
            return DEGREE_SCORE[1][i + 1]
        except:
            return 1.0

    def contain_word(self, sentence, word):
        """
        判断句子是否包含某单词
        :param sentence: list,
        :param word: str
        :return:
        """
        for words in sentence:
            if word in words:
                return True
        return False

    def word_arcs_analyse(self, i, arcs, roles=None):
        """
        根据情感词语在句子中的依存句法关系，修正情感分值
        :param i: int, 情感词在句子中的索引
        :param arcs: Ltp依存句法关系分析输出
        :param roles: Ltp语义角色标注输出
        :return: float
        """
        if roles:
            for role in roles:
                if i == role.index:
                    return 3.0
        label = arcs[i][1]
        if re.search('COO', label):
            label = arcs[arcs[i][0] - 1][1]
        print(label)
        if re.search('SBV|POB', label):
            return 0.0
        elif re.search('ATT|ADV', label):
            return 0.5
        elif re.search('VOB', label):
            return 2.0
        elif re.search('HED', label):
            return 3.0
        else:
            return 1.0

    def sentiment_score(self, parser):
        """
        句子情感分析算法
        :param parser: list, Ltp.sentence_parser输出
        :return: list, [正面情感分值， 负面情感分值]
        """
        words = parser[0]  # 分词结果
        arcs = parser[3]  # 依存句法分析结果
        roles = parser[4]   # 语义角色标注结果
        i = 0
        a = 0
        postive_score = 0.0
        negative_score = 0.0
        for i in range(len(words)):
            word = words[i].strip()
            if not word:
                continue
            temp_score = 0.0
            if word in self.postive_list:  # 扫描正面情感词
                print('+', word)
                temp_score = self.word_arcs_analyse(i, arcs, roles)
                c = 0
                for w in words[a:i]:    # 扫描程度副词
                    temp_score *= self.get_degree_score(w)
                    if w in self.deny_list:     # 扫描否定词
                        print('n: ', w)
                        c += 1
                if self.judgeodd(c):
                    postive_score += (temp_score * -1.0)
                else:
                    postive_score += temp_score
                a = i + 1

            elif word in self.negative_list:    # 扫面负面情感词
                print('-', word)
                temp_score = self.word_arcs_analyse(i, arcs, roles)
                c = 0
                for w in words[a:i]:
                    temp_score *= self.get_degree_score(w)
                    if w in self.deny_list:
                        print('n: ', w)
                        c += 1
                if self.judgeodd(c):
                    negative_score += (temp_score * -1.0)
                else:
                    negative_score += temp_score
                a = i + 1

            # elif word == '！' or word == '!':
            #     print(words)
            #     for w2 in words[::-1]:
            #         if w2 in self.postive_list or self.negative_list:
            #             postive_score *= 2.0
            #             negative_score *= 2.0
            #             break
            # i += 1 # 扫描词位置前移

            if postive_score < 0:
                negative_score -= postive_score
                postive_score = 0
            if negative_score < 0:
                postive_score -= negative_score
                negative_score = 0

        return [postive_score, negative_score]

    def sent_sentiment_score(self, text):
        """
        文档情感分析，文档分句，每句进行情感分析，后加权平均
        :param text:
        :return:
        """
        sents = [sentence for sentence in re.split(r'[，,]', text) if sentence]
        score = [0.0, 0.0]
        for sent in sents:
            parser = self.ltp.sentence_parser(sent)
            score_temp = self.sentiment_score(parser)
            # print(score_temp)
            score[0] += score_temp[0]
            score[1] += score_temp[1]
        # for review in senti_score_list:
        #     score_array = np.array(review)
        #     Pos = np.sum(score_array[:, 0])
        #     Neg = np.sum(score_array[:, 1])
        #     AvgPos = np.mean(score_array[:, 0])
        #     AvgPos = float('%.1f'%AvgPos)
        #     AvgNeg = np.mean(score_array[:, 1])
        #     AvgNeg = float('%.1f'%AvgNeg)
        #     StdPos = np.std(score_array[:, 0])
        #     StdPos = float('%.1f'%StdPos)
        #     StdNeg = np.std(score_array[:, 1])
        #     StdNeg = float('%.1f'%StdNeg)
        #     score.append([Pos, Neg, AvgPos, AvgNeg, StdPos, StdNeg])
        return score


def xml_analysis(xml_path):
    tree = etree.parse(xml_path)
    root = tree.getroot()
    fr1 = codecs.open('train_data.txt', 'a', 'utf-8')
    fr2 = codecs.open('train_label.txt', 'a', 'utf-8')
    for child in root:
        for sentence in child.xpath('.//sentence'):
            text = str(sentence.xpath('.//text()')[0]).strip()
            label = sentence.attrib.get('polarity')
            if label:
                if label == 'POS':
                    label = '1'
                elif label == 'NEG':
                    label = '-1'
            else:
                label = '0'

            if text:
                fr1.write(text + '\n')
                fr2.write(label + '\n')
            text = None
            label = None
    fr1.close()
    fr2.close()


if __name__ == '__main__':
    ltp = Ltp(4)
    ltp.load_dict(ALL_DICT_PATH)
    analyzer = EmotionAnalysis(ltp)

    sent = '苹果说，用户从即日起可以预定新款iPad，有关产品将于3月16日开始率先在美国、澳大利亚、加拿大、法国、中国香港和新加坡等10多个国家和地区率先上市。'

    print(analyzer.sent_sentiment_score(sent.strip()))
