#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import random
import copy
import xlrd
import smtplib
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from mylog import *
from err_code import *
from mail_list import *

import pdb;  pdb.set_trace()


class Account:
    def __init__(self, mail_user, mail_passwd, mail_host, sender_name):
        # mail_host 不知道就填空，用auto_get_host获取
        self.user = mail_user
        self.passwd = mail_passwd
        self.host = mail_host
        self.sender_name = sender_name

    def check(self):
        pass

    def auto_get_host(self):
        pass


class AccountsMange:
    def __init__(self, account_list=None):
        if account_list is not None:
            self._AccountList = account_list[:]
        else:
            self._AccountList = []
        self._CurrAccountId = 0

        # 一旦出现一次"发送过多"错误就被置True
        self._send_too_many_mark = False

    def add(self, mail_user, mail_passwd, mail_host, sender_name):
        # 用户暂停下来添加账户 未做优化
        account = Account(mail_user, mail_passwd, mail_host, sender_name)
        self._AccountList.append(account)

    def delete(self, mail_user):
        # 用户暂停下来删除账户 未做优化
        for i, each_account in enumerate(self._AccountList):
            if each_account.user == mail_user:
                del(self._AccountList[i])
                break

    def get_an_account(self):
        # 每调一次就切换一个账号
        account = copy.copy(self._AccountList[self._CurrAccountId])
        self._CurrAccountId = (self._CurrAccountId + 1) % len(self._AccountList)
        return account

    def send_too_many_proc(self, origin_err_info):
        # 每当轮询到第一个账户失败时就一直等，除非是第一次发送第一个账号失败 需要用self._PolicyTooManyMark
        err_info = origin_err_info
        if 1 == len(self._AccountList):
            self._send_too_many_mark = True
            err = ERROR_SEND_TOO_MANY_NEED_WAIT
        elif 0 == self._CurrAccountId and self._send_too_many_mark:
            # 不换账号，继续尝试第一个，直到第一个成功
            err = ERROR_SEND_TOO_MANY_NEED_WAIT
            err_info = u"所有邮箱都已发送太多邮件被拒，将从第一个开始重新尝试"
        else:
            self._CurrAccountId = (self._CurrAccountId + 1) % len(self._AccountList)
            account_next = self._AccountList[self._CurrAccountId]
            err = ERROR_SEND_TOO_MANY
            err_info += u"\n切换到账号{}".format(account_next.user)
            # 只要进一次这里就永远被标记
            self._send_too_many_mark = True
        return err, err_info


