# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui1.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(961, 648)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.image1 = QtImageViewer(self.centralwidget)
        self.image1.setObjectName("image1")
        self.horizontalLayout.addWidget(self.image1)
        self.image2 = QtImageViewer(self.centralwidget)
        self.image2.setObjectName("image2")
        self.imageList = QtWidgets.QComboBox(self.image2)
        self.imageList.setGeometry(QtCore.QRect(0, 0, 141, 20))
        self.imageList.setObjectName("imageList")
        self.horizontalLayout.addWidget(self.image2)
        self.buttonLayout = QtWidgets.QVBoxLayout()
        self.buttonLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.buttonLayout.setObjectName("buttonLayout")
        self.loadButton = QtWidgets.QPushButton(self.centralwidget)
        self.loadButton.setObjectName("loadButton")
        self.buttonLayout.addWidget(self.loadButton)
        self.editButton = QtWidgets.QPushButton(self.centralwidget)
        self.editButton.setObjectName("editButton")
        self.buttonLayout.addWidget(self.editButton)
        self.excelButton = QtWidgets.QPushButton(self.centralwidget)
        self.excelButton.setObjectName("excelButton")
        self.buttonLayout.addWidget(self.excelButton)
        self.tagButton = QtWidgets.QPushButton(self.centralwidget)
        self.tagButton.setObjectName("tagButton")
        self.buttonLayout.addWidget(self.tagButton)
        self.horizontalLayout.addLayout(self.buttonLayout)
        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 3)
        self.horizontalLayout.setStretch(2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 961, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.loadButton.clicked.connect(MainWindow.loadImage)
        self.editButton.clicked.connect(MainWindow.editConfig)
        self.excelButton.clicked.connect(MainWindow.startProcess2)
        self.imageList.currentIndexChanged['int'].connect(MainWindow.changeImage)
        self.tagButton.clicked.connect(MainWindow.selectTag)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.loadButton.setText(_translate("MainWindow", "打开图片"))
        self.editButton.setText(_translate("MainWindow", "修改参数"))
        self.excelButton.setText(_translate("MainWindow", "生成Excel"))
        self.tagButton.setText(_translate("MainWindow", "生成标签"))
from QtImageViewer import QtImageViewer
