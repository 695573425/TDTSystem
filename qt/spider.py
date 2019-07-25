# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'spider.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!
import os
import time
import pymongo

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QTime
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMessageBox
from mongo import MongoDB
from CookiesPool.run import Cookies
from qt.topic_list import Ui_Topic_List
from text2vec.text2vec import Text2Vec
from weibosearch.run import Spider
from ltp.ltp import Ltp
from tdt.tdt import Tdt
from setting import *

class Ui_Spider(QtWidgets.QWidget):
    """
    信息采集模块
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = MongoDB.get_client()[MONGO_DB]
        self.parent = parent
        self.setupUi()

    def setupUi(self):


        self.vLayout = QtWidgets.QVBoxLayout(self)
        self.vLayout.setObjectName("vLayout")

        # Cookies配置
        self.groupBox = QtWidgets.QGroupBox(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.vLayout_grouBox = QtWidgets.QVBoxLayout(self.groupBox)
        self.cookies_intro = QtWidgets.QTextBrowser(self.groupBox)  # 简介
        self.cookies_intro.setObjectName('cookies_intro')
        self.cookies_intro.setMaximumHeight(60)
        self.vLayout_grouBox.addWidget(self.cookies_intro)
        self.groupBox_box = QtWidgets.QGroupBox(self.groupBox)
        self.hLayout_groupBox_box = QtWidgets.QHBoxLayout(self.groupBox_box)
        self.generator = QtWidgets.QCheckBox(self.groupBox_box)  # 产生器
        self.hLayout_groupBox_box.addWidget(self.generator)
        self.valid = QtWidgets.QCheckBox(self.groupBox_box)  # 验证器
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.valid.setSizePolicy(sizePolicy)
        self.hLayout_groupBox_box.addWidget(self.valid)
        self.api = QtWidgets.QCheckBox(self.groupBox_box)  # API接口
        self.api.setChecked(True)
        self.hLayout_groupBox_box.addWidget(self.api)
        self.vLayout_grouBox.addWidget(self.groupBox_box)
        self.vLayout.addWidget(self.groupBox)

        # 爬虫配置
        self.groupBox_2 = QtWidgets.QGroupBox(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")

        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.spider_intro = QtWidgets.QTextBrowser(self.groupBox_2)  # 简介
        self.spider_intro.setMaximumHeight(25)

        self.gridLayout.addWidget(self.spider_intro, 0, 0, 1, 3)

        # 输入微博爬虫检索关键词
        self.groupBox_keyword = QtWidgets.QGroupBox(self.groupBox_2)
        self.groupBox_keyword.setMinimumWidth(200)
        self.groupBox_keyword.setStyleSheet('QGroupBox{border:none}')
        self.hLayout_groupBox_keyword = QtWidgets.QHBoxLayout(self.groupBox_keyword)
        self.label_keyword = QtWidgets.QLabel(self.groupBox_keyword)
        self.lineEdit_keyword = QtWidgets.QLineEdit(self.groupBox_keyword)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hLayout_groupBox_keyword.addWidget(self.label_keyword)
        self.hLayout_groupBox_keyword.addWidget(self.lineEdit_keyword)
        self.hLayout_groupBox_keyword.addItem(spacerItem)
        self.gridLayout.addWidget(self.groupBox_keyword, 1, 0, 1, 1)

        # 输入微博爬取页码范围
        self.groupBox_page = QtWidgets.QGroupBox(self.groupBox_2)
        self.groupBox_page.setStyleSheet('QGroupBox{border:none}')
        self.groupBox_page.setMaximumWidth(200)
        self.hLayout_groupBox_page = QtWidgets.QHBoxLayout(self.groupBox_page)
        self.label_page = QtWidgets.QLabel(self.groupBox_page)
        self.label_page2 = QtWidgets.QLabel(self.groupBox_page)
        self.lineEdit_minPage = QtWidgets.QLineEdit(self.groupBox_page)
        self.lineEdit_maxPage = QtWidgets.QLineEdit(self.groupBox_page)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hLayout_groupBox_page.addWidget(self.label_page)
        self.hLayout_groupBox_page.addWidget(self.lineEdit_minPage)
        self.hLayout_groupBox_page.addWidget(self.label_page2)
        self.hLayout_groupBox_page.addWidget(self.lineEdit_maxPage)
        self.hLayout_groupBox_page.addItem(spacerItem)
        self.gridLayout.addWidget(self.groupBox_page, 1, 1, 1, 1)

        # 设定检索实时还是热门微博
        self.comboBox = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox.setMaximumWidth(60)
        self.comboBox.addItem('')
        self.comboBox.addItem('')
        self.gridLayout.addWidget(self.comboBox, 1, 2, 1, 1)

        # # 微博数据库选择
        # self.comboBox_weibo = QtWidgets.QComboBox(self.groupBox_2)
        # self.comboBox_weibo.setMaximumWidth(60)
        # self.comboBox_weibo.addItem('')
        # self.comboBox_weibo.addItem('')
        # self.gridLayout.addWidget(self.comboBox_weibo, 1, 3, 1, 1)
        #
        # # 话题数据库选择
        # self.comboBox_topic = QtWidgets.QComboBox(self.groupBox_2)
        # self.comboBox_topic.setMaximumWidth(60)
        # self.comboBox_topic.addItem('')
        # self.comboBox_topic.addItem('')
        # self.gridLayout.addWidget(self.comboBox_topic, 1, 4, 1, 1)

        # 采集评论
        self.if_get_comment = QtWidgets.QCheckBox(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.if_get_comment.setSizePolicy(sizePolicy)
        self.if_get_comment.setMinimumSize(QtCore.QSize(100, 0))
        self.gridLayout.addWidget(self.if_get_comment, 2, 0, 1, 1)

        # 设置定时器
        self.groupBox_time = QtWidgets.QGroupBox(self.groupBox_2)
        self.groupBox_time.setStyleSheet('QGroupBox{border:none}')
        self.hLayout_groupBox_time = QtWidgets.QHBoxLayout(self.groupBox_time)
        self.if_set_timer = QtWidgets.QCheckBox(self.groupBox_time)
        self.if_set_timer.setObjectName("if_set_timer")
        self.timer = QtWidgets.QTimeEdit(self.groupBox_time)
        self.timer.setEnabled(False)
        self.timer.setDisplayFormat('HH:mm:ss')
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.timer.setSizePolicy(sizePolicy)
        self.timer.setMaximumWidth(100)
        self.timer.setTime(QtCore.QTime(0, 0, 0))
        self.timer.setObjectName("timer")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hLayout_groupBox_time.addWidget(self.if_set_timer)
        self.hLayout_groupBox_time.addWidget(self.timer)
        self.hLayout_groupBox_time.addItem(spacerItem)
        self.gridLayout.addWidget(self.groupBox_time, 2, 1, 1, 1)

        # 爬虫结束自动关机
        self.autoShut = QtWidgets.QCheckBox(self.groupBox_2)
        self.gridLayout.addWidget(self.autoShut, 2, 2, 1, 1)

        # 开启关闭爬虫按钮
        self.startButton = QtWidgets.QPushButton(self.groupBox_2)
        self.startButton.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.startButton.setSizePolicy(sizePolicy)
        self.startButton.setMaximumSize(QtCore.QSize(100, 16777215))
        self.startButton.setObjectName("startButton")

        self.gridLayout.addWidget(self.startButton, 2, 3, 1, 1)
        self.stopButton = QtWidgets.QPushButton(self.groupBox_2)
        self.stopButton.setEnabled(False)
        self.stopButton.setMaximumSize(QtCore.QSize(100, 16777215))
        self.stopButton.setObjectName("stopButton")
        self.gridLayout.addWidget(self.stopButton, 2, 4, 1, 1)

        self.vLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(self)
        self.groupBox_3.setObjectName("groupBox_3")
        self.groupBox_4 = QtWidgets.QGroupBox(self.groupBox_3)
        self.hLayout_groupBox_4 = QtWidgets.QHBoxLayout(self.groupBox_4)

        self.vLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.vLayout_4.setObjectName("vLayout_4")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        # 微博、评论获取数标签
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.total_weibo = QtWidgets.QLabel(self.groupBox_3)
        self.total_weibo.setObjectName("total_weibo")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.total_weibo)
        self.label__4 = QtWidgets.QLabel(self.groupBox_3)
        self.label__4.setObjectName("label__4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label__4)
        self.total_comment = QtWidgets.QLabel(self.groupBox_3)
        self.total_comment.setObjectName("total_comment")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.total_comment)
        self.label_2 = QtWidgets.QLabel(self.groupBox_3)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.a_weibo = QtWidgets.QLabel(self.groupBox_3)
        self.a_weibo.setObjectName("a_weibo")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.a_weibo)
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.a_comment = QtWidgets.QLabel(self.groupBox_3)
        self.a_comment.setObjectName("a_comment")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.a_comment)
        self.hLayout_groupBox_4.addLayout(self.formLayout)

        # 话题检测进度条
        self.progressBar = QtWidgets.QProgressBar(self.groupBox_4)
        self.progressBar.setVisible(False)
        self.progressBar.setMaximum(self.db['weibo'].count())
        self.hLayout_groupBox_4.addWidget(self.progressBar)

        # 话题检测按钮
        self.tdtButton = QtWidgets.QPushButton(self.groupBox_4)
        self.tdtButton.setMaximumWidth(100)
        self.tdtButton.clicked.connect(self.topic_detect)
        self.hLayout_groupBox_4.addWidget(self.tdtButton)

        self.vLayout_4.addWidget(self.groupBox_4)

        # 文本框，显示爬虫微博信息
        self.terminal = QtWidgets.QTextBrowser(self.groupBox_3)
        self.terminal.setObjectName("terminal")
        self.vLayout_4.addWidget(self.terminal)
        self.vLayout.addWidget(self.groupBox_3)

        self.retranslateUi(self)
        self.if_set_timer.toggled['bool'].connect(self.timer.setEnabled)
        self.startButton.clicked.connect(self.startSpider)
        self.stopButton.clicked.connect(self.stopSpider)
        self.timer.timeChanged.connect(self.timing)
        self.destroyed.connect(self.stopSpider)


    def retranslateUi(self, Spider):
        Spider.setStyleSheet('font:15px')
        _translate = QtCore.QCoreApplication.translate
        Spider.setWindowTitle(_translate("Spider", "Form"))
        self.groupBox.setTitle(_translate("Spider", "Cookies"))
        self.cookies_intro.setText(_translate("Spider", "产生器：开启将动态为cookies池添加新cookie\n"
                                                        "验证器：开启将定时验证cookie是否有效，无效则从cookies池中删除\n"
                                                        "api接口：开启则为爬虫设置随机cookie"))
        self.cookies_intro.setStyleSheet('border:none')
        self.groupBox_box.setStyleSheet('border:none')
        self.generator.setText(_translate("Spider", "产生器"))
        self.valid.setText(_translate("Spider", "验证器"))
        self.api.setText(_translate("Spider", "api接口"))

        self.groupBox_2.setTitle(_translate("Spider", "Spider"))

        self.spider_intro.setText(_translate("Spider", "这是爬虫"))
        self.spider_intro.setStyleSheet('border:none;font:15px')
        self.label_keyword.setText(_translate("Spider", "关键词："))
        self.label_page.setText(_translate("Spider", "页码"))
        self.label_page2.setText(_translate("Spider", "-"))
        self.comboBox.setItemText(0, _translate("Spider", "热门"))
        self.comboBox.setItemText(1, _translate("Spider", "实时"))
        self.if_get_comment.setText(_translate("Spider", "采集评论"))
        self.if_set_timer.setText(_translate("Spider", "启用定时器"))
        self.autoShut.setText(_translate('Spider', '爬虫结束后自动关机            '))
        self.startButton.setText(_translate("Spider", "开始"))
        self.stopButton.setText(_translate("Spider", "停止"))
        self.groupBox_3.setTitle(_translate("Spider", ""))
        self.groupBox_4.setStyleSheet('QGroupBox{border:none}')
        self.label_5.setText(_translate("Spider", "总微博数："))
        self.label__4.setText(_translate("Spider", "总评论数："))
        self.label_2.setText(_translate("Spider", "本次获取微博数："))
        self.a_weibo.setText(_translate("Spider", "0"))
        self.label_4.setText(_translate("Spider", "本次获取评论数："))
        self.tdtButton.setText(_translate("Spider", "话题检测"))
        self.a_comment.setText(_translate("Spider", "0"))
        self.total_weibo.setText(_translate("Spider", str(self.db['weibo'].count())))
        self.total_comment.setText(_translate("Spider", str(self.db['comment'].count())))

    class TimeThread(QThread):
        """
        定时器线程，实现计时功能
        """
        def __init__(self, timer):
            super().__init__()
            self.timer = timer

        def run(self):
            while True:
                self.timer.setTime(self.timer.time().addSecs(-1))
                time.sleep(1)

    class SpiderThread(QThread):
        """
        爬虫线程
        """
        count = pyqtSignal(int)
        log = pyqtSignal(str)

        def __init__(self, spider, timer=None):
            super().__init__()
            self.spider = spider
            self.timer = timer

        def run(self):
            while self.spider:
                self.count.emit(self.spider.count.value)
                self.log.emit(self.spider.q.get())
                time.sleep(0.1)

    def timing(self):
        if self.timer.time() == QTime(0, 0, 0):
            self.stopSpider()

    def startSpider(self):
        """
        开启爬虫
        :return:
        """
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.generator.setEnabled(False)
        self.valid.setEnabled(False)
        self.api.setEnabled(False)
        self.lineEdit_keyword.setEnabled(False)
        self.lineEdit_minPage.setEnabled(False)
        self.lineEdit_maxPage.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.if_get_comment.setEnabled(False)
        self.if_set_timer.setEnabled(False)
        self.timer.setEnabled(False)
        self.terminal.setText('')
        Cookies.start(self.generator.isChecked(), self.valid.isChecked(), self.api.isChecked())
        if self.api.isChecked():
            if self.if_get_comment.isChecked():
                self.spider = Spider('comment')
            else:
                opts = ''
                opts += ' -a keyword=' + self.lineEdit_keyword.text()
                opts += ' -a start_page=' + self.lineEdit_minPage.text()
                opts += ' -a end_page=' + self.lineEdit_maxPage.text()
                if self.comboBox.currentIndex() == 0:
                    opts += ' -a sort=hot'
                else:
                    opts += ' -a sort=time'
                self.spider = Spider('weibo', opts)
            self.spider.start()
            self.spiderThread = self.SpiderThread(self.spider)

            if self.if_set_timer.isChecked():
                self.timeThread = self.TimeThread(self.timer)
                self.timeThread.start()

            def setLabel(count):
                if count == -1:
                    self.stopSpider()
                    return
                if self.if_get_comment.isChecked():
                    self.a_comment.setText(str(count))
                    self.total_comment.setText(str(self.db['comment'].count()))
                else:
                    self.a_weibo.setText(str(count))
                    self.total_weibo.setText(str(self.db['weibo'].count()))

            def insertLog(log):
                self.terminal.insertPlainText(log)
                self.terminal.moveCursor(QTextCursor.End)

            self.spiderThread.count.connect(setLabel)
            self.spiderThread.log.connect(insertLog)
            self.spiderThread.start()

            self.terminal.insertPlainText('开始运行微博爬虫\r\n')

    def stopSpider(self):
        """
        关闭爬虫
        :return:
        """
        if hasattr(self, 'spider') and self.spider:
            self.spider.stop()
            self.spiderThread.terminate()
            if hasattr(self, 'timeThread') and self.timeThread:
                self.timeThread.terminate()
            self.spider = None
            Cookies.stop()
            if self.autoShut.isChecked():
                os.system('shutdown /f /s /t 0')
            QMessageBox.information(self, "消息", "爬虫结束！", QMessageBox.Yes)
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.generator.setEnabled(True)
        self.valid.setEnabled(True)
        self.api.setEnabled(True)
        self.lineEdit_keyword.setEnabled(True)
        self.lineEdit_minPage.setEnabled(True)
        self.lineEdit_maxPage.setEnabled(True)
        self.comboBox.setEnabled(True)
        self.if_get_comment.setEnabled(True)
        self.if_set_timer.setEnabled(True)
        self.timer.setEnabled(True)

    class SinglePassThread(QThread):
        """
        话题检测线程
        """
        count = pyqtSignal(int)
        stop = pyqtSignal(bool)

        def __init__(self):
            super().__init__()
            self.stop.emit(False)

        def run(self):
            ltp = Ltp.get_object()
            tdt = Tdt.get_object()
            model = Text2Vec.get_object()
            weibo_collection = MongoDB.get_client()[MONGO_DB]['weibo']
            count1 = 0
            weibo_set = weibo_collection.find().sort('posted_at', pymongo.ASCENDING)
            for weibo in weibo_set:
                tdt.single_pass(weibo, 'topic', ltp, model)
                weibo_collection.update_one({'_id': weibo['_id']}, {'$set': weibo}, True)
                count1 += 1
                self.count.emit(count1)
            self.stop.emit(True)

    def topic_detect(self):
        """
        开始话题追踪
        :return:
        """
        self.progressBar.setVisible(True)
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.tdtButton.setEnabled(False)
        self.singlePassThread = self.SinglePassThread()

        def setProgressBar(count):
            self.progressBar.setProperty("value", count)

        def stop(flag):
            if flag:
                self.stop_topic_detect()

        self.singlePassThread.count.connect(setProgressBar)
        self.singlePassThread.stop.connect(stop)
        self.singlePassThread.start()

    def stop_topic_detect(self):
        """
        结束话题追踪
        :return:
        """
        QMessageBox.information(self, "消息", "话题检测结束！", QMessageBox.Yes)
        self.singlePassThread.terminate()
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(True)
        self.tdtButton.setEnabled(True)
        self.progressBar.setVisible(False)

        # self.parent.tab_2 = Ui_Topic_List(self.parent)