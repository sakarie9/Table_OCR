# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui3.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(399, 262)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.folderSelectButton = QtWidgets.QPushButton(Dialog)
        self.folderSelectButton.setObjectName("folderSelectButton")
        self.horizontalLayout.addWidget(self.folderSelectButton)
        self.tagSelectButton = QtWidgets.QPushButton(Dialog)
        self.tagSelectButton.setObjectName("tagSelectButton")
        self.horizontalLayout.addWidget(self.tagSelectButton)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(6, -1, -1, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.radioButton1 = QtWidgets.QRadioButton(Dialog)
        self.radioButton1.setChecked(True)
        self.radioButton1.setObjectName("radioButton1")
        self.buttonGroup = QtWidgets.QButtonGroup(Dialog)
        self.buttonGroup.setObjectName("buttonGroup")
        self.buttonGroup.addButton(self.radioButton1)
        self.verticalLayout.addWidget(self.radioButton1)
        self.radioButton2 = QtWidgets.QRadioButton(Dialog)
        self.radioButton2.setObjectName("radioButton2")
        self.buttonGroup.addButton(self.radioButton2)
        self.verticalLayout.addWidget(self.radioButton2)
        self.radioButton3 = QtWidgets.QRadioButton(Dialog)
        self.radioButton3.setObjectName("radioButton3")
        self.buttonGroup.addButton(self.radioButton3)
        self.verticalLayout.addWidget(self.radioButton3)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout_3.addWidget(self.progressBar)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.startButton = QtWidgets.QPushButton(Dialog)
        self.startButton.setObjectName("startButton")
        self.horizontalLayout_2.addWidget(self.startButton)
        self.cancelButton = QtWidgets.QPushButton(Dialog)
        self.cancelButton.setDefault(True)
        self.cancelButton.setFlat(False)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_2.addWidget(self.cancelButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Dialog)
        self.folderSelectButton.clicked.connect(Dialog.selectFolder)
        self.tagSelectButton.clicked.connect(Dialog.selectTag)
        self.startButton.clicked.connect(Dialog.startProcess)
        self.cancelButton.clicked.connect(Dialog.cancelProcess)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.folderSelectButton.setText(_translate("Dialog", "选择文件夹"))
        self.tagSelectButton.setText(_translate("Dialog", "选择标签"))
        self.radioButton1.setText(_translate("Dialog", "生成Excel+Tag"))
        self.radioButton2.setText(_translate("Dialog", "只生成Excel"))
        self.radioButton3.setText(_translate("Dialog", "只生成Tag"))
        self.label.setText(_translate("Dialog", "0/0"))
        self.startButton.setText(_translate("Dialog", "开始"))
        self.cancelButton.setText(_translate("Dialog", "取消"))
