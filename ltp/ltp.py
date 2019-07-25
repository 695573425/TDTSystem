#!/usr/bin/env python3
# coding: utf-8


import os
import re

from pyltp import Segmentor, Postagger, NamedEntityRecognizer, Parser, SementicRoleLabeller


from setting import *

class Ltp:
    """
    哈工大语言云(ltp)，自然语言处理工具，有五个模型，分别为：
    分词，词性标注，命名实体识别，依存句法分析，语义角色标注
    """
    ltp = None
    ltp_2 = None

    @staticmethod
    def get_object():
        if Ltp.ltp:
            print('Ltp Ready!')
            return Ltp.ltp
        else:
            print('Ltp init!')
            Ltp.ltp = Ltp(3)
            Ltp.ltp.create_stopwordslist(STOPWORDS_DIR)
            return Ltp.ltp

    @staticmethod
    def get_object2():
        if Ltp.ltp_2:
            print('Ltp2 Ready!')
            return Ltp.ltp_2
        else:
            print('Ltp2 init!')
            Ltp.ltp_2 = Ltp(4)
            return Ltp.ltp_2

    def __init__(self, model_num=None, LTP_DATA_DIR=None):
        """
        初始化
        :param model_num: 加载模型数
        :param LTP_DATA_DIR: ltp模型目录路劲
        """
        if not LTP_DATA_DIR:
            self.LTP_DATA_DIR = DEFAULT_LTP_DATA_DIR
        else:
            self.LTP_DATA_DIR = LTP_DATA_DIR

        if isinstance(model_num, int):
            self.load_model(model_num > 0, model_num > 1, model_num > 2, model_num > 3, model_num > 4)
        else:
            self.load_model()
        self.stopwords_list = None

    def load_model(self, segmentor=None, postagger=None, recognizer=None, parser=None, labeller=None):
        """

        :param segmentor: 是否加载分词模型
        :param postagger: 是否加载词性标注模型
        :param recognizer: 是否加载命名实体识别模型
        :param parser: 是否加载依存句法分析模型
        :param labeller: 是否加载语义角色标注模型
        :return:
        """
        self.segmentor = None
        self.postagger = None
        self.recognizer = None
        self.parser = None
        self.labeller = None
        # 分词模型
        if segmentor:
            self.segmentor = Segmentor()
            self.segmentor.load(os.path.join(self.LTP_DATA_DIR, "cws.model"))
        # 词性标注模型
        if postagger:
            self.postagger = Postagger()
            self.postagger.load(os.path.join(self.LTP_DATA_DIR, "pos.model"))
        # 命名实体识别模型
        if recognizer:
            self.recognizer = NamedEntityRecognizer()
            self.recognizer.load(os.path.join(self.LTP_DATA_DIR, "ner.model"))
        # 依存句法分析模型
        if parser:
            self.parser = Parser()
            self.parser.load(os.path.join(self.LTP_DATA_DIR, "parser.model"))
        # 语义角色标注模型
        if labeller:
            self.labeller = SementicRoleLabeller()
            self.labeller.load(os.path.join(self.LTP_DATA_DIR, 'pisrl_win.model'))

    def create_stopwordslist(self, file):
        """
        使用停用词表
        :param file: 停用词典路径
        :return:
        """
        self.stopwords_list = [line.strip() for line in open(file, encoding='UTF-8').readlines()]

    def cut_stopwords(self, words, not_cut_list):
        """
        去停用词
        :param words: list, 待处理文本数据（分词后），
        :param not_cut_list: list, 停用词典
        :return:
        """
        if not self.stopwords_list:
            return words
        new_words = []
        for word in words:
            if word not in self.stopwords_list or word in not_cut_list:
                new_words.append(word)
        return new_words

    def load_dict(self, dict_dir):
        """
        使用自定义分词词典
        :param dict_dir: 自定义分词词典路径
        :return:
        """
        if self.segmentor:
            self.segmentor.release()
        self.segmentor = Segmentor()
        self.segmentor.load_with_lexicon(os.path.join(self.LTP_DATA_DIR, "cws.model"), dict_dir)

    def pretreating(self, text):
        """
        微博文本预处理，包括过滤无用元素和数据切分
        :param text: str, 待处理文本
        :return: tuple, (标题: str, 正文: str, hashtag: list)
        """
        text = re.sub('http.*', '', text)  # 过滤URL链接
        text = re.sub('@([\S]*)\s', '', text)  # 过滤@用户
        try:
            title = re.search('【(.*)】', text).group(1)  # 识别标题
            title = re.sub('#', '', title)
        except:
            title = ''
        hashtag = []
        tags = re.finditer('#([^#]+)#', text)  # 识别hashtag
        for tag in tags:
            if tag[0]:
                hashtag.append(tag[1])

        body = re.sub('【.*】', '', text)
        body = re.sub('#([^#]+)#', '', body)
        return title, body, hashtag

    def is_same_entity(self, list1, list2):
        """
        判断是否为同一命名实体
        """
        if not list1 or not list2:
            return None
        list = []
        len1 = len(list1)
        len2 = len(list2)
        label1 = [0 for i in range(len1)]
        label2 = [0 for i in range(len2)]
        cursor1 = cursor2 = 0
        flag = -1

        def contain(word1, word2):
            if word1 in word2:
                return -1
            elif word2 in word1:
                return 1
            else:
                return 0

        while cursor1 < len1 and cursor2 < len2:
            if flag == -1:
                for i in range(cursor2, len2):
                    temp = contain(list1[cursor1], list2[i])
                    if temp:
                        flag = temp
                        for j in range(cursor2, i):
                            if label2[j] == 0:
                                list.append(list2[j])
                        cursor2 = i
                        if temp < 0:
                            if label2[cursor2] == 0:
                                list.append(list2[cursor2])
                            label1[cursor1] = label2[i] = 1
                            cursor1 += 1
                        else:
                            if label1[cursor1] == 0:
                                list.append(list1[cursor1])
                            label1[cursor1] = label2[i] = 1
                            cursor2 += 1
                        if i == len2 - 1:
                            i += 1
                        break
                if i == len2 - 1:
                    list.append(list1[cursor1])
                    cursor1 += 1
                    continue
            else:
                for i in range(cursor1, len1):
                    temp = contain(list1[i], list2[cursor2])
                    if temp:
                        flag = temp
                        for j in range(cursor1, i):
                            if label1[j] == 0:
                                list.append(list1[j])
                        cursor1 = i
                        if temp < 0:
                            if label2[cursor2] == 0:
                                list.append(list2[cursor2])
                            label1[i] = label2[cursor2] = 1
                            cursor1 += 1
                        else:
                            if label1[cursor1] == 0:
                                list.append(list1[cursor1])
                            label1[i] = label2[cursor2] = 1
                            cursor2 += 1
                        if i == len1 - 1:
                            i += 1
                        break
                if i == len1 - 1:
                    list.append(list2[cursor2])
                    cursor2 += 1
                    continue
        if label1[0] == label2[0] == 0 or label1[-1] == label2[-1] == 0:
            return None

        def change_above_2(list):
            count = 0
            j = list[0]
            for i in range(1, len(list)):
                if list[i] != j:
                    j = list[i]
                    count += 1
                if count >= 2:
                    return True
            return False

        if change_above_2(label1) and change_above_2(label2):
            return None

        return list

    def netag_list_update(self, list, new_item):
        """
        命名实体列表更新
        """
        for _tuple in list:
            item = _tuple[0]
            list_temp = self.is_same_entity(item, new_item[0])
            if list_temp:
                _tuple[0] = list_temp
                _tuple[1] += new_item[1]
                list = sorted(list, key=lambda item: item[1], reverse=True)
                return list

        list.append(new_item)
        list = sorted(list, key=lambda item: item[1], reverse=True)
        return list

    def netag_dict_merge(self, dict1, dict2):
        """
        命名实体列表合并
        """
        for key in dict1:
            list1 = dict1[key]
            list2 = dict2[key]
            for item in list2:
                list1 = self.netag_list_update(list1, item)
            dict1[key] = list1
        return dict1

    def get_time(self, sentence):
        """
        从文本中获取时间
        """
        r = re.finditer(r'(\d+年)?(\d+月)?(\d+日)?', sentence)
        list = []
        for time in r:
            if time[0]:
                temp = [time[i] for i in range(1, 4) if time[i]]
                list.append([temp, 1])
        return list

    def sentence_parser(self, sentence):
        """
        句子解析，包括分词，词性标注，命名实体识别，依存句法关系分析，语义角色分析
        :param sentence:
        :return: tuple, (分词输出: list, 词性标注输出: list, 命名实体输出: dict, 依存句法关系输出: list, 语义角色分析输出)
        """
        # 分词
        words = None
        if self.segmentor:
            words = self.segmentor.segment(sentence)
            words = list(words)
            # print(type(words), ': ', list(words))

        # 词性标注
        postags = None
        if self.postagger:
            postags = self.postagger.postag(words)
            # print(type(postags), ': ', list(postags))
            postags = list(postags)

        # 命名实体识别
        netag_list = None
        entity_word_list = []
        if self.recognizer:
            netags = self.recognizer.recognize(words, postags)
            # print(type(netags), ': ', list(netags))
            netag = []
            netag_list = {
                'Time': [],
                'Nh': [],
                'Ni': [],
                'Ns': []
            }
            for item in self.get_time(sentence):
                self.netag_list_update(netag_list['Time'], item)
            for i in range(len(netags)):
                if netags[i] == 'O':
                    continue
                else:
                    label1 = re.search('(.*)-(.*)', netags[i]).group(1)
                    label2 = re.search('(.*)-(.*)', netags[i]).group(2)
                    if words[i] not in entity_word_list:
                        entity_word_list.append(words[i])
                    netag.append(words[i])
                    if label1 == 'S' or label1 == 'E':
                        self.netag_list_update(netag_list[label2], [netag, 1])
                        netag = []
        words = self.cut_stopwords(words, entity_word_list)

        # 依存句法分析
        arcs_list = None
        if self.parser:
            arcs = self.parser.parse(words, postags)
            # print(type(arcs), ': ', "\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
            arcs_list = [(arc.head, arc.relation) for arc in arcs]

        # 语义角色分析
        roles = None
        if self.labeller:
            roles = self.labeller.label(words, postags, arcs)
            for role in roles:
                print(words[role.index], "".join(
                    ["%s:%s" % (arg.name, ''.join(words[arg.range.start:arg.range.end + 1])) for arg in
                     role.arguments]))

        return words, postags, netag_list, arcs_list, roles

    def text_parser(self, text):
        """
        微博文本解析
        :param text:
        :return: tuple, (标题（分词后）:list， 正文（分词后）: list，hashtag: list, 命名实体: dict)
        """
        _, _, entity, _, _ = self.sentence_parser(text)
        title, body, hashtag = self.pretreating(text)
        body = [sentence for sentence in re.split(r'[？?！!。；;：:\n\r]', body) if sentence]
        parser = self.sentence_parser(' '.join(body))
        body = parser[0]

        if title:
            parser = self.sentence_parser(title)
            title = parser[0]
        else:
            title = []

        if hashtag:
            parser = self.sentence_parser(' '.join(hashtag))
            hashtag = parser[0]
        else:
            hashtag = []
        return title, body, hashtag, entity


