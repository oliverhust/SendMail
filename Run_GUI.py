#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import random
import platform
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_send1 import Ui_MainWindow
from ui_add_account import Ui_Dialog_Account
from ui_progress import Ui_Dialog_Progress
from ui_recv_host import Ui_Dialog_RecvHost
from ui_ndr import Ui_Dialog_Ndr
from main import UIInterface, UITimer
from main import Account
from mylog import *

if 'Windows' in platform.system():
    import winsound

# import pdb; pdb.set_trace()
PROGRAM_UNIQUE_PORT = 48625


# ################################ GUI定时器(一次性与周期性混合) ##############################
class GUITimer(UITimer, QTimer):

    def __init__(self, parent=None):
        UITimer.__init__(self)
        QTimer.__init__(self, parent)
        self._FirstSet = None
        self._Period = None
        self._Callback = None
        self.connect(self, SIGNAL("timeout()"), self.__iner_callback)

    def setup(self, period_time, callback_function, first_set_time=None):
        if first_set_time is None:
            self._FirstSet = period_time
        else:
            self._FirstSet = first_set_time
        self._Period = period_time
        self._Callback = callback_function

    def start(self, first_set_time=None):
        if first_set_time is not None:
            self._FirstSet = first_set_time
        QTimer.start(self, self._FirstSet)

    def set_tmp_time(self, tmp_time):
        self.setInterval(tmp_time)

    def stop(self):
        QTimer.stop(self)

    def __iner_callback(self):
        QTimer.setInterval(self, self._Period)
        self._Callback()


# #####################################################################
# ########################### 无边框窗口 ###############################
class NoFrameWin(QWidget):

    def __init__(self, parent=None):
        super(NoFrameWin, self).__init__(parent)
        self._dragPosition = 0  # 窗口移动用
        self.setWindowOpacity(1)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowSystemMenuHint|Qt.WindowMinMaxButtonsHint)
        self.setWindowModality(Qt.ApplicationModal)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        # 定义鼠标移动事件
        if event.buttons() == Qt.LeftButton:
            g_pos = event.globalPos()
            if type(g_pos) != QPoint or type(self._dragPosition) != QPoint:
                return
            self.move(event.globalPos() - self._dragPosition)
            event.accept()


# #####################################################################
# ########################## 无边框透明窗口 #############################
class TransParentWin(NoFrameWin):

    def __init__(self, parent=None):
        NoFrameWin.__init__(self, parent)
        self.setAttribute(Qt.WA_TranslucentBackground)


# #####################################################################
# ########################## MessageBox #############################
class MyMessageBox(QMessageBox):
    """  :type 0(question)  """
    ICON_LIST = [r':/r_icon/pic/r_icon/question.png', ]

    def __init__(self, parent, icon_type=0):
        super(MyMessageBox, self).__init__(parent)
        self.setIconPixmap(QPixmap(MyMessageBox.ICON_LIST[icon_type]))

    def setText(self, q_string):
        raw_text = unicode(q_string)
        n = raw_text.count(u"\n")
        if len(raw_text) > 0 and raw_text[-1] == u"\n":
            n -= 1
        if 0 == n:
            new_string = QString(u"\n") + q_string
        else:
            new_string = q_string
        QMessageBox.setText(self, new_string)


# #####################################################################
IMG_LIST = [u'/auto_back/pic/auto_back/img%03d.jpg' % x for x in range(1, 44)]


# #####################################################################
# ###################### 自动更换背景图片的部件 ###########################
class AutoBackground:

    def __init__(self, widget):
        self._Widget = widget
        self._curr_background = 0
        self._img_list = []

        self._timer_background = QTimer(widget)
        self._Widget.connect(self._timer_background, SIGNAL("timeout()"), self.__slot_background)

    def start(self, rc_img_list, internal=80000, rand=True):
        self._img_list = rc_img_list[:]
        if rand:
            random.shuffle(self._img_list)
        self.set_background(0)
        self._timer_background.start(internal)

    def stop(self):
        self._timer_background.stop()

    def __slot_background(self):
        self._curr_background = (self._curr_background + 1) % len(self._img_list)
        self.set_background(self._curr_background)

    def set_background(self, img_index):
        style_raw = u'''#widget { border-image: url(:%s); }'''
        style = style_raw % (self._img_list[img_index])
        # print(u"Set back style:{}".format(style))
        self._Widget.setStyleSheet(QString(style))


