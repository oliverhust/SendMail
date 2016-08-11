# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_add_account.ui'
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

class Ui_Dialog_Account(object):
    def setupUi(self, Dialog_Account):
        Dialog_Account.setObjectName(_fromUtf8("Dialog_Account"))
        Dialog_Account.resize(354, 342)
        self.lineEdit_user = QtGui.QLineEdit(Dialog_Account)
        self.lineEdit_user.setGeometry(QtCore.QRect(30, 60, 291, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(14)
        self.lineEdit_user.setFont(font)
        self.lineEdit_user.setObjectName(_fromUtf8("lineEdit_user"))
        self.label_6 = QtGui.QLabel(Dialog_Account)
        self.label_6.setGeometry(QtCore.QRect(30, 170, 161, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(16)
        self.label_6.setFont(font)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.pushButton_cancel = QtGui.QPushButton(Dialog_Account)
        self.pushButton_cancel.setGeometry(QtCore.QRect(190, 270, 131, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(16)
        self.pushButton_cancel.setFont(font)
        self.pushButton_cancel.setObjectName(_fromUtf8("pushButton_cancel"))
        self.label_4 = QtGui.QLabel(Dialog_Account)
        self.label_4.setGeometry(QtCore.QRect(30, 20, 91, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(16)
        self.label_4.setFont(font)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.lineEdit_passwd = QtGui.QLineEdit(Dialog_Account)
        self.lineEdit_passwd.setGeometry(QtCore.QRect(30, 130, 291, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(14)
        self.lineEdit_passwd.setFont(font)
        self.lineEdit_passwd.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText)
        self.lineEdit_passwd.setInputMask(_fromUtf8(""))
        self.lineEdit_passwd.setText(_fromUtf8(""))
        self.lineEdit_passwd.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEdit_passwd.setPlaceholderText(_fromUtf8(""))
        self.lineEdit_passwd.setObjectName(_fromUtf8("lineEdit_passwd"))
        self.pushButton = QtGui.QPushButton(Dialog_Account)
        self.pushButton.setGeometry(QtCore.QRect(30, 270, 131, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(16)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.label_5 = QtGui.QLabel(Dialog_Account)
        self.label_5.setGeometry(QtCore.QRect(30, 90, 91, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(16)
        self.label_5.setFont(font)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.lineEdit_host = QtGui.QLineEdit(Dialog_Account)
        self.lineEdit_host.setGeometry(QtCore.QRect(30, 210, 291, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(14)
        self.lineEdit_host.setFont(font)
        self.lineEdit_host.setObjectName(_fromUtf8("lineEdit_host"))

        self.retranslateUi(Dialog_Account)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Account)
        Dialog_Account.setTabOrder(self.lineEdit_user, self.lineEdit_passwd)
        Dialog_Account.setTabOrder(self.lineEdit_passwd, self.lineEdit_host)
        Dialog_Account.setTabOrder(self.lineEdit_host, self.pushButton)
        Dialog_Account.setTabOrder(self.pushButton, self.pushButton_cancel)

    def retranslateUi(self, Dialog_Account):
        Dialog_Account.setWindowTitle(_translate("Dialog_Account", "添加账号", None))
        self.label_6.setText(_translate("Dialog_Account", "服务器地址", None))
        self.pushButton_cancel.setText(_translate("Dialog_Account", "取消", None))
        self.label_4.setText(_translate("Dialog_Account", "邮箱账号", None))
        self.pushButton.setText(_translate("Dialog_Account", "确定", None))
        self.label_5.setText(_translate("Dialog_Account", "密码", None))
        self.lineEdit_host.setText(_translate("Dialog_Account", "mail.hust.edu.cn", None))

