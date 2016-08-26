# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_ndr.ui'
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

class Ui_Dialog_Ndr(object):
    def setupUi(self, Dialog_Ndr):
        Dialog_Ndr.setObjectName(_fromUtf8("Dialog_Ndr"))
        Dialog_Ndr.setWindowModality(QtCore.Qt.NonModal)
        Dialog_Ndr.resize(1034, 658)
        Dialog_Ndr.setMinimumSize(QtCore.QSize(1034, 658))
        Dialog_Ndr.setMaximumSize(QtCore.QSize(1034, 658))
        Dialog_Ndr.setStyleSheet(_fromUtf8("#Dialog_Ndr {\n"
"    background-image: url(:/r_back/pic/r_back/blue.jpg);\n"
"}"))
        self.tableWidget = QtGui.QTableWidget(Dialog_Ndr)
        self.tableWidget.setGeometry(QtCore.QRect(40, 220, 951, 401))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(12)
        self.tableWidget.setFont(font)
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.tableWidget.setAutoFillBackground(False)
        self.tableWidget.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 60);"))
        self.tableWidget.setFrameShape(QtGui.QFrame.Panel)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.textEdit = QtGui.QTextEdit(Dialog_Ndr)
        self.textEdit.setGeometry(QtCore.QRect(450, 30, 541, 171))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(12)
        self.textEdit.setFont(font)
        self.textEdit.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 60);"))
        self.textEdit.setFrameShape(QtGui.QFrame.Panel)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.label = QtGui.QLabel(Dialog_Ndr)
        self.label.setGeometry(QtCore.QRect(180, 20, 151, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(24)
        self.label.setFont(font)
        self.label.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.label.setObjectName(_fromUtf8("label"))
        self.pushButton = QtGui.QPushButton(Dialog_Ndr)
        self.pushButton.setGeometry(QtCore.QRect(40, 30, 121, 71))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(22)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet(_fromUtf8("background-color: rgba(190, 190, 190, 120);"))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.label_2 = QtGui.QLabel(Dialog_Ndr)
        self.label_2.setGeometry(QtCore.QRect(360, 20, 51, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(24)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_NdrNum = QtGui.QLabel(Dialog_Ndr)
        self.label_NdrNum.setGeometry(QtCore.QRect(270, 20, 71, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(24)
        self.label_NdrNum.setFont(font)
        self.label_NdrNum.setStyleSheet(_fromUtf8("color: rgb(0, 0, 220);"))
        self.label_NdrNum.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_NdrNum.setObjectName(_fromUtf8("label_NdrNum"))
        self.lcdNumber = QtGui.QLCDNumber(Dialog_Ndr)
        self.lcdNumber.setGeometry(QtCore.QRect(180, 120, 251, 81))
        self.lcdNumber.setStyleSheet(_fromUtf8("color: rgb(0, 0, 127);"))
        self.lcdNumber.setFrameShape(QtGui.QFrame.Box)
        self.lcdNumber.setObjectName(_fromUtf8("lcdNumber"))
        self.label_3 = QtGui.QLabel(Dialog_Ndr)
        self.label_3.setGeometry(QtCore.QRect(180, 85, 141, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.pushButton_Save = QtGui.QPushButton(Dialog_Ndr)
        self.pushButton_Save.setEnabled(True)
        self.pushButton_Save.setGeometry(QtCore.QRect(40, 125, 121, 71))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(14)
        self.pushButton_Save.setFont(font)
        self.pushButton_Save.setStyleSheet(_fromUtf8("background-color: rgba(190, 190, 190, 120);"))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/r_icon/pic/r_icon/excel.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_Save.setIcon(icon)
        self.pushButton_Save.setIconSize(QtCore.QSize(40, 40))
        self.pushButton_Save.setObjectName(_fromUtf8("pushButton_Save"))

        self.retranslateUi(Dialog_Ndr)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Ndr)

    def retranslateUi(self, Dialog_Ndr):
        Dialog_Ndr.setWindowTitle(_translate("Dialog_Ndr", "退信接收", None))
        Dialog_Ndr.setToolTip(_translate("Dialog_Ndr", "建议\"已等待退信时间\"大于15分钟后停止接收退信", None))
        self.tableWidget.setToolTip(_translate("Dialog_Ndr", "建议\"已等待退信时间\"大于15分钟后停止接收退信", None))
        self.textEdit.setToolTip(_translate("Dialog_Ndr", "建议\"已等待退信时间\"大于15分钟后停止接收退信", None))
        self.textEdit.setHtml(_translate("Dialog_Ndr", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Malgun Gothic Semilight\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.label.setText(_translate("Dialog_Ndr", "退信:", None))
        self.pushButton.setText(_translate("Dialog_Ndr", "停止", None))
        self.label_2.setText(_translate("Dialog_Ndr", "封", None))
        self.label_NdrNum.setText(_translate("Dialog_Ndr", "0", None))
        self.lcdNumber.setToolTip(_translate("Dialog_Ndr", "建议该时间大于15分钟后停止接收退信", None))
        self.label_3.setToolTip(_translate("Dialog_Ndr", "建议该时间大于15分钟后停止接收退信", None))
        self.label_3.setText(_translate("Dialog_Ndr", "已等待退信时间：", None))
        self.pushButton_Save.setToolTip(_translate("Dialog_Ndr", "<html><head/><body><p><span style=\" font-size:11pt;\">停止之后才能保存表格</span></p></body></html>", None))
        self.pushButton_Save.setText(_translate("Dialog_Ndr", "导出\n"
"表格", None))

import send1_rc
