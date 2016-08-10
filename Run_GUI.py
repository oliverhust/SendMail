#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_send1 import Ui_MainWindow
from main import UIInterface


# Make main window class
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
        self.connect(self.pushButton_OK, SIGNAL("clicked()"), self.slot_button_ok)
        self.connect(self.pushButton_cancel, SIGNAL("clicked()"), self.slot_button_cancel)

        # 用户界面数据
        self._sub = u""
        self._body_path = u""
        self._append_list = []
        self._xls_path = u""
        self._xls_selected_list = []
        self._xls_col_name = ""

    def slot_open_body(self):
        s = QFileDialog.getOpenFileName(self, "Open file dialog", "/", "Text file(*.txt)")
        if len(s) == 0:
            self._body_path = u""
        else:
            self._body_path = unicode(s)
        self.label_body.setText(QString(s))

    def slot_open_appends(self):
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
            quit()
        elif r == QMessageBox.Discard:
            print("Warning button/Discard")
            quit()
        elif r == QMessageBox.Cancel:
            print("Warning button/Cancel")
        else:
            return

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

        ret = True
        if start_str.isdigit() and end_str.isdigit() and len(col_str) == 1 \
           and col_str.isalpha() and int(start_str) <= int(end_str):
            pass
        else:
            QMessageBox.critical(self, u"Input Error", QString(u"请正确输入Excel表格中从表的起始及列名"))
            ret = False
        return ret

    def slot_button_ok(self):
        if not self._ui_data_check():
            return

        self._sub = self.lineEdit_Sub.text()
        # xls表格位置选择
        start = int(self.lineEdit_Xls_From.text())
        end = int(self.lineEdit_Xls_To.text())
        self._xls_selected_list = range(start, end + 1)
        self._xls_col_name = self.lineEdit_Xls_Col.text()
        print(u"sub = {}\nbody_path = {}\nappend_list = {}\npath_xls = {}".format(self._sub, self._body_path, self._append_list, self._xls_path))
        print(u"selected = {}, col_name = {}".format(self._xls_selected_list, self._xls_col_name))




# Main Function
if __name__=='__main__':
    Program = QApplication(sys.argv)
    Window = MainWindow()
    Window.show()
    Program.exec_()