# #####################################################################
# ########################### 主窗口 ###################################
class MainWindow(QMainWindow, Ui_MainWindow, TransParentWin):

    def __init__(self, gui_proc=None, parent=None):
        super(MainWindow, self).__init__(parent)
        self._GUIProc = gui_proc
        self._dragPosition = 0  # 窗口移动用
        self.setupUi(self)

        # 窗口启动
        self.timer_form_load = QTimer(self)
        self.timer_form_load.setSingleShot(True)
        self.connect(self.timer_form_load, SIGNAL("timeout()"), self.slot_form_load)
        self.timer_form_load.start(200)

        # 直接关闭窗口
        self.connect(self.button_close, SIGNAL("clicked()"), self.slot_button_close)

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
        self._account_list = []

    def slot_open_body(self):
        self.label_body.setText(QString(u"载入时间较长，请稍等..."))
        s = QFileDialog.getOpenFileName(self, "Open file dialog", "/", "Text file(*.txt)")
        if len(s) == 0:
            self._body_path = u""
        else:
            self._body_path = unicode(s)
        self.label_body.setText(QString(self._body_path))

    def slot_open_appends(self):
        self.label_append.setText(QString(u"载入时间较长，请稍等..."))
        s_list = QFileDialog.getOpenFileNames(self, "Open file dialog", "/", "All files(*.*)")
        if not s_list:
            self.label_append.setText(QString(u""))
            self._append_list = []
            return
        # 拼接附件文件名
        self._append_list = [unicode(s_list[0])]
        q_s = QString(unicode(s_list[0]).replace(u'\\', u'/'))
        for i in range(1, len(s_list)):
            self._append_list.append(unicode(s_list[i]))
            q_s += QString(u"; ") + QString(unicode(s_list[i]).replace(u'\\', u'/'))
        self.label_append.setText(q_s)

    def slot_open_mail_list(self):
        self.label_maillist.setText(QString(u"载入时间较长，请稍等..."))
        s = QFileDialog.getOpenFileName(self, "Open file dialog", "/", "Excel file(*.xls;*.xlsx)")
        if len(s) == 0:
            self._xls_path = u""
        else:
            self._xls_path = unicode(s)
        self.label_maillist.setText(QString(s))

    def slot_form_load(self):
        print time.strftime('%Y-%m-%d %H:%M:%S')
        print("The form has loaded")
        # 【【【【调用GUI的事件处理函数: 窗口启动】】】】
        if self._GUIProc is not None:
            self._GUIProc.event_form_load()

    def slot_button_close(self):
        self.close()

    def slot_button_cancel(self):
        box = MyMessageBox(self)
        box.setWindowTitle(u"Are you sure to exit?")
        b_save = box.addButton(QString(u"保存"), QMessageBox.ActionRole)
        b_discard = box.addButton(QString(u"不保存"), QMessageBox.ActionRole)
        box.addButton(QString(u"点错了"), QMessageBox.ActionRole)
        box.setText(QString(u"是否保存进度，以便下次启动继续?"))
        box.exec_()

        button = box.clickedButton()
        if button == b_save:
            print(u"Exit and save.\n")
            if self._GUIProc is not None:
                self._GUIProc.event_main_exit_and_save()
            self.close()
        elif button == b_discard:
            print(u"Exit and discard.\n")
            if self._GUIProc is not None:
                self._GUIProc.event_main_exit_and_discard()
            self.close()

    def _set_account_list_sender_name(self, sender_name):
        # 返回一个账户结构体的列表，没有则返回[]
        for i in range(len(self._account_list)):
            self._account_list[i].sender_name = sender_name

    def _ui_data_check(self):
        if len(unicode(self.lineEdit_Sub.text())) == 0:
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
           and col_str.isalpha() and 1 <= int(start_str) <= int(end_str) <= 100:
            pass
        else:
            QMessageBox.critical(self, u"Input Error", QString(u"请正确输入Excel表格中从表的起始及列名"))
            return False

        if len(unicode(self.lineEdit_Sender_Name.text())) == 0:
            QMessageBox.critical(self, u"Input Error", QString(u"请输入发件人"))
            return False

        if self.listWidget.count() == 0:
            QMessageBox.critical(self, u"Input Error", QString(u"请输添加发送账号"))
            return False

        return True

    def get_ui_data_to_memory(self):
        self._sub = unicode(self.lineEdit_Sub.text())
        # xls表格位置选择
        txt_from = unicode(self.lineEdit_Xls_From.text())
        txt_to = unicode(self.lineEdit_Xls_To.text())
        if txt_from.isdigit() and txt_to.isdigit():
            start = int(txt_from)
            end = int(txt_to)
            self._xls_selected_list = range(start, end + 1)
        else:
            self._xls_selected_list = []
        self._xls_col_name = unicode(self.lineEdit_Xls_Col.text())
        self._sender_name = unicode(self.lineEdit_Sender_Name.text())
        self._speed_each_hour = self.spinBox_Each_Hour.value()
        self._speed_each_time = self.spinBox_Each_Time.value()
        self._set_account_list_sender_name(self._sender_name)

        print(u"sub = {}\nbody_path = {}\nappend_list = {}\npath_xls = {}".format(self._sub, self._body_path, self._append_list, self._xls_path))
        print(u"selected = {}, col_name = {}, sender_name = {}".format(self._xls_selected_list, self._xls_col_name, self._sender_name))
        print(u"Speed each hour = {}, each time = {}".format(self._speed_each_hour, self._speed_each_time))
        for i, account in enumerate(self._account_list):
            print(u"Account[{}] = {}".format(i, account))

    def slot_button_run(self):
        if not self._ui_data_check():
            return

        if self._GUIProc is not None:
            # 【【【【调用GUI的事件处理函数: 开始发送】】】】
            self._GUIProc.event_start_send()

    def account_add(self):
        # 弹出添加账户界面
        new_win = AccountWindow()
        if not new_win.exec_():
            print(u"User cancel add account.")
            return
        print(u"User try add an account {}.".format(new_win.user))
        for account in self._account_list:
            if account.user == new_win.user:
                QMessageBox.critical(self, u"Input Error", QString(u"已存在该账户，要添加请先删除"))
                return
        self._account_list.append(Account(new_win.user, new_win.passwd, new_win.host, u""))
        self.listWidget.addItem(QString(new_win.user))

    def account_del(self):
        if self.listWidget.currentRow() < 0:
            return
        user_del = unicode(self.listWidget.item(self.listWidget.currentRow()).text())
        print(u"User del account[{}] {}".format(self.listWidget.currentRow(), user_del))
        for i, account in enumerate(self._account_list):
            if account.user == user_del:
                del(self._account_list[i])
                break
        self.listWidget.takeItem(self.listWidget.currentRow())


