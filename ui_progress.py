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
        Dialog_Progress.resize(836, 470)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(10)
        Dialog_Progress.setFont(font)
        Dialog_Progress.setStyleSheet(_fromUtf8("#Dialog_Progress {\n"
"    \n"
"    \n"
"    border-image: url(:/background/pic/back/lan.jpg);\n"
"}"))
        self.pushButton = QtGui.QPushButton(Dialog_Progress)
        self.pushButton.setGeometry(QtCore.QRect(25, 25, 101, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(14)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet(_fromUtf8("background-color: rgba(190, 190, 190, 120);\n"
""))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.progressBar = QtGui.QProgressBar(Dialog_Progress)
        self.progressBar.setGeometry(QtCore.QRect(25, 85, 781, 36))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Agency FB"))
        font.setPointSize(12)
        self.progressBar.setFont(font)
        self.progressBar.setStyleSheet(_fromUtf8(""))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.textEdit = QtGui.QTextEdit(Dialog_Progress)
        self.textEdit.setGeometry(QtCore.QRect(25, 140, 781, 301))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(12)
        self.textEdit.setFont(font)
        self.textEdit.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 30);"))
        self.textEdit.setFrameShadow(QtGui.QFrame.Sunken)
        self.textEdit.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.label_5 = QtGui.QLabel(Dialog_Progress)
        self.label_5.setGeometry(QtCore.QRect(155, 30, 81, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Microsoft YaHei UI Light"))
        font.setPointSize(16)
        self.label_5.setFont(font)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtGui.QLabel(Dialog_Progress)
        self.label_6.setGeometry(QtCore.QRect(310, 30, 66, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Microsoft YaHei UI Light"))
        font.setPointSize(16)
        self.label_6.setFont(font)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_has_sent = QtGui.QLabel(Dialog_Progress)
        self.label_has_sent.setGeometry(QtCore.QRect(240, 30, 66, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Microsoft YaHei UI Light"))
        font.setPointSize(16)
        self.label_has_sent.setFont(font)
        self.label_has_sent.setObjectName(_fromUtf8("label_has_sent"))
        self.label_failed_sent = QtGui.QLabel(Dialog_Progress)
        self.label_failed_sent.setGeometry(QtCore.QRect(375, 30, 66, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Microsoft YaHei UI Light"))
        font.setPointSize(16)
        self.label_failed_sent.setFont(font)
        self.label_failed_sent.setObjectName(_fromUtf8("label_failed_sent"))
        self.label_not_sent = QtGui.QLabel(Dialog_Progress)
        self.label_not_sent.setGeometry(QtCore.QRect(540, 30, 81, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Microsoft YaHei UI Light"))
        font.setPointSize(16)
        self.label_not_sent.setFont(font)
        self.label_not_sent.setObjectName(_fromUtf8("label_not_sent"))
        self.label_7 = QtGui.QLabel(Dialog_Progress)
        self.label_7.setGeometry(QtCore.QRect(450, 30, 81, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Microsoft YaHei UI Light"))
        font.setPointSize(16)
        self.label_7.setFont(font)
        self.label_7.setObjectName(_fromUtf8("label_7"))

        self.retranslateUi(Dialog_Progress)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Progress)

    def retranslateUi(self, Dialog_Progress):
        Dialog_Progress.setWindowTitle(_translate("Dialog_Progress", "发送进度", None))
        self.pushButton.setText(_translate("Dialog_Progress", "暂停", None))
        self.textEdit.setHtml(_translate("Dialog_Progress", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Malgun Gothic Semilight\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.label_5.setText(_translate("Dialog_Progress", "已发送：", None))
        self.label_6.setText(_translate("Dialog_Progress", "失败：", None))
        self.label_has_sent.setText(_translate("Dialog_Progress", "0", None))
        self.label_failed_sent.setText(_translate("Dialog_Progress", "0", None))
        self.label_not_sent.setText(_translate("Dialog_Progress", "0", None))
        self.label_7.setText(_translate("Dialog_Progress", "待发送：", None))

import send1_rc
