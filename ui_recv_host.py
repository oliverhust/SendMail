# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_recv_host.ui'
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

class Ui_Dialog_RecvHost(object):
    def setupUi(self, Dialog_RecvHost):
        Dialog_RecvHost.setObjectName(_fromUtf8("Dialog_RecvHost"))
        Dialog_RecvHost.resize(494, 274)
        Dialog_RecvHost.setStyleSheet(_fromUtf8("#Dialog_RecvHost {\n"
"    \n"
"    background-image: url(:/r_back/pic/r_back/love_s.jpeg);\n"
"\n"
"}"))
        self.label = QtGui.QLabel(Dialog_RecvHost)
        self.label.setGeometry(QtCore.QRect(20, 20, 81, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setStyleSheet(_fromUtf8(""))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_user = QtGui.QLabel(Dialog_RecvHost)
        self.label_user.setGeometry(QtCore.QRect(110, 20, 361, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Comic Sans MS"))
        font.setPointSize(22)
        font.setUnderline(False)
        self.label_user.setFont(font)
        self.label_user.setText(_fromUtf8(""))
        self.label_user.setObjectName(_fromUtf8("label_user"))
        self.label_3 = QtGui.QLabel(Dialog_RecvHost)
        self.label_3.setGeometry(QtCore.QRect(20, 80, 186, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(16)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet(_fromUtf8(""))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.pushButton = QtGui.QPushButton(Dialog_RecvHost)
        self.pushButton.setGeometry(QtCore.QRect(370, 190, 101, 66))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("High Tower Text"))
        font.setPointSize(14)
        font.setItalic(True)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet(_fromUtf8("QPushButton:hover {    \n"
"    margin: 0;\n"
"}\n"
"QPushButton {    \n"
"    color: rgb(255, 209, 117);    \n"
"    border-image: url(:/r_icon/pic/r_icon/right64.png);\n"
"    margin: 5;\n"
"    background-color: rgba(255, 255, 255, 0);\n"
" \n"
"}"))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.label_4 = QtGui.QLabel(Dialog_RecvHost)
        self.label_4.setGeometry(QtCore.QRect(25, 210, 286, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.comboBox = QtGui.QComboBox(Dialog_RecvHost)
        self.comboBox.setGeometry(QtCore.QRect(20, 120, 451, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(16)
        self.comboBox.setFont(font)
        self.comboBox.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 120);\n"
"selection-color: rgb(0, 0, 0);\n"
"selection-background-color: rgba(0, 0, 255, 25);"))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))

        self.retranslateUi(Dialog_RecvHost)
        QtCore.QMetaObject.connectSlotsByName(Dialog_RecvHost)

    def retranslateUi(self, Dialog_RecvHost):
        Dialog_RecvHost.setWindowTitle(_translate("Dialog_RecvHost", "设置IMAP服务器", None))
        Dialog_RecvHost.setToolTip(_translate("Dialog_RecvHost", "<html><head/><body><p>目前只支持下拉选项中的域名</p><p>不支持的账号需自己登录查看退信</p></body></html>", None))
        self.label.setText(_translate("Dialog_RecvHost", "账号：", None))
        self.label_3.setText(_translate("Dialog_RecvHost", "IMAP服务器地址：", None))
        self.pushButton.setToolTip(_translate("Dialog_RecvHost", "<html><head/><body><p>下一步</p></body></html>", None))
        self.pushButton.setText(_translate("Dialog_RecvHost", "Next", None))
        self.label_4.setToolTip(_translate("Dialog_RecvHost", "<html><head/><body><p>目前只支持下拉选项中的域名</p><p>不支持的账号需自己登录查看退信</p></body></html>", None))
        self.label_4.setText(_translate("Dialog_RecvHost", "已为您自动选择，建议直接下一步", None))
        self.comboBox.setToolTip(_translate("Dialog_RecvHost", "<html><head/><body><p>目前只支持下拉选项中的域名</p><p>不支持的账号需自己登录查看退信</p></body></html>", None))

import send1_rc