# #######################################################################################
# ################################ GUI主流程 启动及事件处理 ################################
# #######################################################################################
class GUIMain(UIInterface, MainWindow):

    def __init__(self, parent=None):
        UIInterface.__init__(self)
        MainWindow.__init__(self, self)
        self.event_init_ui_timer(GUITimer(self))
        self._progress_win = None
        self._ndr_win = None

    def proc_err_same_program(self):
        QMessageBox.critical(self, u"Program Error", QString(u"已经有另一个相同的程序在运行！\n请先停止该程序"))
        self.close()

    def proc_err_before_load(self, err, err_info):
        QMessageBox.critical(self, u"Fatal Error", QString(err_info))
        self.close()

    def proc_ask_if_recover(self, last_success_num, last_failed_num, last_not_sent):
        ret = False
        box = MyMessageBox(self)
        box.setWindowTitle(u"Recover or not")
        b_recover = box.addButton(QString(u"继续上次的"), QMessageBox.ActionRole)
        box.addButton(QString(u"开始新任务"), QMessageBox.ActionRole)

        box.setText(QString(u"检测到上次退出的发送情况:\n"
                            u"成功{}，  失败{}，  未发送{}\n"
                            u"要载入上次的进度吗？已发送的邮件不会再发送".format(
                             last_success_num, last_failed_num, last_not_sent)))
        box.exec_()

        button = box.clickedButton()
        if button == b_recover:
            ret = True
            print(u"The progress will recover")
        else:
            print(u"User cancel recover")
        return ret

    def proc_ask_if_reload_ui(self, mail_sub):
        ret = False
        box = MyMessageBox(self)
        box.setWindowTitle(u"Reload or not")
        b_recover = box.addButton(QString(u"恢复上次"), QMessageBox.ActionRole)
        box.addButton(QString(u"开始新任务"), QMessageBox.ActionRole)

        box.setText(QString(u"检测到上次保存了邮件内容\n"
                            u"标题：{}\n"
                            u"要载入上次的邮件内容吗？".format(mail_sub)))
        box.exec_()

        button = box.clickedButton()
        if button == b_recover:
            ret = True
            print(u"The progress will reload")
        else:
            print(u"User cancel reload")
        return ret

    def proc_reload_tmp_data_to_ui(self, data):
        self._sub = data["Sub"]
        self.lineEdit_Sub.setText(QString(self._sub))
        self._body_path = data["Body"]
        self.label_body.setText(QString(self._body_path))

        self._append_list = data["AppendList"][:]
        append_str = u";".join(self._append_list)
        append_str = append_str.replace("\\", "/")
        self.label_append.setText(QString(append_str))

        self._xls_path = data["XlsPath"]
        self.label_maillist.setText(QString(self._xls_path))
        self._xls_col_name = data["ColName"]
        self.lineEdit_Xls_Col.setText(QString(self._xls_col_name))

        self._xls_selected_list = data["SelectedList"][:]
        if self._xls_selected_list:
            sec_min = self._xls_selected_list[0]
            sec_max = self._xls_selected_list[-1]
        else:
            sec_min = u""
            sec_max = u""
        self.lineEdit_Xls_From.setText(QString(unicode(sec_min)))
        self.lineEdit_Xls_To.setText(QString(unicode(sec_max)))

        self._speed_each_hour = data["EachHour"]
        self.spinBox_Each_Hour.setValue(self._speed_each_hour)
        self._speed_each_time = data["EachTime"]
        self.spinBox_Each_Time.setValue(self._speed_each_time)

    def proc_reload_account_list_to_ui(self, account_list):
        self._account_list = account_list[:]
        for account in self._account_list:
            self.listWidget.addItem(QString(account.user))
        if account_list:
            self.lineEdit_Sender_Name.setText(QString(account_list[0].sender_name))

    def proc_get_all_ui_data(self):
        self.get_ui_data_to_memory()
        data = {"Sub": self._sub, "Body": self._body_path, "AppendList": self._append_list[:],
                "XlsPath": self._xls_path, "ColName": self._xls_col_name, "SelectedList": self._xls_selected_list[:],
                "EachHour": self._speed_each_hour, "EachTime": self._speed_each_time,
                "AccountList": self._account_list[:]}
        return data

    def proc_err_before_send(self, err, err_info):
        QMessageBox.critical(self, u"Input Error", QString(err_info))

    def proc_confirm_before_send(self, last_success_num, last_failed_num, will_send_num, all_sheets, select_list):
        info1 = u"本次将发送邮件{}封，\n上次成功发送的{}封邮件不会重复发送.\n".format(will_send_num, last_success_num)
        info2 = u"以下表格中的邮箱将被发送:\n"
        selected_sheets = []
        for i in select_list:
            selected_sheets.append(all_sheets[i-1])  # 用户的选择是从1开始的
        info_sheets = u"\n".join(selected_sheets)
        info3 = u"\n\n【普通账户大量群发邮件有被封号风险】\n您确定仍要继续吗？"

        button = QMessageBox.question(self, u"Confirm",
                                      QString(info1 + info2 + info_sheets + info3),
                                      QMessageBox.Ok | QMessageBox.Cancel,
                                      QMessageBox.Ok)
        if button == QMessageBox.Ok:
            return True
        print(u"User cancel before send.")
        return False

    def proc_exec_progress_window(self, init_progress):
        # 弹出进度条界面
        self.setHidden(True)
        self._progress_win = ProgressWindow(self)
        self._progress_win.set_progress_bar(init_progress[0], init_progress[1], init_progress[2])
        ret = self._progress_win.exec_()
        if ret:
            print(u"Exit progress window normal, ret = {}".format(ret))
            ret = True
        else:
            print(u"Exit progress window pause or abnormal, ret = {}".format(ret))
            ret = False
        self.setHidden(False)
        return ret

    def proc_update_progress(self, progress_tuple=None, progress_info=None):
        # 更新进度条窗口上的所有信息
        if progress_tuple is not None:
            self._progress_win.set_progress_bar(progress_tuple[0], progress_tuple[1], progress_tuple[2])
        if progress_info is not None:
            self._progress_win.progress_log(progress_info + u"\n")

    def proc_finish_with_failed(self, success_num, failed_num, not_sent_num):
        self._progress_win.set_button_text_finish()

    def proc_finish_all_success(self, success_num, failed_num, not_sent_num):
        self._progress_win.set_button_text_finish()

    def proc_err_fatal_run(self, err, err_info):
        self._progress_win.exit_with_error(unicode(err_info))

    def proc_err_auto_retry(self, err, err_info):
        self._progress_win.mention_and_auto_close(unicode(err_info))

    def proc_ask_if_ndr(self):
        info = u"发送成功的邮件可能会被对方退回来，是否接收系统退信？" \
               u"以便进一步分析邮件退信的原因，同时你也可以再次尝试发送退信的邮件\n" \
               u"注意退信窗口不会自动关闭，建议时间15分钟(视邮件多少而定)，您也可以提前关闭"
        button = QMessageBox.question(self, u"Receive bounce E-mail ?",
                                      QString(info),
                                      QMessageBox.Ok | QMessageBox.Cancel,
                                      QMessageBox.Ok)
        if button == QMessageBox.Ok:
            return True
        return False

    def proc_input_recv_host(self, user_list):
        # 返回字典{user:host}  host对于不支持的账户填u""，与发送服务器一致则填None 用Account.get_recv_host辅助
        dict_ret = {}
        for user in user_list:
            win = RecvHostWindow(user)
            win.exec_()
            dict_ret[win.user] = win.host
        return dict_ret

    def proc_exec_ndr_win(self, send_finish_datetime):
        delta_seconds = (datetime.datetime.now() - send_finish_datetime).seconds
        minute = delta_seconds / 60
        second = delta_seconds % 60

        self.setHidden(True)
        self._ndr_win = NdrWindow(self, minute, second)
        self._ndr_win.exec_()
        self.setHidden(False)

    def proc_ndr_refresh_data(self, err_info, ndr_data_list, ndr_all_count, has_finish_a_loop):
        # ndr_data_list:[[时间，退回的邮箱， 出错信息， 建议]...]
        if len(err_info) > 0:
            self._ndr_win.append_text(err_info)
        for ndr_data in ndr_data_list:
            self._ndr_win.add_one_row(ndr_data[1], ndr_data[3], ndr_data[2])


