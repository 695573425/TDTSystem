# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

from qt.mainwindow import Ui_MainWindow

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.setupUi()
    ui.setWindowTitle('食品安全话题检测与追踪系统')
    ui.show()
    sys.exit(app.exec_())

