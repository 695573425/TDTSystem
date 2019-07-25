# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from qt.topic_list import Ui_Topic_List
from qt.topic_detail import Ui_Topic_Detail
from qt.topic_warn import Ui_Topic_Warn
from qt.topic_trade import Ui_Topic_Trade
from qt.spider import Ui_Spider

from mongo import MongoDB
from ltp.ltp import Ltp
from setting import dirname


class Ui_MainWindow(QMainWindow):
    """
    主界面，共5个模块：信息采集、话题分析、舆情分析、话题追踪、话题预警
    """
    def __init__(self):
        super().__init__()
        self.ltp = Ltp.get_object()

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(960, 600)
        self.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.tabBar().setObjectName("tabWidget_bar")
        self.tab = QtWidgets.QWidget()

        # 信息采集模块
        self.tab = Ui_Spider(self)
        self.tabWidget.addTab(self.tab, "")

        # 话题分析模块
        self.tab_2 = Ui_Topic_List(self)
        self.tabWidget.addTab(self.tab_2, "")

        # 舆情分析模块
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")

        # 话题追踪模块
        self.tab_4 = Ui_Topic_Trade(self)
        self.tabWidget.addTab(self.tab_4, "")

        # 话题预警模块
        self.tab_5 = Ui_Topic_Warn(self)
        self.tabWidget.addTab(self.tab_5, "")

        self.tab_3.setObjectName("topic_detail")
        self.verticalLayout_detail = QtWidgets.QVBoxLayout(self.tab_3)
        self.verticalLayout_detail.setObjectName("verticalLayout_detail")
        self.tabWidget_detail = QtWidgets.QTabWidget(self.tab_3)
        self.tabWidget_detail.setObjectName("tabWidget_detail")
        self.tabWidget_detail.tabBar().setObjectName("tabWidget_detail_bar")
        self.tabWidget_detail.setTabsClosable(True)
        self.tabWidget_detail.setMovable(True)
        self.verticalLayout_detail.addWidget(self.tabWidget_detail)
        self.tabWidget_detail.tabCloseRequested['int'].connect(self.tabWidget_detail.removeTab)


        self.verticalLayout.addWidget(self.tabWidget)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tabWidget.setTabText(0, _translate("MainWindow", "数据采集"))
        self.tabWidget.setTabText(1, _translate("MainWindow", "话题分析"))
        self.tabWidget.setTabText(2, _translate("MainWindow", "舆情分析"))
        self.tabWidget.setTabText(3, _translate("MainWindow", "话题追踪"))
        self.tabWidget.setTabText(4, _translate("MainWindow", "话题预警"))
        with open(dirname + '/qt/mainwindow.qss', 'r') as f:
            self.setStyleSheet(f.read())

    def getDetail(self, id):
        """
        获取话题的详细信息，在舆情分析模块中加入一个tab展示
        :param id:
        :return:
        """
        self.tabWidget.setCurrentIndex(2)
        for i in range(self.tabWidget_detail.count()):
            if self.tabWidget_detail.tabText(i) == str(id):
                self.tabWidget_detail.setCurrentIndex(i)
                return

        topic_detail = Ui_Topic_Detail(id, self)
        self.tabWidget_detail.addTab(topic_detail, "")
        _translate = QtCore.QCoreApplication.translate
        self.tabWidget_detail.setTabText(self.tabWidget_detail.indexOf(topic_detail), _translate("MainWindow", str(id)))
        self.tabWidget_detail.setCurrentWidget(topic_detail)

    def topicTrade(self, id):
        """
        话题追踪
        :param id:
        :return:
        """
        self.tabWidget.setCurrentIndex(3)
        self.tab_4.setId(id)

    def closeEvent(self, *args, **kwargs):
        self.tab.stopSpider()  # 关闭爬虫进程
        MongoDB.close_client()  # 关闭mongoDB连接
        os.system('taskkill /F /FI "IMAGENAME eq QtWebEngineProcess.exe"')  # 关闭浏览器引擎进程

    def resizeEvent(self, *args, **kwargs):
        self.tabWidget.setStyleSheet('#tabWidget_bar::tab{width:' + str((self.size().width() - 140) / 5) + 'px;}')
