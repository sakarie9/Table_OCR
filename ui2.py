# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui2.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(910, 799)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.horizontalLayout_4.addWidget(self.tableWidget)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableWidget_tags = QtWidgets.QTableWidget(Dialog)
        self.tableWidget_tags.setObjectName("tableWidget_tags")
        self.tableWidget_tags.setColumnCount(0)
        self.tableWidget_tags.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget_tags)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.deleteButton = QtWidgets.QPushButton(Dialog)
        self.deleteButton.setAutoDefault(False)
        self.deleteButton.setDefault(False)
        self.deleteButton.setFlat(False)
        self.deleteButton.setObjectName("deleteButton")
        self.horizontalLayout.addWidget(self.deleteButton)
        self.clearButton = QtWidgets.QPushButton(Dialog)
        self.clearButton.setAutoDefault(False)
        self.clearButton.setObjectName("clearButton")
        self.horizontalLayout.addWidget(self.clearButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.outputButton = QtWidgets.QPushButton(Dialog)
        self.outputButton.setObjectName("outputButton")
        self.horizontalLayout_2.addWidget(self.outputButton)
        self.closeButton = QtWidgets.QPushButton(Dialog)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout_2.addWidget(self.closeButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout.setStretch(0, 10)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.horizontalLayout_4.setStretch(0, 5)
        self.horizontalLayout_4.setStretch(1, 1)

        self.retranslateUi(Dialog)
        self.deleteButton.clicked.connect(Dialog.deleteRow)
        self.clearButton.clicked.connect(Dialog.clearTable)
        self.outputButton.clicked.connect(Dialog.output)
        self.closeButton.clicked.connect(Dialog.close)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.deleteButton.setText(_translate("Dialog", "删除行"))
        self.clearButton.setText(_translate("Dialog", "清空"))
        self.outputButton.setText(_translate("Dialog", "导出"))
        self.closeButton.setText(_translate("Dialog", "关闭"))