class MailContent:
    """  邮件内容：主题、正文、附件 """
    SPECIAL_STR_PATTERN = r'\{##[A-Z]##\}'     # 邮件正文或标题中的特殊字符

    def __init__(self, mail_sub, mail_body, mail_append_list):
        self._Sub = mail_sub    # 原始主题
        self._Body = mail_body  # 原始正文
        self._AppendList = mail_append_list

        # 暂存附件内容不用每次读取
        self._msg_append_list = []

        # 判断内容里面是否有特殊含义的字符需要替换（这样每封邮件都不一样，需要一封封发送）
        self._bool_special = self._is_special_content(self._Sub, self._Body)

    def sub(self, mail_matrix=None, mail_address=""):
        if not self.is_special_content():
            return self._Sub
        # 获取实际位置然后调用替换
        data_tmp = mail_matrix.get_data_by_name(mail_address)
        if data_tmp:
            logging_warn(u"Replace {}`s content is not match {}".format(mail_address, data_tmp[0]))
            return self.text_replace(self._Sub, data_tmp)
        return self._Sub

    def body(self, mail_matrix=None, mail_address=""):
        if not self.is_special_content():
            return self._Body
        # 获取实际位置然后调用替换
        data_tmp = mail_matrix.get_data_by_name(mail_address)
        if data_tmp:
            # 再进一步检查防止出错
            if data_tmp[0] != mail_address:
                logging_warn(u"Replace {}`s content is not match {}".format(mail_address, data_tmp[0]))
            return self.text_replace(self._Body, data_tmp)
        return self._Body

    def append_list(self):
        return self._AppendList

    def msg_append_list(self):
        return self._msg_append_list

    def read_append(self):
        """ 读取附件，失败则暂停 """
        if self._msg_append_list:   # 如果已经读取了就返回
            return ERROR_SUCCESS, u""
        ret = ERROR_SUCCESS, u"读取附件成功"
        for each_append in self._AppendList:
            try:
                f = open(each_append, 'rb')
            except Exception, e:
                ret = ERROR_OPEN_APPEND_FAILED, u"无法打开附件: {} \n{}".format(each_append, e)
                break
            try:
                file_content = f.read()
            except Exception, e:
                ret = ERROR_READ_APPEND_FAILED, u"无法读取附件: {} \n{}".format(each_append, e)
                f.close()
                break
            f.close()
            msg_append = MIMEApplication(file_content)
            f_basename = os.path.basename(each_append).encode(MailProc.ENCODE)
            msg_append.add_header('Content-Disposition', 'attachment', filename=f_basename)
            self._msg_append_list.append(msg_append)
        logging(ret[1])
        return ret

    @staticmethod
    def text_replace(text, data_list):
        text_ret = text
        matches = re.findall(MailContent.SPECIAL_STR_PATTERN, text_ret)
        if not matches:
            return text_ret
        matches = list(set(matches))
        for each_match in matches:
            index = ord(each_match[3]) - ord('A') + 1
            if 0 < index < len(data_list):
                data_tmp = data_list[index]
                if type(data_tmp) == unicode or type(data_tmp) == str:
                    text_ret = text_ret.replace(text_ret, data_tmp)
                else:
                    text_ret = text_ret.replace(text_ret, u"")
            else:
                text_ret = text_ret.replace(text_ret, u"")
        return text_ret

    @staticmethod
    def _is_special_content(sub, body):
        """ 真正作判断的函数 """
        if re.search(MailContent.SPECIAL_STR_PATTERN, sub) is None and \
           re.search(MailContent.SPECIAL_STR_PATTERN, body) is None:
            return False
        return True

    def is_special_content(self):
        """  判断内容里面是否有特殊含义的字符需要替换（这样每封邮件都不一样，需要一封封发送）  """
        return self._bool_special


class SimpleMatrix:
    """ 邮件矩阵的基类 """
    def __init__(self, max_send_a_loop=0, mail_matrix=None):
        self._curr_line = 0
        self._curr_row = 0
        self._max_send_a_loop = max_send_a_loop

        if mail_matrix is not None:
            self._MatrixData = mail_matrix
        else:
            self._MatrixData = []

        all_need_send = 0
        for each_line in self._MatrixData:
            all_need_send += len(each_line)

        # 进度条
        self._success_num = 0
        self._failed_num = 0
        self._not_send_num = all_need_send

    def init(self):
        pass

    def set_max_send_a_loop(self, max_send_a_loop):
        self._max_send_a_loop = max_send_a_loop

    def group_mail_get(self):
        if self._curr_line >= len(self._MatrixData):
            return []
        return self._MatrixData[self._curr_line][self._curr_row: self._curr_row + self._max_send_a_loop]

    def group_mail_step(self, failed_mail=None):
        self._curr_row += self._max_send_a_loop
        if self._curr_row >= len(self._MatrixData[self._curr_line]):
            self._curr_row = 0
            self._curr_line += 1
        if failed_mail is None or failed_mail:
            self._success_num += self._max_send_a_loop
            self._not_send_num -= self._max_send_a_loop
        else:
            self._success_num += self._max_send_a_loop - len(failed_mail)
            self._failed_num += len(failed_mail)
            self._not_send_num -= self._max_send_a_loop

    def get_data_by_name(self, mail_name):
        # 返回一个字符串列表，[该位置的收件人名，表格中的A, B, C...]
        for list_line in self._MatrixData:
            for dat in list_line:
                if dat == mail_name:
                    return [dat]
        return []

    def curr_progress(self):
        return self._success_num, self._failed_num, self._not_send_num


