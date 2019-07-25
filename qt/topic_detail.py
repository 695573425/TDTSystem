# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tab.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

# sys.path.append('E:\Python\workspace\TDTSystem')

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QHeaderView, QWidget
from bson import ObjectId

from emotion.emotion import EmotionAnalysis
from ltp.ltp import Ltp
from setting import *
from mongo import MongoDB
from qt.my_widget import MplCanvas, MyButton



class Ui_Topic_Detail(QtWidgets.QWidget):
    """
    舆情分析模块
    """

    def __init__(self, id, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ltp = Ltp.get_object()
        client = MongoDB.get_client()
        db = client[MONGO_DB]
        self.topic_collection = db['topic']
        self.weibo_collection = db['weibo']
        self.comment_collection = db['comment']
        self.id = id
        self.setupUi()

    def setupUi(self):
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        # 显示话题详细信息
        self.textBrowser = QtWidgets.QTextBrowser(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.textBrowser.setSizePolicy(sizePolicy)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_2.addWidget(self.textBrowser)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox.setMaximumHeight(300)
        self.groupBox_2 = QtWidgets.QGroupBox(self)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.groupBox_3 = QtWidgets.QGroupBox(self.groupBox_2)
        self.groupBox_3.setMaximumHeight(50)
        self.hLayout_groupBox_3 = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.button = MyButton(self.id, self.parent, '话题追踪')
        self.button.setMaximumWidth(100)
        self.button_2 = QtWidgets.QPushButton(self.groupBox_3)
        self.button_2.setMaximumWidth(100)
        self.button_2.clicked.connect(self.sentiment_analysize)
        self.progressBar = QtWidgets.QProgressBar(self.groupBox_3)
        self.progressBar.setVisible(False)
        self.progressBar.setMaximum(100)
        self.hLayout_groupBox_3.addWidget(self.button)
        self.hLayout_groupBox_3.addWidget(self.button_2)
        self.hLayout_groupBox_3.addWidget(self.progressBar)
        self.verticalLayout_3.addWidget(self.groupBox_3)

        # 绘制画布，展示话题热度时间曲线和情感分析饼图
        self.mplCanvas = MplCanvas(self.groupBox_2, self.id)
        self.mplCanvas.setObjectName("mplCanvas")
        self.mplCanvas.setMinimumSize(500, 180)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.mplCanvas.setSizePolicy(sizePolicy)
        self.verticalLayout_3.addWidget(self.mplCanvas)
        self.verticalLayout.addWidget(self.groupBox_2)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    class AnalysizeThread(QThread):
        """
        情感分析线程
        """
        count = pyqtSignal(int)
        stop = pyqtSignal(bool)

        def __init__(self, id):
            super().__init__()
            self.id = id

        def run(self):
            ltp = Ltp.get_object2()
            ltp.load_dict(ALL_DICT_PATH)
            analyzer = EmotionAnalysis(ltp)

            topic_collection = MongoDB.get_client()[MONGO_DB]['topic']
            comment_collection = MongoDB.get_client()[MONGO_DB]['comment']
            topic = topic_collection.find_one({'_id': ObjectId(self.id)})
            count1 = 0

            for weibo_id in topic['text_id_list']:
                if MONGO_DB == 'weibo':
                    comments = comment_collection.find({'id': weibo_id})
                else:
                    data = MongoDB.get_client()[MONGO_DB]['mid'].find_one({'id': weibo_id})
                    if not data:
                        continue
                    comments = comment_collection.find({'mid': data['mid']})
                for data in comments:
                    if 'score' in data and data['score']:
                        continue
                    content = data['content'].strip()
                    if not content:
                        continue
                    data['score'] = analyzer.sent_sentiment_score(data['content'].strip())
                    comment_collection.update_one({'_id': data['_id']}, {'$set': data}, True)
                count1 += 1
                self.count.emit(round((count1 / topic['text_num']) * 100))
            self.stop.emit(True)

    def sentiment_analysize(self):
        """
        情感分析
        :return:
        """
        self.progressBar.setVisible(True)
        self.analysize_thread = self.AnalysizeThread(self.id)

        def setProgressBar(count):
            self.progressBar.setProperty("value", count)

        def stop(flag):
            self.progressBar.setVisible(False)

        self.analysize_thread.count.connect(setProgressBar)
        self.analysize_thread.stop.connect(stop)
        self.analysize_thread.start()



    def retranslateUi(self, tab):
        _translate = QtCore.QCoreApplication.translate
        tab.setWindowTitle(_translate("tab", "Form"))
        self.groupBox.setTitle(_translate("tab", "话题信息"))
        self.groupBox_2.setTitle(_translate("tab", "舆情分析"))
        self.groupBox_3.setStyleSheet('QGroupBox{border:none}')
        self.button_2.setText(_translate("tab", "情感分析"))
        self.textBrowser.setStyleSheet('border:none')
        topic = self.topic_collection.find_one({'_id': ObjectId(self.id)})
        try:
            self.textBrowser.insertPlainText('事件时间：' + topic['central_time'][0:10] + '\n')
        except:
            pass
        try:
            if topic['entity']['Ns'][0][1] >= topic['text_num'] / 2:
                self.textBrowser.insertPlainText('地点：' + ''.join(topic['entity']['Ns'][0][0]) + '\n')
        except:
            pass
        try:
            if topic['entity']['Ni'][0][1] >= topic['text_num'] / 2:
                self.textBrowser.insertPlainText('机构：' + ''.join(topic['entity']['Ni'][0][0]) + '\n')
        except:
            pass
        try:
            if topic['entity']['Nh'][0][1] >= topic['text_num'] / 2:
                self.textBrowser.insertPlainText('相关人物：' + ''.join(topic['entity']['Nh'][0][0]) + '\n')
        except:
            pass
        count = 0
        text = ''
        for id in topic['text_id_list']:
            weibo = self.weibo_collection.find_one({'id': id})
            if weibo['comment_count'] > count:
                count = weibo['comment_count']
                text = weibo['content']
        title, body, _ = self.ltp.pretreating(text)
        if title:
            self.textBrowser.insertPlainText('概要：' + title + '\n')
        self.textBrowser.insertPlainText('报道：' + body + '\n')
        self.textBrowser.insertPlainText('微博数：' + str(topic['text_num']) + '\n')
        self.textBrowser.insertPlainText('热度：' + str(round(topic['heat'], 2)) + '\n')
