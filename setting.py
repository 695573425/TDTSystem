# -*- coding: utf-8 -*-

import os

# 项目路劲
dirname, _ = os.path.split(os.path.abspath(__file__))
dirname = dirname.replace('\\', '/')  

# ltp数据文件夹路径
DEFAULT_LTP_DATA_DIR = dirname + '/ltp/ltp_data_v3.4.0/'

# 停用词典路径
STOPWORDS_DIR = dirname + '/data/chinesestopword.txt'


ALL_DICT_PATH = dirname + '/emotion/dict/allwords.txt'

# 正面情感词典路径
POSTIVE_DICT_PATH = dirname + '/emotion/dict/positive.txt'

# 负面情感词典路径
NEGATIVE_DICT_PATH = dirname + '/emotion/dict/negative.txt'

# 否定词典路径
DENY_DICT_PATH = dirname + '/emotion/dict/deny.txt'

# 程度副词词典路径
DEGREE_DICT_PATH = dirname + '/emotion/dict/degree.txt'

#  程度副词权重
DEGREE_SCORE = (
    (69, 142, 180),
    (2.5, 2.0, 1.5, 0.5)
)

#  mongoDB数据库配置
MONGO_URI = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'weibo1'