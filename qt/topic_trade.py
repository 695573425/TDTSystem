# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'self.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

import sys

# sys.path.append('E:\Python\workspace\TDTSystem')
from setting import *
from mongo import MongoDB
from qt.echarts import Ui_Pyecharts

from qt.topic_list import MyLabel


class Ui_Topic_Trade(QtWidgets.QWidget):
    """
    话题追踪模块
    """
    def __init__(self, mainwindow):
        super().__init__()
        client = MongoDB.get_client()
        db = client[MONGO_DB]
        self.collection = db['topic']
        self.weibo_collection = db['weibo']
        self.setupUi(mainwindow)
        self.id = None

    def setupUi(self, MainWindow):
        self.setObjectName("self")
        self.MainWindow = MainWindow
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.idlabel = QtWidgets.QLabel(self)
        self.verticalLayout.addWidget(self.idlabel)
        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setStyleSheet('border:none')
        self.groupBox.setMaximumHeight(50)
        self.horticalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.verticalLayout.addWidget(self.groupBox)

        # pyecharts, 展示话题地理传播路径，话题转发（评论）关系图
        self.echarts = Ui_Pyecharts.getEngine2(self)
        self.echarts.setMinimumHeight(400)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.echarts.setSizePolicy(sizePolicy)
        self.verticalLayout.addWidget(self.echarts)

        self.label = MyLabel(self.groupBox, self)
        self.label.Select(False)
        self.label.setVisible(False)
        self.label_2 = MyLabel(self.groupBox, self)
        self.label_2.Select(False)
        self.label_2.setVisible(False)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        spacerItem_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        spacerItem_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horticalLayout.addItem(spacerItem)
        self.horticalLayout.addWidget(self.label)
        self.horticalLayout.addItem(spacerItem_1)
        self.horticalLayout.addWidget(self.label_2)
        self.horticalLayout.addItem(spacerItem_2)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def setId(self, id):
        """
        设置话题id
        :param id:
        :return:
        """
        if self.id == id:
            return
        self.id = id
        self.idlabel.setText('ID: ' + str(self.id))
        self.label.setId(id)
        self.label.Select(False)
        self.label.setVisible(True)
        self.label_2.setId(id)
        self.label_2.Select(False)
        self.label_2.setVisible(True)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("self", "Form"))
        self.idlabel.setStyleSheet('font:20px')
        # self.textBrowser.setText('话题总数：' + str(self.tableWidget.rowCount()) + '\n')
        self.label.setText(_translate("self", "话题传播"))
        self.label_2.setText(_translate("self", "微博转发关系图"))
