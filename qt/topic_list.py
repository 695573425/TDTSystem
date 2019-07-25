# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'self.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

# sys.path.append('E:\Python\workspace\TDTSystem')

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView

from qt.echarts import Ui_Pyecharts
from qt.city import china
from qt.my_widget import MyLabel

from ltp.ltp import Ltp
from mongo import MongoDB
from setting import *


class Ui_Topic_List(QtWidgets.QWidget):
    """
    话题分析模块
    """
    
    def __init__(self, mainwindow):
        super().__init__()
        client = MongoDB.get_client()
        db = client[MONGO_DB]
        self.collection = db['topic']
        self.weibo_collection = db['weibo']
        self.ltp = Ltp.get_object()
        self.area = ''
        self.keys = []
        self.setupUi(mainwindow)

    
    def setupUi(self,  MainWindow):
        self.setObjectName("self")
        self.MainWindow = MainWindow
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")


        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setStyleSheet('border:none')
        self.groupBox.setMaximumHeight(50)
        self.horticalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.verticalLayout.addWidget(self.groupBox)

        # pyecharts, 展示话题地理分布，关键词云，总体热度时间曲线
        self.echarts = Ui_Pyecharts.getEngine(self)
        self.echarts.setMinimumHeight(400)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.echarts.setSizePolicy(sizePolicy)
        self.verticalLayout.addWidget(self.echarts)
        self.echarts.map('china')

        self.label = MyLabel(self.groupBox, self)
        self.label.Select(True)
        self.label_2 = MyLabel(self.groupBox, self)
        self.label_2.Select(False)
        self.label_3 = MyLabel(self.groupBox, self)
        self.label_3.Select(False)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        spacerItem_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        spacerItem_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        spacerItem_3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horticalLayout.addItem(spacerItem)
        self.horticalLayout.addWidget(self.label)
        self.horticalLayout.addItem(spacerItem_1)
        self.horticalLayout.addWidget(self.label_2)
        self.horticalLayout.addItem(spacerItem_2)
        self.horticalLayout.addWidget(self.label_3)
        self.horticalLayout.addItem(spacerItem_3)


        self.groupBox_2 = QtWidgets.QGroupBox(self)
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setMinimumHeight(200)
        self.groupBox_2.setMaximumHeight(300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        # 关键词
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setObjectName('keytab')
        self.tabWidget.tabBar().setObjectName('keytab_bar')
        self.tabWidget.setMaximumHeight(30)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.tabCloseRequested['int'].connect(self.tab_remove)
        self.verticalLayout_3.addWidget(self.tabWidget)

        # 话题列表
        self.tableWidget = QtWidgets.QTableWidget(self.groupBox_2)
        self.tableWidget.setObjectName("tableWidget")
        self.setTablet()
        self.getTableData()

        self.verticalLayout_3.addWidget(self.tableWidget)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def tabChange(self):
        pass

    def tab_remove(self, index):
        key = self.tabWidget.tabText(index)
        self.tabWidget.removeTab(index)
        self.keys_update(key)

    def keys_update(self, key):
        if key in self.keys:
            self.keys.remove(key)
            self.getTableData()
        else:
            self.keys.append(key)
            tab = QtWidgets.QWidget()
            self.tabWidget.addTab(tab, '')
            self.tabWidget.setTabText(self.tabWidget.count()-1, key)
            self.getTableData()


    def set_area(self, area):
        if self.area == area:
            return
        self.area = area
        self.getTableData()

    def topic_has_keys(self, topic):

        for key in self.keys:
            if key not in topic['keywords']:
                return False
        if not self.area:
            return True
        for area in topic['entity']['Ns']:
            temp = ''.join(area[0])
            if temp in self.area or self.area in temp:
                return True
            if self.area in china:
                for city in china[self.area]:
                    if city in temp or temp in city:
                        return True
        return False

    def setTablet(self):
        _translate = QtCore.QCoreApplication.translate
        self.tableWidget.setColumnCount(6)
        item = QtWidgets.QTableWidgetItem()
        item.setText(_translate("test", "话题概要"))
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(_translate("test", "关键词"))
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(_translate("test", "微博总数"))
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(_translate("test", "热度"))
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(_translate("test", "开始时间"))
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(_translate("test", "更新时间"))
        self.tableWidget.setHorizontalHeaderItem(5, item)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget.setColumnWidth(1, 250)
        self.tableWidget.setColumnWidth(2, 60)
        self.tableWidget.setColumnWidth(3, 60)
        self.tableWidget.setColumnWidth(4, 60)
        self.tableWidget.setColumnWidth(5, 60)
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.cellDoubleClicked['int', 'int'].connect(self.getDetail)

    def getTableData(self):
        _translate = QtCore.QCoreApplication.translate
        topicset = self.collection.find().sort('text_num', -1)
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        for topic in topicset:
            # if topic['text_num'] < 5:
            #     continue
            if not self.topic_has_keys(topic):
                continue
            row_count = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(row_count+1)
            item = QtWidgets.QTableWidgetItem()
            item.setText(_translate("test", ''))
            self.tableWidget.setVerticalHeaderItem(row_count, item)
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            count = 0
            text = ''
            for id in topic['text_id_list']:
                weibo = self.weibo_collection.find_one({'id': id})
                if not weibo:
                    continue
                if weibo['comment_count'] > count:
                    count = weibo['comment_count']
                    text = weibo['content']
            title, body, _ = self.ltp.pretreating(text)
            if title:
                body = title
            item.setTextAlignment(Qt.AlignCenter)
            item.setText(_translate("test", body))
            self.tableWidget.setItem(row_count, 0, item)
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            count = 0
            keywords = []
            for key in topic['keywords']:
                count += 1
                if count > 10:
                    break
                keywords.append(key)
            item.setText(_translate("test", ' '.join(keywords)))
            self.tableWidget.setItem(row_count, 1, item)
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item.setData(Qt.DisplayRole, topic['text_num'])
            self.tableWidget.setItem(row_count, 2, item)
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item.setData(Qt.DisplayRole, topic['heat'])
            self.tableWidget.setItem(row_count, 3, item)
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item.setText(_translate("test", topic['start_time']))
            self.tableWidget.setItem(row_count, 4, item)
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item.setText(_translate("test", topic['latest_time']))
            self.tableWidget.setItem(row_count, 5, item)

    def getDetail(self, row):
        text_num = int(self.tableWidget.item(row, 2).text())
        start_time = self.tableWidget.item(row, 4).text()
        topic = self.collection.find_one({'text_num': text_num, 'start_time': start_time})
        id = topic['_id']
        self.MainWindow.getDetail(id)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("self", "Form"))
        self.groupBox_2.setTitle(_translate("self", "话题列表"))
        #self.textBrowser.setText('话题总数：' + str(self.tableWidget.rowCount()) + '\n')
        self.label.setText(_translate("self", "地理分布"))
        self.label_2.setText(_translate("self", "热词"))
        self.label_3.setText(_translate("self", "时间曲线"))
        self.tabWidget.setStyleSheet('''
        #keytab:pane{
            border:none;  
            background-color: white;      
        }
        #keytab_bar::close-button{
            subcontrol-position:left;
        }
        #keytab_bar::tab{ 
            border-bottom-color: yellow;
            border-radius: 10px;
            border: none;
            color: red;
            background: white;    
            margin-right: 20px;
            min-height: 20px;
            min-width: 20px;
            padding-left:10px;
            
        }
    ''')
