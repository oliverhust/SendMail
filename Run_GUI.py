#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_send1 import Ui_MainWindow
from ui_add_account import Ui_Dialog_Account
from ui_progress import Ui_Dialog_Progress
from main import UIInterface

# import pdb; pdb.set_trace()

# ########################### 主窗口 ############################
class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)
        self.setupUi(self)

        # 窗口启动
        self.timer_form_load = QTimer(self)
        self.connect(self.timer_form_load, SIGNAL("timeout()"), self.slot_form_load)
        self.timer_form_load.start(100)

        # 打开正文、附件、Excel
        self.connect(self.pushButton_body, SIGNAL("clicked()"), self.slot_open_body)
        self.connect(self.pushButton_append, SIGNAL("clicked()"), self.slot_open_appends)
        self.connect(self.pushButton_mail_list, SIGNAL("clicked()"), self.slot_open_mail_list)

        # 按钮 开始、退出
        self.connect(self.pushButton_OK, SIGNAL("clicked()"), self.slot_button_run)
        self.connect(self.pushButton_cancel, SIGNAL("clicked()"), self.slot_button_cancel)

        # 添加/删除账户
        self.connect(self.pushButton_account_add, SIGNAL("clicked()"), self.account_add)
        self.connect(self.pushButton_account_del, SIGNAL("clicked()"), self.account_del)

        # 用户界面数据
        self._sub = u""
        self._body_path = u""
        self._append_list = []
        self._xls_path = u""
        self._xls_selected_list = []
        self._xls_col_name = ""
        self._sender_name = u""
        self._speed_each_hour = 400
        self._speed_each_time = 40

    def slot_open_body(self):
        self.label_body.setText(QString(u"正在打开，请稍候..."))
        s = QFileDialog.getOpenFileName(self, "Open file dialog", "/", "Text file(*.txt)")
        if len(s) == 0:
            self._body_path = u""
        else:
            self._body_path = unicode(s)
        self.label_body.setText(QString(s))

    def slot_open_appends(self):
        self.label_append.setText(QString(u"正在打开，请稍候..."))
        s_list = QFileDialog.getOpenFileNames(self, "Open file dialog", "/", "All files(*.*)")
        if not s_list:
            self.label_append.setText(QString(u""))
            self._append_list = []
        # 拼接附件文件名
        self._append_list = [unicode(s_list[0])]
        q_s = QString(unicode(s_list[0]).replace(u'\\', u'/'))
        for i in range(1, len(s_list)):
            self._append_list.append(unicode(s_list[i]))
            q_s += QString(u"; ") + QString(unicode(s_list[i]).replace(u'\\', u'/'))
        self.label_append.setText(q_s)

    def slot_open_mail_list(self):
        self.label_maillist.setText(QString(u"正在打开，请稍候..."))
        s = QFileDialog.getOpenFileName(self, "Open file dialog", "/", "Excel file(*.xls;*.xlsx)")
        if len(s) == 0:
            self._xls_path = u""
        else:
            self._xls_path = unicode(s)
        self.label_maillist.setText(QString(s))

    def slot_form_load(self):
        print("Start the Form.")
        self.timer_form_load.stop()

    def slot_button_cancel(self):
        r = QMessageBox.warning(self, "Warning",
                                QString(u"是否保存进度，以便下次启动继续?"),
                                QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel,
                                QMessageBox.Save)
        if r == QMessageBox.Save:
            print("Warning button/Save")
            self.close()
        elif r == QMessageBox.Discard:
            print("Warning button/Discard")
            self.close()
        elif r == QMessageBox.Cancel:
            print("Warning button/Cancel")
        else:
            return

    def _get_ui_accounts_data(self):
        # 返回一个账户结构体的列表，没有则返回[]
        self.listWidget.


    def _ui_data_check(self):
        if len(self.lineEdit_Sub.text()) == 0:
            QMessageBox.critical(self, u"Input Error", QString(u"请输入标题"))
            return False
        if len(self._body_path) == 0:
            QMessageBox.critical(self, u"Input Error", QString(u"请输入正文txt文件所在路径"))
            return False
        if len(self._xls_path) == 0:
            QMessageBox.critical(self, u"Input Error", QString(u"请输入包含邮箱列表的Excel表格所在路径"))
            return False

        start_str = unicode(self.lineEdit_Xls_From.text())
        end_str = unicode(self.lineEdit_Xls_To.text())
        if len(start_str) == 0 or len(end_str) == 0:
            QMessageBox.critical(self, u"Input Error", QString(u"请输入Excel表格中从表的起始"))
            return False
        col_str = unicode(self.lineEdit_Xls_Col.text())
        if len(col_str) == 0:
            QMessageBox.critical(self, u"Input Error", QString(u"请输入Excel表格中邮箱所在的列"))
            return False

        if start_str.isdigit() and end_str.isdigit() and len(col_str) == 1 \
           and col_str.isalpha() and int(start_str) <= int(end_str):
            pass
        else:
            QMessageBox.critical(self, u"Input Error", QString(u"请正确输入Excel表格中从表的起始及列名"))
            return False

        if len(self.lineEdit_Sender_Name.text()) == 0:
            QMessageBox.critical(self, u"Input Error", QString(u"请输入发件人"))
            return False

        return True

    def slot_button_run(self):
        if not self._ui_data_check():
            return

        self._sub = self.lineEdit_Sub.text()
        # xls表格位置选择
        start = int(self.lineEdit_Xls_From.text())
        end = int(self.lineEdit_Xls_To.text())
        self._xls_selected_list = range(start, end + 1)
        self._xls_col_name = self.lineEdit_Xls_Col.text()
        self._sender_name = unicode(self.lineEdit_Sender_Name.text())
        self._speed_each_hour = self.spinBox_Each_Hour.value()
        self._speed_each_time = self.spinBox_Each_Time.value()
        print(u"sub = {}\nbody_path = {}\nappend_list = {}\npath_xls = {}".format(self._sub, self._body_path, self._append_list, self._xls_path))
        print(u"selected = {}, col_name = {}, sender_name = {}".format(self._xls_selected_list, self._xls_col_name, self._sender_name))
        print(u"Speed each hour = {}, each time = {}".format(self._speed_each_hour, self._speed_each_time))

        # 弹出进度条界面
        new_win = ProgressWindow(self)
        if new_win.exec_():
            print("Exit nornal")

    def account_add(self):
        new_win = AccountWindow(self)
        if not new_win.exec_():
            print("User cancel")
            return

        self.listWidget.addItem(QString(new_win.user))

    def account_del(self):
        self.listWidget.takeItem(self.listWidget.currentRow())


# ########################### 添加账户窗口 ############################
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

    def cancel_account(self):
        self.reject()


# ########################### 进度条窗口 ############################
class ProgressWindow(QDialog, Ui_Dialog_Progress):

    def __init__(self, parent=None):
        super(ProgressWindow, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # 暂停按钮
        self.connect(self.pushButton, SIGNAL("clicked()"), self.slot_pause)

    def slot_pause(self):
        self.reject()


def test_ui_progress():
    app = QApplication(sys.argv)
    Window = ProgressWindow()
    Window.show()
    app.exec_()


def main():
    app = QApplication(sys.argv)
    Window = MainWindow()
    Window.show()
    app.exec_()


# Main Function
if __name__=='__main__':
    main()
    # test_ui_progress()