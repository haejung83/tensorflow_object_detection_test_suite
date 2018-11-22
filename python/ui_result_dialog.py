# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'result_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(720, 490)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(16)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelTitleTested = QtWidgets.QLabel(Dialog)
        self.labelTitleTested.setObjectName("labelTitleTested")
        self.horizontalLayout.addWidget(self.labelTitleTested)
        self.labelTestedCount = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelTestedCount.sizePolicy().hasHeightForWidth())
        self.labelTestedCount.setSizePolicy(sizePolicy)
        self.labelTestedCount.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelTestedCount.setObjectName("labelTestedCount")
        self.horizontalLayout.addWidget(self.labelTestedCount)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(16)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labelTitlePassed = QtWidgets.QLabel(Dialog)
        self.labelTitlePassed.setObjectName("labelTitlePassed")
        self.horizontalLayout_2.addWidget(self.labelTitlePassed)
        self.labelPassedCount = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelPassedCount.sizePolicy().hasHeightForWidth())
        self.labelPassedCount.setSizePolicy(sizePolicy)
        self.labelPassedCount.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelPassedCount.setObjectName("labelPassedCount")
        self.horizontalLayout_2.addWidget(self.labelPassedCount)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        # Haejung did it
        # self.widgetResultList = QtWidgets.QListView(Dialog)
        self.widgetResultList = QtWidgets.QListWidget(Dialog)
        self.widgetResultList.setObjectName("widgetResultList")

        self.verticalLayout_2.addWidget(self.widgetResultList)
        self.btnBox = QtWidgets.QDialogButtonBox(Dialog)
        self.btnBox.setOrientation(QtCore.Qt.Horizontal)
        self.btnBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.btnBox.setObjectName("btnBox")
        self.verticalLayout_2.addWidget(self.btnBox)

        self.retranslateUi(Dialog)
        self.btnBox.accepted.connect(Dialog.accept)
        self.btnBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Test Result"))
        self.labelTitleTested.setText(_translate("Dialog", "Tested Count"))
        self.labelTestedCount.setText(_translate("Dialog", "None"))
        self.labelTitlePassed.setText(_translate("Dialog", "Passed Count"))
        self.labelPassedCount.setText(_translate("Dialog", "None"))

