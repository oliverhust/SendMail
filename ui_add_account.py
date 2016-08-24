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
        Dialog_Account.resize(345, 333)
        Dialog_Account.setMinimumSize(QtCore.QSize(345, 333))
        Dialog_Account.setMaximumSize(QtCore.QSize(345, 333))
        Dialog_Account.setWindowOpacity(1.0)
        Dialog_Account.setStyleSheet(_fromUtf8("#Dialog_Account {background-image: url(:/background/pic/dream_like2_s.jpg);}\n"
"\n"
"\n"
""))
        self.lineEdit_user = QtGui.QLineEdit(Dialog_Account)
        self.lineEdit_user.setGeometry(QtCore.QRect(30, 65, 291, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Comic Sans MS"))
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_user.setFont(font)
        self.lineEdit_user.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 120);"))
        self.lineEdit_user.setFrame(False)
        self.lineEdit_user.setObjectName(_fromUtf8("lineEdit_user"))
        self.label_6 = QtGui.QLabel(Dialog_Account)
        self.label_6.setGeometry(QtCore.QRect(30, 180, 161, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Microsoft YaHei UI Light"))
        font.setPointSize(15)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(3)
        self.label_6.setFont(font)
        self.label_6.setStyleSheet(_fromUtf8("color: rgb(255, 255, 255);\n"
"font: 25 15pt \"Microsoft YaHei UI Light\";"))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_4 = QtGui.QLabel(Dialog_Account)
        self.label_4.setGeometry(QtCore.QRect(30, 35, 91, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Microsoft YaHei UI Light"))
        font.setPointSize(15)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(3)
        self.label_4.setFont(font)
        self.label_4.setStyleSheet(_fromUtf8("color: rgb(255, 255, 255);\n"
"font: 25 15pt \"Microsoft YaHei UI Light\";"))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.lineEdit_passwd = QtGui.QLineEdit(Dialog_Account)
        self.lineEdit_passwd.setGeometry(QtCore.QRect(30, 135, 291, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(14)
        self.lineEdit_passwd.setFont(font)
        self.lineEdit_passwd.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 120);"))
        self.lineEdit_passwd.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText)
        self.lineEdit_passwd.setInputMask(_fromUtf8(""))
        self.lineEdit_passwd.setText(_fromUtf8(""))
        self.lineEdit_passwd.setFrame(False)
        self.lineEdit_passwd.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEdit_passwd.setPlaceholderText(_fromUtf8(""))
        self.lineEdit_passwd.setObjectName(_fromUtf8("lineEdit_passwd"))
        self.label_5 = QtGui.QLabel(Dialog_Account)
        self.label_5.setGeometry(QtCore.QRect(30, 105, 91, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Microsoft YaHei UI Light"))
        font.setPointSize(15)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(3)
        self.label_5.setFont(font)
        self.label_5.setStyleSheet(_fromUtf8("color: rgb(255, 255, 255);\n"
"font: 25 15pt \"Microsoft YaHei UI Light\";"))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.lineEdit_host = QtGui.QLineEdit(Dialog_Account)
        self.lineEdit_host.setGeometry(QtCore.QRect(30, 210, 291, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Comic Sans MS"))
        font.setPointSize(14)
        self.lineEdit_host.setFont(font)
        self.lineEdit_host.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 120);"))
        self.lineEdit_host.setFrame(False)
        self.lineEdit_host.setObjectName(_fromUtf8("lineEdit_host"))
        self.pushButton = QtGui.QCommandLinkButton(Dialog_Account)
        self.pushButton.setGeometry(QtCore.QRect(70, 250, 61, 71))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 40))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 40))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 40))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 40))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 40))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 40))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 40))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 40))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 40))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.pushButton.setPalette(palette)
        self.pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButton.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 40);"))
        self.pushButton.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icon/pic/ico/green_ok_128px_1075415_easyicon.net.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QtCore.QSize(50, 50))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton_cancel = QtGui.QCommandLinkButton(Dialog_Account)
        self.pushButton_cancel.setGeometry(QtCore.QRect(200, 250, 61, 71))
        self.pushButton_cancel.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 60);"))
        self.pushButton_cancel.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icon/pic/ico/red_delete_128px_1075470_easyicon.net.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_cancel.setIcon(icon1)
        self.pushButton_cancel.setIconSize(QtCore.QSize(50, 50))
        self.pushButton_cancel.setObjectName(_fromUtf8("pushButton_cancel"))

        self.retranslateUi(Dialog_Account)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Account)
        Dialog_Account.setTabOrder(self.lineEdit_user, self.lineEdit_passwd)
        Dialog_Account.setTabOrder(self.lineEdit_passwd, self.lineEdit_host)

    def retranslateUi(self, Dialog_Account):
        Dialog_Account.setWindowTitle(_translate("Dialog_Account", "添加账号", None))
        Dialog_Account.setToolTip(_translate("Dialog_Account", "添加一个账号", None))
        self.label_6.setText(_translate("Dialog_Account", "服务器地址", None))
        self.label_4.setText(_translate("Dialog_Account", "邮箱账号", None))
        self.label_5.setText(_translate("Dialog_Account", "密码", None))
        self.lineEdit_host.setText(_translate("Dialog_Account", "mail.hust.edu.cn", None))

import send1_rc
