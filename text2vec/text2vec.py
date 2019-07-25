# -*- coding: utf-8 -*-

# 文本提取特征向量
class Text2Vec:
    model = None

    @staticmethod
    def get_object():
        if Text2Vec.model:
            print('Text2Vec Ready!')
            return Text2Vec.model
        else:
            print('Text2Vec init!')
            Text2Vec.model = Text2Vec()
            return Text2Vec.model

    def get_weight(self, text):
        """
        正文，标题，hashtag权重
       :param text:list, text = [标题， 正文， hashtag]
        :return:
        """
        weight = [0.3, 0.2, 0.5]
        if not text[0]:
            weight[0] = 0
            weight[1] += 0.1
            weight[2] += 0.2
        if not text[2]:
            if weight[0]:
                weight[0] += (weight[2] * 0.2)
                weight[1] += (weight[2] * 0.1)
            else:
                weight[1] += weight[2]
            weight[2] = 0
        return weight

    def text2dict(self, text):
        """
        文本体征提取，计算特征向量
        :param text: str
        :return: dict
        """
        _dict = {}
        weight = self.get_weight(text)
        for word in text[0]:
            word = word.replace('.', '_')
            if word not in _dict:
                _dict[word] = 0.0
            _dict[word] += weight[0]
        for word in text[1]:
            word = word.replace('.', '_')
            if word not in _dict:
                _dict[word] = 0.0
            _dict[word] += weight[1]
        for word in text[2]:
            word = word.replace('.', '_')
            if word not in _dict:
                _dict[word] = 0.0
            _dict[word] += weight[2]

        return _dict

    def cosine(self, vector1, vector2):
        """计算余弦相似度
        """
        assert len(vector1) == len(vector2)
        dot_product = 0.0
        norm1 = 0.0
        norm2 = 0.0
        for x1, x2 in zip(vector1, vector2):
            dot_product += x1 * x2
            norm1 += x1 ** 2
            norm2 += x2 ** 2
        if norm1 == 0 or norm2 == 0:
            return 0.0
        else:
            return dot_product / ((norm1 ** 0.5) * (norm2 ** 0.5))

    def similarity(self, dict1, dict2):
        """
        计算文本相似度
        :param dict1:
        :param dict2:
        :return:
        """
        if isinstance(dict1, list):
            dict1 = self.text2dict(dict1)
        if isinstance(dict2, list):
            dict2 = self.text2dict(dict2)
        words = []
        vector1 = []
        vector2 = []
        for word in dict1:
            words.append(word)
            vector1.append(dict1[word])
        for word in words:
            if word not in dict2:
                vector2.append(0.0)
            else:
                vector2.append(dict2[word])
        for word in dict2:
            if word not in words:
                words.append(word)
                vector2.append(dict2[word])
        for _ in range(len(vector1), len(words)):
            vector1.append(0.0)
        return self.cosine(vector1, vector2)
