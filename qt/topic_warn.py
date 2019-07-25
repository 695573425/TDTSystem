# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'self.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!
import sys
import time

sys.path.append('E:\Python\workspace\TDTSystem')
from mongo import MongoDB
from ltp.ltp import Ltp
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow

from qt.my_widget import MyText, MyButton
from setting import *

class Ui_Topic_Warn(QtWidgets.QWidget):
    """
    话题预警模块
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        db = MongoDB.get_client()[MONGO_DB]
        self.topic_collection = db['topic']
        self.weibo_collection = db['weibo']
        self.attention = False
        self.emotion = False
        self._time = False
        self.ltp = Ltp.get_object()
        self.setupUi()

    def setupUi(self):
        self.setObjectName('topic_warn')
        self.vLayout = QtWidgets.QVBoxLayout(self)

        self.intro = QtWidgets.QLabel(self)
        self.intro.setMaximumHeight(50)
        self.vLayout.addWidget(self.intro)
        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setMaximumHeight(50)
        self.hLayout_groupBox = QtWidgets.QHBoxLayout(self.groupBox)
        self.checkBox = QtWidgets.QCheckBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.checkBox.setSizePolicy(sizePolicy)
        self.checkBox_2 = QtWidgets.QCheckBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.checkBox_2.setSizePolicy(sizePolicy)
        self.checkBox_3 = QtWidgets.QCheckBox(self.groupBox)
        self.button = QtWidgets.QPushButton(self.groupBox)
        self.hLayout_groupBox.addWidget(self.checkBox)
        self.hLayout_groupBox.addWidget(self.checkBox_2)
        self.hLayout_groupBox.addWidget(self.checkBox_3)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hLayout_groupBox.addItem(spacerItem)
        self.hLayout_groupBox.addWidget(self.button)
        self.vLayout.addWidget(self.groupBox)

        self.tabWidget = QtWidgets.QTabWidget(self)
        self.vLayout.addWidget(self.tabWidget)

        self.button.clicked.connect(self.warning)
        self.retranslateUi()

    def showResult(self, result):
        """
        展示话题预警结果
        :param result:
        :return:
        """
        count = 0
        self.tabWidget.clear()
        for _, values in result.items():
            count += 1
            if not values:
                continue
            tab = QtWidgets.QWidget()
            vLayout_tab = QtWidgets.QVBoxLayout(tab)

            textBrowser = QtWidgets.QTextBrowser(tab)
            if count == 1:
                warn_text = '特重警情（Ⅰ级）：出现舆情。国内网民对该舆情关注度极高，媒体高度关注，传播速度非常快，影响扩大到了整个社会，舆情即将化为行为舆论。'
            elif count == 2:
                warn_text = '重警情（Ⅱ级）：出现舆情。国内网民对该舆情关注度高，媒体开始关注，传播速度快，影响扩散到了很大范围，舆情有转化为行为舆论的可能。'
            elif count == 3:
                warn_text = '中度警情（Ⅲ级）：出现舆情。国内网民对该舆情关注度较高，传播速度中等，舆情影响局限在一定范围内，没有转化为行为舆论的可能。'
            else:
                warn_text = '轻警情（Ⅳ级）：出现舆情。国内网民对该舆情关注度低，传播速度慢，舆情影响局限在较小范围内，没有转化为行为舆论的可能。'
            textBrowser.setText('       ' + warn_text)
            textBrowser.setMaximumHeight(50)
            textBrowser.setStyleSheet('border:none')
            vLayout_tab.addWidget(textBrowser)

            scrollArea = QtWidgets.QScrollArea(tab)
            scrollArea.setWidgetResizable(True)

            scrollAreaWidgetContents = QtWidgets.QWidget()
            scrollArea.setWidget(scrollAreaWidgetContents)
            vLayout = QtWidgets.QVBoxLayout(scrollAreaWidgetContents)

            values = dict(sorted(values.items(), key=lambda item: item[1], reverse=True))
            for id in values:
                groupBox = QtWidgets.QGroupBox(scrollArea)
                groupBox.setStyleSheet('QGroupBox{background:white;border:none}')
                v = QtWidgets.QVBoxLayout(groupBox)
                groupBox2 = QtWidgets.QGroupBox(groupBox)
                groupBox2.setMaximumHeight(50)
                h = QtWidgets.QHBoxLayout(groupBox2)
                label = QtWidgets.QLabel('预警值： ')
                h.addWidget(label)
                progressBar = QtWidgets.QProgressBar(groupBox2)
                progressBar.setMaximumWidth(100)
                progressBar.setMinimumWidth(100)
                progressBar.setMaximum(200)
                progressBar.setProperty("value", values[id])
                if values[id] > 200:
                    progressBar.setProperty("value", 200)
                progressBar.setFormat("")
                h.addWidget(progressBar)
                spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                   QtWidgets.QSizePolicy.Minimum)
                h.addItem(spacerItem)
                button1 = MyButton(id, self.parent, text='舆情分析')
                button2 = MyButton(id, self.parent, text='话题追踪')
                h.addWidget(button1)
                h.addWidget(button2)
                v.addWidget(groupBox2)
                text = MyText(ltp=self.ltp, id=id, topic_collection=self.topic_collection,
                              weibo_collection=self.weibo_collection)
                v.addWidget(text)
                vLayout.addWidget(groupBox)
            vLayout_tab.addWidget(scrollArea)
            self.tabWidget.addTab(tab, '')
            self.tabWidget.setTabText(self.tabWidget.indexOf(tab), str(count) + '级预警')

    def get_weight(self, text):
        """
        关注度、评价度、时间指标权重
        :param text:
        :return:
        """
        weight = [0.4, 0.4, 0.2]
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

    def get_score(self, topic):
        """
        计算预警值
        :param topic:
        :return:
        """
        weight = self.get_weight([self.attention, self.emotion, self._time])

        heat = topic['heat']
        heat1 = heat / 100
        try:
            emotion = topic['score']
            total = emotion[0] + emotion[1] + emotion[2]
            if total > 500:
                emotion[0] += emotion[2] * 0.3 * emotion[0] / (emotion[0] + emotion[1])
                emotion[1] += emotion[2] * 0.3 * emotion[1] / (emotion[0] + emotion[1])
                emotion[2] *= 0.7
                emotion1 = emotion[1] * (emotion[0] + emotion[1]) / emotion[0] / total
            else:
                emotion1 = 0
        except:
            emotion1 = 0

        emotion1 = emotion1 * 60

        timeArray = time.strptime(topic['central_time'], '%Y-%m-%d %H:%M:%S')
        time_gap = int(time.time() - time.mktime(timeArray))
        time_gap = 3000 * 86400 / time_gap

        # print(heat, heat1, emotion, emotion1, topic['central_time'], time_gap)
        return heat1 * weight[0] + emotion1 * weight[1] + time_gap * weight[2]

    def warning(self):
        """
        话题预警算法
        :return:
        """
        if self.attention == self.checkBox.isChecked() \
                and self.emotion == self.checkBox_2.isChecked() \
                and self._time == self.checkBox_3.isChecked():
            return
        self.attention = self.checkBox.isChecked()
        self.emotion = self.checkBox_2.isChecked()
        self._time = self.checkBox_3.isChecked()

        if not self.attention and not self.emotion and not self._time:
            return

        topicset = self.topic_collection.find()
        warning_result = {
            100: {},
            60: {},
            40: {}
        }
        for topic in topicset:
            if topic['text_num'] < 5:
                continue
            score = self.get_score(topic)
            for key in warning_result:
                if score >= key:
                    warning_result[key][topic['_id']] = score
                    break

        self.showResult(warning_result)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setStyleSheet('font:15px Times New Roman;')
        self.intro.setStyleSheet('font:20px;border:none')
        self.intro.setText('     这是话题预警模块，根据所选指标进行话题预警\n')
        self.groupBox.setStyleSheet('QGroupBox{border:none}')
        self.checkBox.setText(_translate('topic_warn', '关注度'))
        self.checkBox_2.setText(_translate('topic_warn', '评价度'))
        self.checkBox_3.setText(_translate('topic_warn', '时间'))
        self.button.setText(_translate('topic_warn', '预警'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = QMainWindow()
    mainwindow.resize(800, 600)
    ui = Ui_Topic_Warn()
    mainwindow.setCentralWidget(ui)
    mainwindow.show()
    sys.exit(app.exec_())
