# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenuBar,
    QPlainTextEdit, QProgressBar, QPushButton, QSizePolicy,
    QStatusBar, QTabWidget, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(793, 549)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(0, 10, 781, 511))
        self.tabInput = QWidget()
        self.tabInput.setObjectName(u"tabInput")
        self.tbox_config = QPlainTextEdit(self.tabInput)
        self.tbox_config.setObjectName(u"tbox_config")
        self.tbox_config.setGeometry(QRect(10, 40, 271, 41))
        self.label_4 = QLabel(self.tabInput)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(400, 10, 261, 16))
        self.pbInputFolder = QPushButton(self.tabInput)
        self.pbInputFolder.setObjectName(u"pbInputFolder")
        self.pbInputFolder.setGeometry(QRect(300, 320, 81, 21))
        self.pbOutputFolder = QPushButton(self.tabInput)
        self.pbOutputFolder.setObjectName(u"pbOutputFolder")
        self.pbOutputFolder.setGeometry(QRect(690, 50, 81, 21))
        self.pbConfig = QPushButton(self.tabInput)
        self.pbConfig.setObjectName(u"pbConfig")
        self.pbConfig.setGeometry(QRect(300, 50, 81, 21))
        self.label_2 = QLabel(self.tabInput)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 140, 261, 16))
        self.label = QLabel(self.tabInput)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 261, 16))
        self.tbox_tasklist = QPlainTextEdit(self.tabInput)
        self.tbox_tasklist.setObjectName(u"tbox_tasklist")
        self.tbox_tasklist.setGeometry(QRect(10, 170, 271, 41))
        self.tbox_OutputFolder = QPlainTextEdit(self.tabInput)
        self.tbox_OutputFolder.setObjectName(u"tbox_OutputFolder")
        self.tbox_OutputFolder.setGeometry(QRect(400, 40, 271, 41))
        self.label_3 = QLabel(self.tabInput)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 280, 261, 16))
        self.pbTaskList = QPushButton(self.tabInput)
        self.pbTaskList.setObjectName(u"pbTaskList")
        self.pbTaskList.setGeometry(QRect(300, 180, 81, 21))
        self.tbox_InputFolder = QPlainTextEdit(self.tabInput)
        self.tbox_InputFolder.setObjectName(u"tbox_InputFolder")
        self.tbox_InputFolder.setGeometry(QRect(10, 310, 271, 41))
        self.pbRun = QPushButton(self.tabInput)
        self.pbRun.setObjectName(u"pbRun")
        self.pbRun.setGeometry(QRect(680, 440, 75, 24))
        self.tabWidget.addTab(self.tabInput, "")
        self.tabProcess = QWidget()
        self.tabProcess.setObjectName(u"tabProcess")
        self.ProgressBar = QProgressBar(self.tabProcess)
        self.ProgressBar.setObjectName(u"ProgressBar")
        self.ProgressBar.setGeometry(QRect(130, 120, 261, 31))
        self.ProgressBar.setValue(24)
        self.tabWidget.addTab(self.tabProcess, "")
        self.tabError = QWidget()
        self.tabError.setObjectName(u"tabError")
        self.lbOutput = QLabel(self.tabError)
        self.lbOutput.setObjectName(u"lbOutput")
        self.lbOutput.setGeometry(QRect(210, 160, 411, 251))
        self.tabWidget.addTab(self.tabError, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 793, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Select Output Folder", None))
        self.pbInputFolder.setText(QCoreApplication.translate("MainWindow", u"Select Folder", None))
        self.pbOutputFolder.setText(QCoreApplication.translate("MainWindow", u"Select Folder", None))
        self.pbConfig.setText(QCoreApplication.translate("MainWindow", u"Select File", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Select Task List excel file", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Select Configuration excel file", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Select Input Folder", None))
        self.pbTaskList.setText(QCoreApplication.translate("MainWindow", u"Select File", None))
        self.pbRun.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabInput), QCoreApplication.translate("MainWindow", u"Input", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabProcess), QCoreApplication.translate("MainWindow", u"Process", None))
        self.lbOutput.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabError), QCoreApplication.translate("MainWindow", u"Error", None))
    # retranslateUi

