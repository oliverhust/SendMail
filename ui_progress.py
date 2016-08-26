# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_progress.ui'
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

class Ui_Dialog_Progress(object):
    def setupUi(self, Dialog_Progress):
        Dialog_Progress.setObjectName(_fromUtf8("Dialog_Progress"))
        Dialog_Progress.resize(1032, 604)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(10)
        Dialog_Progress.setFont(font)
        Dialog_Progress.setToolTip(_fromUtf8(""))
        Dialog_Progress.setStyleSheet(_fromUtf8(""))
        self.pushButton = QtGui.QPushButton(Dialog_Progress)
        self.pushButton.setGeometry(QtCore.QRect(40, 30, 141, 76))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(24)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet(_fromUtf8("QPushButton:hover {    \n"
"    background-color: rgba(190, 190, 190, 150);\n"
"}\n"
"QPushButton {    \n"
"    background-color: rgba(190, 190, 190, 70); \n"
"}"))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.progressBar = QtGui.QProgressBar(Dialog_Progress)
        self.progressBar.setGeometry(QtCore.QRect(0, 579, 1032, 25))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Agency FB"))
        font.setPointSize(12)
        self.progressBar.setFont(font)
        self.progressBar.setStyleSheet(_fromUtf8(""))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.textEdit = QtGui.QTextEdit(Dialog_Progress)
        self.textEdit.setGeometry(QtCore.QRect(40, 140, 946, 401))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(16)
        self.textEdit.setFont(font)
        self.textEdit.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 30);"))
        self.textEdit.setFrameShadow(QtGui.QFrame.Sunken)
        self.textEdit.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.widget = QtGui.QWidget(Dialog_Progress)
        self.widget.setGeometry(QtCore.QRect(0, 0, 1032, 580))
        self.widget.setStyleSheet(_fromUtf8(""))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.widget_2 = QtGui.QWidget(Dialog_Progress)
        self.widget_2.setGeometry(QtCore.QRect(260, 45, 676, 56))
        self.widget_2.setStyleSheet(_fromUtf8("QWidget#widget_2:hover {\n"
"    background-color: rgba(255, 255, 255, 120);\n"
"}"))
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.label_failed_sent = QtGui.QLabel(self.widget_2)
        self.label_failed_sent.setGeometry(QtCore.QRect(350, 5, 106, 40))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(22)
        self.label_failed_sent.setFont(font)
        self.label_failed_sent.setObjectName(_fromUtf8("label_failed_sent"))
        self.label_2 = QtGui.QLabel(self.widget_2)
        self.label_2.setGeometry(QtCore.QRect(257, 5, 87, 40))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(22)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.widget_2)
        self.label_3.setGeometry(QtCore.QRect(475, 5, 116, 40))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(22)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_not_sent = QtGui.QLabel(self.widget_2)
        self.label_not_sent.setGeometry(QtCore.QRect(597, 5, 16, 40))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(22)
        self.label_not_sent.setFont(font)
        self.label_not_sent.setObjectName(_fromUtf8("label_not_sent"))
        self.label_has_sent = QtGui.QLabel(self.widget_2)
        self.label_has_sent.setGeometry(QtCore.QRect(150, 5, 96, 40))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(22)
        self.label_has_sent.setFont(font)
        self.label_has_sent.setStyleSheet(_fromUtf8(""))
        self.label_has_sent.setObjectName(_fromUtf8("label_has_sent"))
        self.label_1 = QtGui.QLabel(self.widget_2)
        self.label_1.setGeometry(QtCore.QRect(26, 5, 116, 40))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(22)
        self.label_1.setFont(font)
        self.label_1.setStyleSheet(_fromUtf8(""))
        self.label_1.setObjectName(_fromUtf8("label_1"))
        self.widget.raise_()
        self.pushButton.raise_()
        self.progressBar.raise_()
        self.textEdit.raise_()
        self.widget_2.raise_()

        self.retranslateUi(Dialog_Progress)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Progress)

    def retranslateUi(self, Dialog_Progress):
        Dialog_Progress.setWindowTitle(_translate("Dialog_Progress", "发送进度", None))
        self.pushButton.setToolTip(_translate("Dialog_Progress", "<html><head/><body><p><span style=\" font-size:11pt;\">如果需要修改发送信息可以随时暂停，返回主界面修改后再次点击开始。已发送的邮件不会重复发送</span></p></body></html>", None))
        self.pushButton.setText(_translate("Dialog_Progress", "暂停", None))
        self.progressBar.setToolTip(_translate("Dialog_Progress", "<html><head/><body><p><span style=\" font-size:11pt;\">如果需要修改发送信息可以随时暂停，返回主界面修改后再次点击开始。已发送的邮件不会重复发送</span></p></body></html>", None))
        self.textEdit.setToolTip(_translate("Dialog_Progress", "<html><head/><body><p><span style=\" font-size:11pt;\">如果需要修改发送信息可以随时暂停，返回主界面修改后再次点击开始。已发送的邮件不会重复发送</span></p></body></html>", None))
        self.textEdit.setHtml(_translate("Dialog_Progress", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Malgun Gothic Semilight\'; font-size:16pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.label_failed_sent.setText(_translate("Dialog_Progress", "0", None))
        self.label_2.setText(_translate("Dialog_Progress", "失败：", None))
        self.label_3.setText(_translate("Dialog_Progress", "待发送：", None))
        self.label_not_sent.setText(_translate("Dialog_Progress", "0", None))
        self.label_has_sent.setText(_translate("Dialog_Progress", "0", None))
        self.label_1.setText(_translate("Dialog_Progress", "已发送：", None))

import send1_rc
