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
        Dialog_Progress.resize(574, 364)
        self.pushButton = QtGui.QPushButton(Dialog_Progress)
        self.pushButton.setGeometry(QtCore.QRect(20, 20, 71, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(14)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.progressBar = QtGui.QProgressBar(Dialog_Progress)
        self.progressBar.setGeometry(QtCore.QRect(20, 70, 541, 31))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.textEdit = QtGui.QTextEdit(Dialog_Progress)
        self.textEdit.setGeometry(QtCore.QRect(20, 120, 531, 221))
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.label_5 = QtGui.QLabel(Dialog_Progress)
        self.label_5.setGeometry(QtCore.QRect(130, 20, 81, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(14)
        self.label_5.setFont(font)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtGui.QLabel(Dialog_Progress)
        self.label_6.setGeometry(QtCore.QRect(320, 20, 81, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(14)
        self.label_6.setFont(font)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_has_sent = QtGui.QLabel(Dialog_Progress)
        self.label_has_sent.setGeometry(QtCore.QRect(210, 20, 81, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(14)
        self.label_has_sent.setFont(font)
        self.label_has_sent.setObjectName(_fromUtf8("label_has_sent"))
        self.label_failed_sent = QtGui.QLabel(Dialog_Progress)
        self.label_failed_sent.setGeometry(QtCore.QRect(390, 20, 81, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(14)
        self.label_failed_sent.setFont(font)
        self.label_failed_sent.setObjectName(_fromUtf8("label_failed_sent"))

        self.retranslateUi(Dialog_Progress)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Progress)

    def retranslateUi(self, Dialog_Progress):
        Dialog_Progress.setWindowTitle(_translate("Dialog_Progress", "发送进度", None))
        self.pushButton.setText(_translate("Dialog_Progress", "暂停", None))
        self.label_5.setText(_translate("Dialog_Progress", "已发送：", None))
        self.label_6.setText(_translate("Dialog_Progress", "失败：", None))
        self.label_has_sent.setText(_translate("Dialog_Progress", "0", None))
        self.label_failed_sent.setText(_translate("Dialog_Progress", "0", None))