# ########################### 添加账户窗口 ############################
class AccountWindow(QDialog, Ui_Dialog_Account, NoFrameWin):
    def __init__(self, parent=None):
        super(AccountWindow, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # 确定/取消按钮
        self.connect(self.pushButton, SIGNAL("clicked()"), self.add_account)
        self.connect(self.pushButton_cancel, SIGNAL("clicked()"), self.cancel_account)
        self.connect(self.lineEdit_user, SIGNAL("editingFinished()"), self._auto_set_host)

        # 账户数据
        self.user = u""
        self.passwd = u""
        self.host = u""

    def add_account(self):
        user = unicode(self.lineEdit_user.text())
        passwd = unicode(self.lineEdit_passwd.text())
        host = unicode(self.lineEdit_host.text())

        if len(user) == 0 or len(passwd) == 0 or len(host) == 0:
            QMessageBox.critical(self, u"Input Error", QString(u"请输入完整信息"))
            return

        if -1 == user.find(u"@"):
            QMessageBox.critical(self, u"Input Error", QString(u"邮箱账号有误，应为xxx@@xxx.xxx"))
            return

        # 询问用户是否需要验证能否登录
        button = QMessageBox.question(self, u"Need Login test?",
                                      QString(u"需要验证该账号能否登录吗？"),
                                      QMessageBox.Ok | QMessageBox.Cancel,
                                      QMessageBox.Ok)
        if button == QMessageBox.Cancel:
            self.user = user
            self.passwd = passwd
            self.host = host
            self.accept()      # 退出添加账户窗口
        elif button == QMessageBox.Ok:
            # 登录验证
            err, err_info = UIInterface.check_account_login(user, passwd, host)
            if 0 == err:
                self.user = user
                self.passwd = passwd
                self.host = host
                QMessageBox.information(self, u"Success", QString(u"验证成功!"))
                self.accept()  # 退出添加账户窗口
            else:
                QMessageBox.information(self, u"Failed", QString(u"验证失败:{}".format(err_info)))

    def cancel_account(self):
        self.reject()

    def _auto_set_host(self):
        user = unicode(self.lineEdit_user.text())
        host = Account.get_send_host(user)
        if host != u"":
            self.lineEdit_host.setText(QString(host))


# ########################### 进度条窗口 ############################
class ProgressWindow(QDialog, Ui_Dialog_Progress, NoFrameWin):

    def __init__(self, gui_proc=None, parent=None):
        super(ProgressWindow, self).__init__(parent)
        self._GUIProc = gui_proc
        self._timer_close = None  # 定时自动关闭MsgBox
        self._box = None
        self._button_is_finish = False  # 发送完成按钮会变成finish
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setupUi(self)
        self._background = AutoBackground(self.widget)
        self._background.start(IMG_LIST, 53400)

        # 暂停按钮
        self.connect(self.pushButton, SIGNAL("clicked()"), self.slot_pause)

    def slot_pause(self):
        if self._GUIProc is not None:
            # 【【【【调用GUI的事件处理函数: 用户暂停发送进度】】】】
            self._GUIProc.event_user_cancel_progress()
        if not self._button_is_finish:
            QMessageBox.information(self, u"Information",
                                    QString(u'如果想重发已失败的邮件，增加邮件或者修改内容，\n'
                                            u'可以再次点击"开始"，已发送成功的邮件不会重复发送'))
            self.reject()           # 用户暂停
        else:
            self.accept()  # 发送完成

    def set_progress_bar(self, success_num, failed_num, not_sent_num):
        self.label_has_sent.setText(QString(unicode(success_num)))
        self.label_failed_sent.setText(QString(unicode(failed_num)))
        self.label_not_sent.setText(QString(unicode(not_sent_num)))

        all_num = success_num + failed_num + not_sent_num
        show_num = success_num + failed_num
        if all_num > 0:
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(all_num)
            self.progressBar.setValue(show_num)
        else:
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(100)
            self.progressBar.setValue(100)

    def progress_log(self, content):
        self.textEdit.append(QString(unicode(content)))

    def set_button_text_finish(self):
        self._button_is_finish = True
        self.pushButton.setText(QString(u"完成"))
        beep()

    def exit_with_error(self, err_info=u""):
        if err_info != u"":
            QMessageBox.critical(self, u"Fatal Error", QString(err_info))
        self.accept()

    def mention_and_auto_close(self, err_info=u"", delay=10000):
        if err_info != u"":
            box = MyMessageBox(self)
            self._box = box
            self._timer_close = QTimer(self)
            self._timer_close.setSingleShot(True)
            self.connect(self._timer_close, SIGNAL("timeout()"), self._close_msg_box)
            self._timer_close.start(delay)

            box.setWindowTitle(u"Error")
            box.addButton(QString(u"自动重试"), QMessageBox.ActionRole)
            box.setText(QString(err_info))
            box.show()

    def _close_msg_box(self):
        self._box.close()
        self._timer_close.disconnect(self._timer_close, SIGNAL("timeout()"), self._close_msg_box)


# ########################### 设置IMAP服务器窗口 ############################
class RecvHostWindow(QDialog, Ui_Dialog_RecvHost, NoFrameWin):

    def __init__(self, account_user, parent=None):
        super(RecvHostWindow, self).__init__(parent)
        self.user = account_user
        self.host = u""
        self._host_list = []
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        self.label_user.setText(QString(unicode(account_user)))
        self._init_combobox()

        self.connect(self.pushButton, SIGNAL("clicked()"), self.slot_set_host)

    def _init_combobox(self):
        # 把支持的host加入combobox
        host_list = [each_host for domain, each_host in Account.RECV_HOSTS.iteritems()]
        host_list = list(set(host_list))
        self._host_list = host_list
        for each_host in host_list:
            self.comboBox.addItem(QString(each_host))
        self.comboBox.addItem(QString(u"与发送服务器一样"))
        self.comboBox.addItem(QString(u"其他 （不支持接收退信）"))

        host = Account.get_recv_host(self.user)
        if host == "":
            self.comboBox.setCurrentIndex(len(host_list)+1)
        else:
            self.comboBox.setCurrentIndex(host_list.index(host))

    def slot_set_host(self):
        index = self.comboBox.currentIndex()
        len_host_list = len(self._host_list)
        if index < len_host_list:
            self.host = self._host_list[index]
        elif index == len_host_list:
            self.host = None   # 代表和发送服务器一样
        else:
            self.host = u""    # 代表不支持
        print(u"User select {} recv host {}".format(self.user, repr(self.host)))
        self.accept()


# ########################### 退信窗口 ############################
class NdrWindow(QDialog, Ui_Dialog_Ndr, NoFrameWin):

    def __init__(self, gui_proc=None, lcd_minute=0, lcd_second=0, parent=None):
        super(NdrWindow, self).__init__(parent)
        self._GUIProc = gui_proc
        self._has_press_pause = False       # 按两次暂停才退出窗口，用来标记
        self._lcd_minute = lcd_minute
        self._lcd_second = lcd_second
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.set_lcd_time(lcd_minute, lcd_second)
        self._init_table()
        self.connect(self.pushButton, SIGNAL("clicked()"), self.slot_stop_ndr)
        self.connect(self.pushButton_Save, SIGNAL("clicked()"), self.slot_save_excel)

        # 定时刷新时间
        self._timer_refresh_lcd = QTimer()
        self.connect(self._timer_refresh_lcd, SIGNAL("timeout()"), self.slot_refresh_lcd)
        self._timer_refresh_lcd.start(1000)

    def _init_table(self):
        # self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnWidth(0, 250)
        self.tableWidget.setColumnWidth(1, 300)
        self.tableWidget.setColumnWidth(2, 380)

        header = [QString(u"被退信的邮箱"), QString(u"原因/建议"), QString(u"详细信息")]
        self.tableWidget.setHorizontalHeaderLabels(header)

    def slot_stop_ndr(self):
        if not self._has_press_pause:
            self._has_press_pause = True
            self.pushButton.setText(QString(u"完成"))
            self._timer_refresh_lcd.stop()
            # 【【【【调用GUI的事件处理函数: 终止接收退信】】】】
            if self._GUIProc is not None:
                self._GUIProc.event_user_cancel_ndr()
            self.append_text(u"用户终止接收退信\n\n")
        else:
            info = u"如果你想重试退信的邮件，可以修改发送信息然后再次开始"
            QMessageBox.information(self, u"Information", QString(info))
            self.accept()

    def slot_save_excel(self):
        if not self._has_press_pause:
            info = u"保存表格之前请先停止接收退信"
            QMessageBox.warning(self, u"Information", QString(info))
        else:
            # 【【【【调用GUI的事件处理函数: 保存退信】】】】
            if self._GUIProc is not None:
                err, err_info = self._GUIProc.event_save_ndr_to_excel()
                if err != 0:
                    QMessageBox.warning(self, u"Error", QString(err_info))
                else:
                    self.append_text(u"已保存表格到：{}".format(err_info))

    def add_one_row(self, mail, suggest, more_info):
        old_row_count = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(old_row_count + 1)
        self.tableWidget.setItem(old_row_count, 0, QTableWidgetItem(QString(mail)))
        self.tableWidget.setItem(old_row_count, 1, QTableWidgetItem(QString(suggest)))
        self.tableWidget.setItem(old_row_count, 2, QTableWidgetItem(QString(more_info)))
        self.label_NdrNum.setText(QString(unicode(old_row_count + 1)))

    def append_text(self, text):
        # self.textEdit.insertPlainText(QString(unicode(text)))
        if len(text) > 0 and text[-1] == '\n':
            text_append = text[:-1]
        else:
            text_append = text
        self.textEdit.append(QString(text_append))

    @staticmethod
    def _time_convert(minute, second):
        m = minute
        s = second
        if s >= 60:
            m += int(s / 60)
            s %= 60
        if m > 99:
            m = 99
            s = 99
        return m, s

    def set_lcd_time(self, minute, second):
        m, s = self._time_convert(minute, second)
        self.lcdNumber.display(QString(u"%02d:%02d" % (m, s)))

    def slot_refresh_lcd(self):
        self._lcd_minute, self._lcd_second = self._time_convert(self._lcd_minute, self._lcd_second + 1)
        self.lcdNumber.display(QString(u"%02d:%02d" % (self._lcd_minute, self._lcd_second)))


def beep():
    if is_windows_system():
        winsound.MessageBeep(0)
    else:
        print("\a")


def test_ndr_win():
    app = QApplication(sys.argv)
    win = NdrWindow()
    win.show()
    app.exec_()


def test_recv_win():
    app = QApplication(sys.argv)
    dict_ret = {}
    user_list = ["liangjinchao@163.com", "abcdefg@hust.edu.cn", "sys@d3p.com"]
    for user in user_list:
        win = RecvHostWindow(user)
        win.exec_()
        dict_ret[win.user] = win.host
    print(dict_ret)


def test_ui_progress():
    app = QApplication(sys.argv)
    win = ProgressWindow()
    win.set_progress_bar(2, 2, 2)
    win.show()
    app.exec_()


def test_ui_progress_return():
    app = QApplication(sys.argv)
    win = ProgressWindow()
    ret = win.exec_()
    if ret:
        print(u"Exit progress window normal, ret = {}".format(ret))
    else:
        print(u"Exit progress window abnormal, ret = {}".format(ret))


def test_account_win():
    app = QApplication(sys.argv)
    win = AccountWindow()
    win.show()
    app.exec_()


def test_main_win():
    app = QApplication(sys.argv)
    win = MainWindow(None)
    win.show()
    app.exec_()


def message_err_when_init(content, title=u"Fatal Error"):
    app = QApplication(sys.argv)
    win = QDialog()
    QMessageBox.critical(win, title, QString(unicode(content)))
    win.close()
    app.exit()


def main_init():
    print(u"Check same program.")
    sys.stdout.flush()
    if check_program_has_same(PROGRAM_UNIQUE_PORT):
        message_err_when_init(u"已经有另一个相同的程序在运行！\n请先停止该程序")
        exit(1)
    print(u"Init the log.")
    logging_init("Send_Mail.log")


def main_fini():
    logging_fini()
    check_program_has_same_fini()


# Main Function
def main():
    main_init()
    QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))
    app = QApplication(sys.argv)
    # app.setStyle("cleanlooks")
    # app.setStyle("plastique")
    win = GUIMain()
    win.show()
    app.exec_()
    main_fini()


if __name__=='__main__':
    main()
    #test_ui_progress()
    #test_ui_progress_return()
    #test_gui_timer()
    #test_ndr_win()
    #test_recv_win()
    #test_account_win()
