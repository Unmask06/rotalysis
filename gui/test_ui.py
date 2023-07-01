# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'test.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialogButtonBox, QLabel,
    QMainWindow, QMenuBar, QPlainTextEdit, QPushButton,
    QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(793, 549)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tbox_config = QPlainTextEdit(self.centralwidget)
        self.tbox_config.setObjectName(u"tbox_config")
        self.tbox_config.setGeometry(QRect(10, 40, 271, 41))
        self.bbConfig = QDialogButtonBox(self.centralwidget)
        self.bbConfig.setObjectName(u"bbConfig")
        self.bbConfig.setGeometry(QRect(10, 100, 156, 24))
        self.bbConfig.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 261, 16))
        self.pbConfig = QPushButton(self.centralwidget)
        self.pbConfig.setObjectName(u"pbConfig")
        self.pbConfig.setGeometry(QRect(300, 50, 81, 21))
        self.bbTaskList = QDialogButtonBox(self.centralwidget)
        self.bbTaskList.setObjectName(u"bbTaskList")
        self.bbTaskList.setGeometry(QRect(10, 230, 156, 24))
        self.bbTaskList.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.tbox_tasklist = QPlainTextEdit(self.centralwidget)
        self.tbox_tasklist.setObjectName(u"tbox_tasklist")
        self.tbox_tasklist.setGeometry(QRect(10, 170, 271, 41))
        self.pbTaskList = QPushButton(self.centralwidget)
        self.pbTaskList.setObjectName(u"pbTaskList")
        self.pbTaskList.setGeometry(QRect(300, 180, 81, 21))
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 140, 261, 16))
        self.pbInputFolder = QPushButton(self.centralwidget)
        self.pbInputFolder.setObjectName(u"pbInputFolder")
        self.pbInputFolder.setGeometry(QRect(300, 320, 81, 21))
        self.bbInputFolder = QDialogButtonBox(self.centralwidget)
        self.bbInputFolder.setObjectName(u"bbInputFolder")
        self.bbInputFolder.setGeometry(QRect(10, 370, 156, 24))
        self.bbInputFolder.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.tbox_InputFolder = QPlainTextEdit(self.centralwidget)
        self.tbox_InputFolder.setObjectName(u"tbox_InputFolder")
        self.tbox_InputFolder.setGeometry(QRect(10, 310, 271, 41))
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 280, 261, 16))
        self.tbox_OutputFolder = QPlainTextEdit(self.centralwidget)
        self.tbox_OutputFolder.setObjectName(u"tbox_OutputFolder")
        self.tbox_OutputFolder.setGeometry(QRect(400, 40, 271, 41))
        self.bbOutputFolder = QDialogButtonBox(self.centralwidget)
        self.bbOutputFolder.setObjectName(u"bbOutputFolder")
        self.bbOutputFolder.setGeometry(QRect(400, 100, 156, 24))
        self.bbOutputFolder.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(400, 10, 261, 16))
        self.pbOutputFolder = QPushButton(self.centralwidget)
        self.pbOutputFolder.setObjectName(u"pbOutputFolder")
        self.pbOutputFolder.setGeometry(QRect(690, 50, 81, 21))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 793, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Select Configuration excel file", None))
        self.pbConfig.setText(QCoreApplication.translate("MainWindow", u"Select File", None))
        self.pbTaskList.setText(QCoreApplication.translate("MainWindow", u"Select File", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Select Task List excel file", None))
        self.pbInputFolder.setText(QCoreApplication.translate("MainWindow", u"Select Folder", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Select Input Folder", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Select Output Folder", None))
        self.pbOutputFolder.setText(QCoreApplication.translate("MainWindow", u"Select Folder", None))
    # retranslateUi

