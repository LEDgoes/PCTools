# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LEDgoes Console.ui'
#
# Created: Sat May 31 19:25:19 2014
#      by: PyQt5 UI code generator 5.1.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ConsoleWindow(object):
    def setupUi(self, ConsoleWindow):
        ConsoleWindow.setObjectName("ConsoleWindow")
        ConsoleWindow.resize(640, 400)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("LEDgoes-Icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ConsoleWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(ConsoleWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.txtConsole = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.txtConsole.setReadOnly(True)
        self.txtConsole.setObjectName("txtConsole")
        self.horizontalLayout.addWidget(self.txtConsole)
        ConsoleWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ConsoleWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 21))
        self.menubar.setObjectName("menubar")
        ConsoleWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ConsoleWindow)
        self.statusbar.setObjectName("statusbar")
        ConsoleWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ConsoleWindow)
        QtCore.QMetaObject.connectSlotsByName(ConsoleWindow)

    def retranslateUi(self, ConsoleWindow):
        _translate = QtCore.QCoreApplication.translate
        ConsoleWindow.setWindowTitle(_translate("ConsoleWindow", "LEDgoes Console"))
        ConsoleWindow.setToolTip(_translate("ConsoleWindow", "How many milliseconds the program will pause before sending the next wave of serial data to the marquee"))

