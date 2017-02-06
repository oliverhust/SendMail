# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'editor_add_link.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog_AddLink(object):
    def setupUi(self, Dialog_AddLink):
        Dialog_AddLink.setObjectName(_fromUtf8("Dialog_AddLink"))
        Dialog_AddLink.resize(761, 98)
        Dialog_AddLink.setStyleSheet(_fromUtf8(""))
        self.verticalLayout_3 = QtGui.QVBoxLayout(Dialog_AddLink)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(Dialog_AddLink)
        self.label.setMinimumSize(QtCore.QSize(81, 26))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit_Link = QtGui.QLineEdit(Dialog_AddLink)
        self.lineEdit_Link.setMinimumSize(QtCore.QSize(581, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_Link.setFont(font)
        self.lineEdit_Link.setText(_fromUtf8(""))
        self.lineEdit_Link.setObjectName(_fromUtf8("lineEdit_Link"))
        self.horizontalLayout.addWidget(self.lineEdit_Link)
        self.Button_OK = QtGui.QPushButton(Dialog_AddLink)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Button_OK.sizePolicy().hasHeightForWidth())
        self.Button_OK.setSizePolicy(sizePolicy)
        self.Button_OK.setMinimumSize(QtCore.QSize(61, 31))
        self.Button_OK.setMaximumSize(QtCore.QSize(61, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Button_OK.setFont(font)
        self.Button_OK.setObjectName(_fromUtf8("Button_OK"))
        self.horizontalLayout.addWidget(self.Button_OK)
        self.horizontalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(Dialog_AddLink)
        self.label_2.setMinimumSize(QtCore.QSize(81, 26))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.lineEdit_Text = QtGui.QLineEdit(Dialog_AddLink)
        self.lineEdit_Text.setMinimumSize(QtCore.QSize(581, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_Text.setFont(font)
        self.lineEdit_Text.setText(_fromUtf8(""))
        self.lineEdit_Text.setObjectName(_fromUtf8("lineEdit_Text"))
        self.horizontalLayout_2.addWidget(self.lineEdit_Text)
        self.Button_Cancel = QtGui.QPushButton(Dialog_AddLink)
        self.Button_Cancel.setMinimumSize(QtCore.QSize(61, 31))
        self.Button_Cancel.setMaximumSize(QtCore.QSize(61, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Button_Cancel.setFont(font)
        self.Button_Cancel.setObjectName(_fromUtf8("Button_Cancel"))
        self.horizontalLayout_2.addWidget(self.Button_Cancel)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.retranslateUi(Dialog_AddLink)
        QtCore.QMetaObject.connectSlotsByName(Dialog_AddLink)
        Dialog_AddLink.setTabOrder(self.lineEdit_Link, self.lineEdit_Text)

    def retranslateUi(self, Dialog_AddLink):
        Dialog_AddLink.setWindowTitle(_translate("Dialog_AddLink", "插入超链接", None))
        self.label.setText(_translate("Dialog_AddLink", "链接地址:", None))
        self.Button_OK.setText(_translate("Dialog_AddLink", "确定", None))
        self.label_2.setText(_translate("Dialog_AddLink", "显示文字:", None))
        self.lineEdit_Text.setPlaceholderText(_translate("Dialog_AddLink", "不填就和\'链接地址\'一样", None))
        self.Button_Cancel.setText(_translate("Dialog_AddLink", "取消", None))

