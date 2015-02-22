# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LEDgoes Designer.ui'
#
# Created: Fri Jan 02 22:36:51 2015
#      by: PyQt5 UI code generator 5.1.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DesignerWindow(object):
    def setupUi(self, DesignerWindow):
        DesignerWindow.setObjectName("DesignerWindow")
        DesignerWindow.resize(621, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("LEDgoes-Icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DesignerWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(DesignerWindow)
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.webView = QtWebKitWidgets.QWebView(self.centralwidget)
        self.webView.setUrl(QtCore.QUrl("about:blank"))
        self.webView.setObjectName("webView")
        self.verticalLayout.addWidget(self.webView)
        DesignerWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(DesignerWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 621, 21))
        self.menubar.setObjectName("menubar")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        DesignerWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(DesignerWindow)
        self.statusbar.setObjectName("statusbar")
        DesignerWindow.setStatusBar(self.statusbar)
        self.actionAbout_LEDgoes_PC_Interface = QtWidgets.QAction(DesignerWindow)
        self.actionAbout_LEDgoes_PC_Interface.setObjectName("actionAbout_LEDgoes_PC_Interface")
        self.actionUSB_Device_Selection = QtWidgets.QAction(DesignerWindow)
        self.actionUSB_Device_Selection.setCheckable(True)
        self.actionUSB_Device_Selection.setChecked(True)
        self.actionUSB_Device_Selection.setObjectName("actionUSB_Device_Selection")
        self.menuHelp.addAction(self.actionAbout_LEDgoes_PC_Interface)
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(DesignerWindow)
        QtCore.QMetaObject.connectSlotsByName(DesignerWindow)

    def retranslateUi(self, DesignerWindow):
        _translate = QtCore.QCoreApplication.translate
        DesignerWindow.setWindowTitle(_translate("DesignerWindow", "LEDgoes PC Interface"))
        self.menuHelp.setTitle(_translate("DesignerWindow", "Help"))
        self.actionAbout_LEDgoes_PC_Interface.setText(_translate("DesignerWindow", "About LEDgoes PC Interface..."))
        self.actionUSB_Device_Selection.setText(_translate("DesignerWindow", "Show Only LEDgoes Communicators"))

from PyQt5 import QtWebKitWidgets
