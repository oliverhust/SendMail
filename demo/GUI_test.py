#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_send1 import Ui_MainWindow
from ui_add_account import Ui_Dialog_Account
from main import UIInterface


# Make main window class
class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)
        self.setupUi(self)

        self.connect(self.pushButton_cancel, SIGNAL("clicked()"), self.slot_button_cancel)

        # 添加/删除账户
        self.connect(self.pushButton_account_add, SIGNAL("clicked()"), self.account_add)
        self.connect(self.pushButton_account_del, SIGNAL("clicked()"), self.account_del)

    def account_add(self):
        print("account_add start")
        self.ui = AccountWindow()
        if self.ui.exec_():
            print("Exit diag1 success")
            print("Get user: {}".format(self.ui.user))
        else:
            print("Exit diag1 abnormal")
        print("account_add exit")

    def account_del(self):
        print("account_del start")
        add = FruitDlg('Add fruit', self)
        if add.exec_():
            print("Get data {}".format(add.fruit))
            print("Exit add success")
        print("account_del end")

    def slot_button_cancel(self):
        self.close()


#弹出对话框
#add
class FruitDlg(QDialog):
    def __init__(self, title, fruit=None, parent=None):
        super(FruitDlg, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)

        #label_0 = QLabel(u'Add fruit： 譬如苹果，香蕉，橘子，西瓜，火龙果，枣，梨子，榴莲')
        label_0 = QLabel(title)
        #让标签字换行
        label_0.setWordWrap(True)
        self.fruit_edit = QLineEdit(fruit)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        validator = QRegExp(r'[^\s][\w\s]+')
        self.fruit_edit.setValidator(QRegExpValidator(validator, self))

        v_box = QVBoxLayout()
        v_box.addWidget(label_0)
        v_box.addWidget(self.fruit_edit)
        v_box.addWidget(btns)
        self.setLayout(v_box)

        self.fruit = None

    def accept(self):
        #OK按钮
        self.fruit = unicode(self.fruit_edit.text())
        #self.done(0)
        QDialog.accept(self)

    def reject(self):
        #self.done(1)
        QDialog.reject(self)


class AccountWindow(QDialog, Ui_Dialog_Account):
    def __init__(self, parent=None):
        super(AccountWindow, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # 确定/取消按钮
        self.connect(self.pushButton, SIGNAL("clicked()"), self.add_account)
        self.connect(self.pushButton_cancel, SIGNAL("clicked()"), self.cancel_account)

        # 账户数据
        self.user = u""
        self.passwd = u""
        self.host = u""

    def add_account(self):
        user = unicode(self.lineEdit_user.text())
        passwd = unicode(self.lineEdit_passwd.text())
        host = unicode(self.lineEdit_host)

        if len(user) == 0 or len(passwd) == 0 or len(host) == 0:
            QMessageBox.critical(self, u"Input Error", QString(u"请输入完整信息"))
            return

        if -1 == user.find(u"@"):
            QMessageBox.critical(self, u"Input Error", QString(u"邮箱账号有误，应为xxx@@xxx.xxx"))
            return

        self.user = user
        self.passwd = passwd
        self.host = host

        self.accept()
        print("Closed Account Form")

    def cancel_account(self):
        self.reject()


def main():
    app = QApplication(sys.argv)
    Window = MainWindow()
    Window.show()
    app.exec_()


def test_account():
    app = QApplication(sys.argv)
    Dialog = QDialog()
    Window = AccountWindow(Dialog)
    Dialog.exec_()
    #Window.show()
    #app.exec_()

# Main Function
if __name__=='__main__':
    main()
    #test_account()