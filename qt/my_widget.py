# -*- coding: utf-8 -*-

import re
import sys

from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from bson import ObjectId

from mongo import MongoDB
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from cmath import sqrt
import numpy as np
from setting import *

class MyText(QtWidgets.QTextBrowser):

    def __init__(self, parent=None, ltp=None, id=None, topic_collection=None, weibo_collection=None):
        super().__init__(parent)
        self.setStyleSheet('font:12px;border:none')
        self.setMinimumHeight(100)
        self.setMaximumHeight(100)
        if ltp:
            self.ltp = ltp
        if topic_collection:
            self.topic_collection = topic_collection
        if weibo_collection:
            self.weibo_collection = weibo_collection
        if id:
            self.getData(id)

    def getData(self, id):
        """
        获取话题信息
        :param id: 话题id
        :return:
        """
        topic = self.topic_collection.find_one({'_id': id})
        self.topic = topic
        count = 0
        text = ''
        time = ''
        for id in topic['text_id_list']:
            weibo = self.weibo_collection.find_one({'id': id})
            if weibo['comment_count'] > count:
                count = weibo['comment_count']
                text = weibo['content']
                time = weibo['posted_at']
        title, body, _ = self.ltp.pretreating(text)

        self.insertHtml('<h2 style="color:red">' + title + '<br>')
        self.insertHtml('<h4 style="color:grey">' + time[0:10] + '</h4>')

        try:
            if topic['entity']['Ns'][0][1] >= topic['text_num'] / 2:
                self.insertHtml('<h4 style="color:grey">&nbsp;&nbsp;&nbsp;' + ''.join(topic['entity']['Ns'][0][0]))
        except:
            pass

        self.insertHtml('<br>')
        body = body[0:100] + '...'
        self.insertHtml('<h3>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + body + '</p>')
        # self.insertPlainText('微博数：' + str(topic['text_num']) + '\n')
        # self.insertPlainText('热度：' + str(round(topic['heat'], 2)) + '\n')


class MyButton(QtWidgets.QPushButton):
    def __init__(self, id, parent=None, text=None):
        super().__init__(parent, text=text)
        self.parent = parent
        self.id = id

    def mouseReleaseEvent(self, *args, **kwargs):
        if self.text() == '舆情分析':
            print(self.id)
            self.parent.getDetail(self.id)
        elif self.text() == '话题追踪':
            self.parent.topicTrade(self.id)


class MyLabel(QtWidgets.QLabel):
    """
    自制QLabel，模拟QTabWidget功能，但只存在一个tab，每次切换将重绘tab
    """
    def __init__(self, parent, mainwindow, id=None):
        super().__init__(parent)
        self.mainwindow = mainwindow
        self.id = None
        self.isSelect = False
        if id:
            self.id = id

    def setId(self, id):
        self.id = id

    def Select(self, ifSelect):
        if ifSelect:
            self.isSelect = True
            self.setFont(QFont("Microsoft YaHei", 15, 75))
            self.setStyleSheet("color:red;")
        else:
            self.isSelect = False
            self.setFont(QFont("Microsoft YaHei", 13, 63))
            self.setStyleSheet("color:black;")

    def mousePressEvent(self, QMouseEvent):
        if self.isSelect:
            return
        if QMouseEvent.button() == Qt.LeftButton:
            self.Select(True)
            if self.text() == '地理分布':
                self.mainwindow.label_2.Select(False)
                self.mainwindow.label_3.Select(False)
                self.mainwindow.echarts.map()
            elif self.text() == '热词':
                self.mainwindow.label.Select(False)
                self.mainwindow.label_3.Select(False)
                self.mainwindow.echarts.wordcloud()
            elif self.text() == '时间曲线':
                self.mainwindow.label.Select(False)
                self.mainwindow.label_2.Select(False)
                self.mainwindow.echarts.bar()
            elif self.text() == '话题传播':
                self.mainwindow.label_2.Select(False)
                if not self.id:
                    return
                self.mainwindow.echarts.geo(self.id)
            elif self.text() == '微博转发关系图':
                self.mainwindow.label.Select(False)
                if not self.id:
                    return
                self.mainwindow.echarts.graph(self.id)


class MplCanvas(QtWidgets.QWidget):
    """
    画布，舆情分析模块中展示：话题热度时间曲线、话题情感倾向饼图
    """
    def __init__(self, parent, id):
        super().__init__(parent)
        self.id = id
        client = MongoDB.get_client()
        db = client[MONGO_DB]
        self.topic_collection = db['topic']
        self.weibo_collection = db['weibo']
        self.comment_collection = db['comment']
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.create_figure(self.create_heatline())
        self.create_figure(self.create_emotion_pie())
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

    def create_figure(self, fig):
        canvas = FigureCanvasQTAgg(fig)
        self.horizontalLayout.addWidget(canvas)
        return canvas

    def create_heatline(self):
        """
        绘制热度时间曲线
        :return:
        """
        figure = plt.figure(figsize=(6, 4), dpi=80, frameon=True)
        topic = self.topic_collection.find_one({'_id': ObjectId(self.id)})
        weibo_id_list = topic['text_id_list']
        timelist = []
        heat = []

        for weibo_id in weibo_id_list:
            weibo = self.weibo_collection.find_one({'id': weibo_id})
            dateint = re.match(r'(\d+)-(\d+)-(\d+)', weibo['posted_at']).group()
            heat_score = weibo['comment_count'] + sqrt(weibo['forward_count'] + weibo['like_count'])
            if dateint in timelist:
                index = timelist.index(dateint)
                heat[index] += heat_score
            else:
                timelist.append(dateint)
                heat.append(heat_score)
        fig1 = plt.subplot(1, 1, 1)
        N = len(timelist)
        ind = np.arange(N)

        def format_date(x, pos=None):
            i = np.clip(int(x + 0.5), 0, N - 1)
            return timelist[i]

        fig1.plot(ind, heat, '.-')
        fig1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
        fig1.set_title('话题热度变化')
        figure.autofmt_xdate()

        return figure

    def create_emotion_pie(self):
        """
        绘制情感倾向饼图
        :return:
        """
        figure = plt.figure(figsize=(6, 4), dpi=80, frameon=True)
        data = [0, 0, 0]
        topic = self.topic_collection.find_one({'_id': ObjectId(self.id)})

        # if 'score' not in topic or not topic['score']:
        for weibo_id in topic['text_id_list']:
            if MONGO_DB == 'weibo':
                comments = self.comment_collection.find({'id': weibo_id})
            else:
                mid = MongoDB.get_client()[MONGO_DB]['mid'].find_one({'id': weibo_id})
                if not mid:
                    continue
                comments = self.comment_collection.find({'mid': mid['mid']})

            for comment in comments:
                if not comment['content'].strip():
                    continue
                if 'score' not in comment or not comment['score']:
                    continue
                score = comment['score']
                if score[0] - score[1] > 2:
                    data[0] += 1
                elif score[0] - score[1] < 0:
                    data[1] += 1
                else:
                    data[2] += 1
        topic['score'] = data
        self.topic_collection.update_one({'_id': topic['_id']}, {'$set': topic}, True)
        # else:
        #     data = topic['score']

        try:
            data[0] += data[2] * 0.3 * data[0] / (data[0] + data[1])
            data[1] += data[2] * 0.3 * data[1] / (data[0] + data[1])
            data[2] *= 0.7
        except:
            pass

        labels = ['积极', '消极', '其它']
        colors = ['r', 'b', 'y']
        fig1 = plt.subplot(1, 1, 1)
        plt.xlim(0, 4)
        plt.ylim(0, 4)
        fig1.pie(x=data, labels=labels, colors=colors, autopct='%.1f%%')
        fig1.set_title('话题舆情倾向度')
        plt.xticks(())
        plt.yticks(())

        return figure