class XlsMatrix:
    """ 由xls表格实现的邮件矩阵          从xls表格导入收件人信息存为矩阵(三维)
    1. 为MailProc发送时提供发件人列表   (策略:各域名邮箱均匀分布)
    2. 统计已成功/失败/未发送的邮件数量
    3. 保存(已成功和已失败的邮件)到MailDB，重启时从DB过滤已成功；提供clear_db供任务完成时调用
    """
    def __init__(self, max_send_a_loop, xls_path):
        self._MaxSendALoop = max_send_a_loop
        self._Path = xls_path
        self._MailColNo = 0
        self._SelectedSheets = []

        self._xls = None
        self._mails_not_sent = []   # 待发送的
        self._mails_has_sent = []
        self._mails_sent_failed = []

    def read_sheets_before_init(self):     # 可能会出异常 打开失败，调用者注意
        self._xls = xlrd.open_workbook(self._Path)
        return self._xls.sheet_names()

    # 注意selected_sheets从1开始，与用户看到的一致，与表格模块不一致 列名： 'A' 'B' ..
    # 检查是否有重复的邮箱
    def init(self, user_selected_sheets, mail_which_col):
        self._init_set_data(user_selected_sheets, mail_which_col)
        err, err_info = self._create_not_sent_list()
        return err, err_info

    def _init_set_data(self, user_selected_sheets, mail_which_col):
        self._MailColNo = ord(mail_which_col.upper()) - ord('A')
        self._SelectedSheets = user_selected_sheets[:]
        for i in range(len(self._SelectedSheets)):
            self._SelectedSheets[i] -= 1

    def _get_xls_mails(self):
        # 从xls中获取收件人数据 [有序]
        mails_read = []
        for sheet_index in self._SelectedSheets:
            sheet = self._xls.sheets()[sheet_index]                # 取第几张sheet
            if self._MailColNo >= sheet.ncols:                   #如果这张表没有该列则跳过
                continue
            for each_ceil in sheet.col_values(self._MailColNo):    # sheet.col_values(列号) 获取sheet内一列
                if "" != str_find_mailbox(each_ceil):
                    mails_read.append(each_ceil)
        logging("Get {} mails from excel.".format(len(mails_read)))
        return mails_read

    @staticmethod
    def _random_sort_mails(mails_input):
        mails_origin = mails_input[:]
        mails_new = []
        logging(u"Origin mail list is:\n{}".format(mails_origin))
        while mails_origin:   # 不断从mails_origin移动到mails_new直到mails_origin为空
            index_r = random.randint(0, len(mails_origin)-1)
            # 从mails_origin头开始选择与mails_origin[index_r]相同域名的邮箱
            for i, each_mail in enumerate(mails_origin):
                if str_is_domain_equal(each_mail, mails_origin[index_r]):
                    mails_new.append(each_mail)
                    mails_origin.pop(i)
                    break
        logging(u"New mail list is:\n{}".format(mails_new))
        return mails_new

    def _create_not_sent_list(self):
        # 根据db的已发送和当前读取的生成待发送列表
        mails_read = self._get_xls_mails()
        try:
            last_sent, last_failed, last_not_sent = self.get_last_exit_data()
        except Exception, e:
            err = ERROR_READ_MATRIX_DB_FAILED
            err_info = u"读取数据库中的已发送数据失败 {}".format(e)
            return err, err_info

        for each_last_sent in last_sent:
            if each_last_sent in mails_read:
                mails_read.remove(each_last_sent)
        if mails_read:
            self._mails_not_sent = []

        mails_new = self._random_sort_mails(mails_read)
        self._mails_not_sent = mails_new
        return ERROR_SUCCESS, u""

    def set_max_send_a_loop(self, max_send_a_loop):
        self._MaxSendALoop = max_send_a_loop

    def group_mail_get(self):
        return self._mails_not_sent[0: self._MaxSendALoop]

    def group_mail_step(self, failed_mails=None):
        # 进行成功/失败数量统计
        curr_mails = self._mails_not_sent[0: self._MaxSendALoop]
        if failed_mails is None:
            self._mails_has_sent += curr_mails
        else:
            self._mails_has_sent += list(set(curr_mails) - set(failed_mails))
            self._mails_sent_failed += failed_mails

        # step 为下次获取准备
        if len(self._mails_not_sent) <= self._MaxSendALoop:
            self._mails_not_sent = []
        else:
            for i in range(self._MaxSendALoop):
                self._mails_not_sent.pop(0)

    @staticmethod
    def get_data_by_name(mail_name):   # 暂不实现
        return mail_name

    def curr_progress(self):
        success_num = len(self._mails_has_sent)
        failed_num = len(self._mails_sent_failed)
        not_send = len(self._mails_not_sent)
        return success_num, failed_num, not_send

    ########################## 数据库相关操作 ###########################

    def clear_db(self):    # ?????????????????????????????
        pass

    def get_last_exit_data(self):
        # 从数据库中获取上次的情况(已发，失败，未发)列表                      ???????????????
        return [], [], []


