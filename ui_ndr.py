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
        self.tableWidget = QtGui.QTableWidget(Dialog_Ndr)
        self.tableWidget.setGeometry(QtCore.QRect(40, 220, 951, 401))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(12)
        self.tableWidget.setFont(font)
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.tableWidget.setAutoFillBackground(False)
        self.tableWidget.setFrameShape(QtGui.QFrame.Panel)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.textEdit = QtGui.QTextEdit(Dialog_Ndr)
        self.textEdit.setGeometry(QtCore.QRect(450, 20, 541, 171))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(12)
        self.textEdit.setFont(font)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.label = QtGui.QLabel(Dialog_Ndr)
        self.label.setGeometry(QtCore.QRect(190, 30, 151, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(24)
        self.label.setFont(font)
        self.label.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.label.setObjectName(_fromUtf8("label"))
        self.pushButton = QtGui.QPushButton(Dialog_Ndr)
        self.pushButton.setGeometry(QtCore.QRect(40, 30, 111, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(22)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.label_2 = QtGui.QLabel(Dialog_Ndr)
        self.label_2.setGeometry(QtCore.QRect(370, 30, 51, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(24)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_NdrNum = QtGui.QLabel(Dialog_Ndr)
        self.label_NdrNum.setGeometry(QtCore.QRect(280, 30, 71, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(24)
        self.label_NdrNum.setFont(font)
        self.label_NdrNum.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_NdrNum.setObjectName(_fromUtf8("label_NdrNum"))
        self.lcdNumber = QtGui.QLCDNumber(Dialog_Ndr)
        self.lcdNumber.setGeometry(QtCore.QRect(170, 110, 251, 81))
        self.lcdNumber.setFrameShape(QtGui.QFrame.Box)
        self.lcdNumber.setObjectName(_fromUtf8("lcdNumber"))
        self.label_3 = QtGui.QLabel(Dialog_Ndr)
        self.label_3.setGeometry(QtCore.QRect(40, 120, 141, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Malgun Gothic Semilight"))
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))

        self.retranslateUi(Dialog_Ndr)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Ndr)

    def retranslateUi(self, Dialog_Ndr):
        Dialog_Ndr.setWindowTitle(_translate("Dialog_Ndr", "退信接收", None))
        Dialog_Ndr.setToolTip(_translate("Dialog_Ndr", "建议\"已等待退信时间\"大于15分钟后停止接收退信", None))
        self.tableWidget.setToolTip(_translate("Dialog_Ndr", "建议\"已等待退信时间\"大于15分钟后停止接收退信", None))
        self.textEdit.setToolTip(_translate("Dialog_Ndr", "建议\"已等待退信时间\"大于15分钟后停止接收退信", None))
        self.label.setText(_translate("Dialog_Ndr", "退信:", None))
        self.pushButton.setText(_translate("Dialog_Ndr", "停止", None))
        self.label_2.setText(_translate("Dialog_Ndr", "封", None))
        self.label_NdrNum.setText(_translate("Dialog_Ndr", "0", None))
        self.lcdNumber.setToolTip(_translate("Dialog_Ndr", "建议该时间大于15分钟后停止接收退信", None))
        self.label_3.setToolTip(_translate("Dialog_Ndr", "建议该时间大于15分钟后停止接收退信", None))
        self.label_3.setText(_translate("Dialog_Ndr", "已等待退信时间", None))