if __name__ == '__main__':
    text1 = '#雅安阳春大事记# #成都七中实验学校食品安全问题# 关于网络公告成都7中事件的涉事机构也承包了“雅安中学”的食堂。经过雅安市教育局联合市场监督管理局迅速对雅安中学（大兴校区）食堂进行现场检查，经过检查，食堂管理规范，未发现有过期发霉变质食品。'
    text2 = '【#成都七中实验学校#食品质量事件更新情况通报】@金温江 刚刚发布第三条事件相关的情况通报：温江区公安分局目前正在对掌握的成都七中实验学校负责食品安全的8名责任人开展全面深入的调查。区市场监管局对投诉反映的19个批次的食材进行了抽样，对所有冻库及库房内食材进行了查封，对新进食材进行全程监管。区市场监管局、区教育局举一反三，已组织开展全区大中小学和幼儿园食堂食品安全的专项检查，切实保障学生的身体健康。温江区委、区政府将依法依规对成都七中实验学校食品安全问题进行认真彻查，严肃处理相关责任人，及时公布调查处理结果。#成都315曝光台##成都爆料#'
    text3 = '【#成都七中实验学校#食品质量事件更新情况通报】'
    ltp = Ltp(3)
    ltp.create_stopwordslist('E:\Python\workspace\TDTSystem\data\chinesestopword.txt')
    title, body, hashtag, entity = ltp.text_parser(text1)

    print(text1)
    print(ltp.text_parser(text1))

    # text1 = '【广西检察机关加强公益保护督促做好非洲猪瘟疫情防控】近日，广西壮族自治区北海市发生非洲猪瘟疫情。北海市海城区检察院从捍卫舌尖安全和维护生态环境两方面发力，实地调查取证、摸排公益诉讼案件线索，并督促相关部门采取有效措施，防止病猪死猪流向市场，危害市民食品安全。'
    # text2 = '【福建又一家85°C被查！】1967年8月15日中秋、国庆双节越来越近，为守护食品安全，福建泉州南安市场监督管理局开展节前食品安全例行检查。昨天（8月15日）上午，南安水头市监所对辖区10多家面包、蛋糕烘焙店的现场制作条件、食品原材料存储条件和员工健康证、进货查验制度落实情况等进行检查。执法人员发现，85℃水头店存在部分食品原材料随意摆放在地上的情况，执法人员当即要求商家进行整改。同日，泉州另一家85°C店也被曝出有问题。南安市场监督管理局执法人员在检查85℃南安溪美店时，发现该店裱花间更衣室的洗手池未正常使用、裱花间内紫外线消毒灯无法正常使用、食品添加剂未进行专人管理，且储存柜未上锁等问题，执法人员对上述行为当场开具执法文书。'
    # #title, sents = ltp.text_segment(text)
    # netags1 = ltp.sentence_parser(text1)[2]
    # netags2 = ltp.sentence_parser(text2)[2]
    # print(netags1)
    # print(netags2)
    #
    # list1 = [[["四川", "成", 'd', "都", "温江区"], 26]]
    # item = [["成都市", "韶关", "温江", "监察局",'长'], 15]
    # print(ltp.netag_list_update(list1, item))
    # print(netags1)
    # print(ltp.netag_dict_merge(netags1, netags1))