class MailProc:
    """ 发送邮件的主流程 """
    MAX_SPECIAL_SEND_A_LOOP = 5                  # 特殊邮件一回合连续发送次数
    MAILS_TRY_AGAIN_WAIT_TIME = 5                # 出现临时错误重试的时间间隔 秒
    MAILS_UNKNOWN_ERROR_MAX_CONTINUE_TIME = 20   # 连续出现未知错误的最大次数
    ENCODE = "gb18030"

    def __init__(self, mail_matrix, accounts_manager, mail_sub, mail_body, mail_append_list):
        """ mail_matrix  邮件矩阵对象 MailMatrix,
            accounts_list Account对象列表，多个账户轮换,
            mail_sub 邮件主题,
            mail_body 邮件正文(html)
            mail_append_list 附件列表(路径名) """
        self._MailMatrix = mail_matrix
        self._AccountsMange = accounts_manager
        self._Content = MailContent(mail_sub, mail_body, mail_append_list)

        # 每回合发送邮件的数量
        if self._Content.is_special_content():
            self._MailMatrix.set_max_send_a_loop(MailProc.MAX_SPECIAL_SEND_A_LOOP)

        # 当前发送账号
        self._curr_account_id = 0
        # 未知错误连续发生的次数
        self._unknown_error_continue_times = 0

        # 当第一次尝试完第二个账户该标志位就会一直被置True
        self._PolicyTooManyMark = False

    @staticmethod
    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(),
                           addr.encode('utf-8') if isinstance(addr, unicode) else addr))

    @staticmethod
    def send_one_group(mail_list, account, mail_sub, mail_body, msg_append_list):
        err = ERROR_SUCCESS
        err_info = ""
        fail_mail = []  # 部分发送失败的邮件

        msg = MIMEMultipart()
        msg['Subject'] = mail_sub
        msg['From'] = MailProc._format_addr(u"{}<{}>".format(account.sender_name, account.user))
        msg['BCC'] = ";".join(mail_list)

        msg_text = MIMEText(mail_body, 'html', MailProc.ENCODE)
        msg.attach(msg_text)

        for each_append in msg_append_list:
            msg.attach(each_append)

        logging("Start to send a group.")
        s = smtplib.SMTP()
        try:
            s.connect(account.host)
        except Exception, e:
            err = ERROR_CONNECT_FAILED
            err_info = u"连接{}失败，请检查网络是否通畅\n错误信息: {}".format(account.host, e)
            return err, err_info, fail_mail
        logging_info("Connect {} Success.".format(account.host))

        try:
            s.login(account.user, account.passwd)
        except Exception, e:
            err = ERROR_LOGIN_FAILED
            err_info = u"{}登录失败，账号或密码错误\n{}".format(account.user, e)
            return err, err_info, fail_mail
        logging_info(u"Account {} login Success.".format(account.user))

        try:
            fail_mail = s.sendmail(account.user, mail_list, msg.as_string())
        except smtplib.SMTPRecipientsRefused, e:
            err = ERROR_SEND_TOO_MANY
            err_info = u"当前账号{}发送邮件太多被拒: {}".format(account.user, e)
        except smtplib.SMTPDataError, e:
            err = ERROR_SEND_TOO_MANY
            err_info = u"当前账号{}发送邮件过多被拒: {}".format(account.user, e)
        except smtplib.SMTPServerDisconnected, e:
            err = ERROR_SEND_TOO_MANY
            err_info = u"当前账号{}发送邮件过多被拒绝连接: {}".format(account.user, e)
        except Exception, e:
            err = ERROR_SEND_FAILED_UNKNOWN
            err_info = u"未知原因，暂时发送失败: {}".format(e)
        else:
            fail_mail = fail_mail.keys()
            if len(fail_mail) != 0:
                err = ERROR_SOME_EMAILS_FAILED
                err_info = u"部分邮件发送失败"
        s.close()
        logging("Send to " + repr(mail_list) + " | " + err_info + " | " + repr(fail_mail))

        return err, err_info, fail_mail

    def _send_try(self, mail_list):
        if not self._Content.is_special_content():
            ret = self.send_one_group(mail_list,
                                      self._AccountsMange.get_an_account(),
                                      self._Content.sub(),
                                      self._Content.body(),
                                      self._Content.msg_append_list())
        else:
            # 特殊邮件只能一封封发
            ret = ERROR_SUCCESS, u"", []
            fail_mail = []
            for offset, each_mail in enumerate(mail_list):
                ret = self.send_one_group(each_mail,
                                          self._AccountsMange.get_an_account(),
                                          self._Content.sub(self._MailMatrix, each_mail),
                                          self._Content.body(self._MailMatrix, each_mail),
                                          self._Content.msg_append_list())
                if ERROR_SUCCESS == ret[0]:
                    continue
                elif ERROR_SEND_FAILED_UNKNOWN == ret[0]:
                    fail_mail += each_mail
                else:
                    break
            if len(fail_mail) != 0 and len(fail_mail) != len(mail_list):     # 部分失败的情况
                ret = ERROR_SOME_EMAILS_FAILED, u"部分邮件发送失败", fail_mail
        return ret

    def _send_policy1(self):
        """ 返回：错误码, log信息(显示), 已发送列表, 发送失败列表, (下一个邮件矩阵位置 x, y) """
        # ret默认为异常退出，一封也没发出去，下次将会再次尝试
        ret = {"ErrCode": ERROR_SUCCESS, "ErrLog": "", "SuccessList": [], "FailedList": [],
               "CurrProgress": self._MailMatrix.curr_progress()}  # (成功, 失败, 未发送) 的数量

        err, err_info = self._Content.read_append()
        if ERROR_SUCCESS != err:
            ret["ErrCode"], ret["ErrLog"] = err, err_info
            return ret

        mail_list = self._MailMatrix.group_mail_get()
        if not mail_list:
            ret["ErrCode"], ret["ErrLog"] = ERROR_FINISH, u"所有邮件都已尝试发送"
            return ret

        # 根据发送结果进行本次发送的自我处理
        err, err_info, fail_mail = self._send_try(mail_list)
        ret["ErrCode"], ret["ErrLog"] = err, err_info

        # 全部发送成功
        if ERROR_SUCCESS == err:
            self._MailMatrix.group_mail_step()   # 告诉邮件矩阵已发送成功，下次将给别的收件人
            ret["SuccessList"] = mail_list
            ret["CurrProgress"] = self._MailMatrix.curr_progress()
        # 部分发送成功(除此之外其他情况都是全部失败)
        elif ERROR_SOME_EMAILS_FAILED == err:
            time.sleep(MailProc.MAILS_TRY_AGAIN_WAIT_TIME)
            ret_tmp = self._send_try(fail_mail)
            if ret_tmp[0] == ERROR_SUCCESS:
                ret["ErrCode"], ret["ErrLog"] = ERROR_SUCCESS, ""
                ret["SuccessList"] = mail_list
                ret["FailedList"] = []
                self._MailMatrix.group_mail_step()   # 告诉邮件矩阵当前已发送成功，下次将给别的收件人
            else:
                ret["SuccessList"] = [i for i in mail_list if i not in fail_mail]
                ret["FailedList"] = fail_mail
                self._MailMatrix.group_mail_step(fail_mail)   # 告诉邮件矩阵当前有一部分发送失败，下次将给别的收件人
            ret["CurrProgress"] = self._MailMatrix.curr_progress()
        # 发送太多被拒
        elif ERROR_SEND_TOO_MANY == err:
            err, err_info = self._AccountsMange.send_too_many_proc(err_info)
            ret["ErrCode"], ret["ErrLog"] = err, err_info

        # 未知错误全组失败，将自动再次尝试
        if ERROR_SEND_FAILED_UNKNOWN == err:
            self._unknown_error_continue_times += 1
            # 未知错误连续发生次数过多
            if self._unknown_error_continue_times >= MailProc.MAILS_UNKNOWN_ERROR_MAX_CONTINUE_TIME:
                ret["ErrCode"] = ERROR_SEND_FAILED_UNKNOWN_TOO_MANY
                ret["ErrLog"] = u"未知错误连续发生次数过多，请排查原因"
        else:
            self._unknown_error_continue_times = 0

        # 其他错误交给GUI处理
        return ret

    def send_once(self):
        """ 主要发送函数 该函数需被反复调用来发送
        user_signal: 继续、暂停、终止
        返回：错误码, log信息(显示), 已发送列表, 发送失败列表, (下一个邮件矩阵位置 x, y)
        """
        return self._send_policy1()


