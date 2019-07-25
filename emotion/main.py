import sys

from emotion import EmotionAnalysis

sys.path.append('E:\Python\workspace\TDTSystem')
from ltp.ltp import Ltp
from setting import *
from mongo import MongoDB
if __name__ == '__main__':
    ltp = Ltp(4)
    ltp.load_dict(ALL_DICT_PATH)
    analyzer = EmotionAnalysis(ltp)


    comment = MongoDB.get_client()['weibo']['comment']
    count = 0

    for data in comment.find():
        count += 1
        print(count)
        if 'score' in data and data['score']:
            continue
        content = data['content'].strip()
        if not content:
            continue
        data['score'] = analyzer.sent_sentiment_score(data['content'].strip())
        comment.update_one({'_id': data['_id']}, {'$set': data}, True)