def is_break_error(err):
    if ERROR_FINISH == err and \
       ERROR_OPEN_APPEND_FAILED == err and \
       ERROR_READ_APPEND_FAILED == err and \
       ERROR_CONNECT_FAILED == err and \
       ERROR_LOGIN_FAILED == err and \
       ERROR_SEND_FAILED_UNKNOWN_TOO_MANY == err:
        return True
    return False


def str_find_mailbox(mail_box):
    r = re.findall(r'\S+@\S+', mail_box)
    if r:
        return r[0]
    return ""


def str_is_domain_equal(mailbox1, mailbox2):
    pos1 = mailbox1.find("@")
    pos2 = mailbox2.find("@")
    if -1 == pos1 or -1 == pos2:
        return False
    domain1 = mailbox1[pos1+1:]
    domain2 = mailbox2[pos2+1:]
    if domain1 == domain2 and domain1 != "":
        return True
    return False


def html_add_head(elems):
    head = '''
<html>
<head>
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=gb18030">
</head>
<body>
'''
    return head + elems + "</body></html>\n\n\n\n"


def html_txt_elem(txt):
    ret = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return "<pre>" + ret + "</pre>"


def chdir_myself():
    p = os.path.dirname(os.path.realpath(__file__))
    print("Change dir to MyPath = " + p)
    os.chdir(p)
    return p


def test_send_mail():
    account1 = Account("M201571736@hust.edu.cn", "hjsg1qaz2wsx", "mail.hust.edu.cn", u"李嘉成")
    account2 = Account("U201313778@hust.edu.cn", "dian201313778", "mail.hust.edu.cn", u"李嘉成")
    account3 = Account("M201571856@hust.edu.cn", "M201571856", "mail.hust.edu.cn", u"李嘉成")
    account4 = Account("liangjinchao.happy@163.com", "ioqitwq!QAZ@WSX", "smtp.163.com", u"李嘉成")
    account5 = Account("dian@hust.edu.cn", "diangroup1", "mail.hust.edu.cn", u"李嘉成")
    account6 = Account("hustoliver@hainan.net", "qwertyui", "smtp.hainan.net", u"李世明")
    account7 = Account("mmyzoliver@hainan.net", "qwertyui", "smtp.hainan.net", u"李世明")
    account8 = Account("sys@d3p.com", "123456", "192.168.11.25", u"李世明")
    mails = [ [""] ]
    #i = 20
    #n = 0
    #while n < 1900:
    #    mails.append(MAIL_LIST_ALL[n: n+i])
    #    n += i
    #    i += 1
    #mails = [MAIL_LIST_ALL[1320:1800]]
    #mails =[["mmyzoliver@163.com"]]
    mails = [#["hustoliver@hainan.net"],
             ["mmyzoliver@163.com", "1026815245@qq.com"],
             MAIL_LIST_ALL[1320:1800],
             ["M201571736@hust.edu.cn"],
             ["1307408482@qq.com"],
             ]

    # mail_matrix = SimpleMatrix(2, mails)   # 一次循环最大发送数量
    mail_matrix = XlsMatrix(40, ur'E:\点 石测试Haha\2014点石 你好.xls')
    try:
        l = mail_matrix.read_sheets_before_init()
    except Exception, e:
        print("Read xls sheet failed:{}".format(e))
        return
    print(u"Get xls sheets:\n[{}]".format(u", ".join(l)))
    mail_matrix.init([3, 4], "E")
    # mail_matrix.init(range(len(l)), "C")

    accounts_list = [ account8 ]
    account_manger = AccountsMange(accounts_list)
    #mail_sub = ur"——邮件发送出问题，打扰了{}——".format(get_time_str())
    mail_sub = u"再次分享内容：笛卡尔的思维"
    mail_body = u"""{}
在笔者看来, 斯特劳森的这种描述实际上并不
能完全表达笛卡尔的身心关系问题的真正内容, 这
主要表现在两个方面: 一、斯特劳森的这种描述其实
混同了心物关系和身心关系这两个并不完全对应的
问题, 二、由此, 在这种思路下来理解笛卡尔的心身
关系问题就有过于简单之嫌。
的确, 诚如斯特劳森和大家所理解的, 笛卡尔的
哲学坚持一种形而上的区分, 即对精神性思维( 心)
和广延性物体( 物) 的二元区分。而且, 这种区分实
际上是笛卡尔整个哲学的基点, 正是通过这种根本
性的区分, 笛卡尔才能为他的科学探索事业寻找到
一种可靠的方法论根基, 从而来构建他的整个科学
知识之树。让我们简单地来回顾一下笛卡尔的这种
思路历程。
早在1627 年笛卡尔所写的􀀁指导心灵探求真理
的原则􀀁 􀀁 一书中, 笛卡尔就明确谈到了思维和物体
相区分的思想。在原则12 中, 笛卡尔区分了纯粹智
性的( intellectuelles ) 东西和纯粹物质性
( mat􀀁rielles) 的东西。纯粹智性的东西, 是那些我
们无须借助任何物体形象, 而只需理智( l 'entede􀀁
ment) 在􀀁 自然光芒􀀁 的照耀下就能认识的东西, 我
们也不能对它们构造任何物体性的观念, 这些东西
包括认识、怀疑、无知、意志的活动等。
    """.format(get_time_str())
    # mail_body = u"My good friend, \nnice to meet you"
    mail_body = html_add_head(html_txt_elem(mail_body))
    
    append_list = [ ur'E:\X 发行资料\简报 点事 （2016年8月）.pdf',
                    ur'E:\X 发行资料\文本-内容.txt',
                  ]
    mail = MailProc(mail_matrix, account_manger, mail_sub, mail_body, append_list)
    fail_list = []

    while True:
        ret = mail.send_once()
        err = ret["ErrCode"]
        print(ret)
        if ERROR_SUCCESS == err:
            pass
        elif ERROR_FINISH == err:
            print("OOOOOOOOOOOOOOOOO已经发完了最后一封邮件OOOOOOOOOOOOOOOOOOO")
            print(u"发送失败的邮件有：{}".format(fail_list))
            break
        elif ERROR_OPEN_APPEND_FAILED == err:
            print(u"打开附件失败")
            break
        elif ERROR_READ_APPEND_FAILED == err:
            print(u"读取附件失败")
            break
        elif ERROR_SEND_TOO_MANY == err:
            print(u"一时发送过多")
            time.sleep(900)
        elif ERROR_SEND_TOO_MANY_NEED_WAIT == err:
            print(u"真的发太多了，等等吧")
            time.sleep(900)
        elif ERROR_CONNECT_FAILED == err:
            print(u"没网了，5秒后再尝试")
            time.sleep(5)
        elif ERROR_LOGIN_FAILED == err:
            print(u"用户名密码错误")
            break
        elif ERROR_SEND_FAILED_UNKNOWN == err:
            print(u"未知错误，将再次尝试")
        elif ERROR_SEND_FAILED_UNKNOWN_TOO_MANY == err:
            print(u"太多未知错误了")
            time.sleep(900)
        elif ERROR_SOME_EMAILS_FAILED == err:
            print(u"部分发送失败")
            fail_list += ret["FailedList"]
        time.sleep(60)


if __name__ == "__main__":
    p = chdir_myself()
    logging_init("SendMail.log")
    test_send_mail()
    logging_fini()


