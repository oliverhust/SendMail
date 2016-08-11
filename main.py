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
import sqlite3
import socket
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from mylog import *
from err_code import *
from mail_list import *

# import pdb;  pdb.set_trace()
PROGRAM_UNIQUE_PORT = 48625


class Account:
    def __init__(self, mail_user, mail_passwd, mail_host, sender_name):
        # mail_host 不知道就填空，用auto_get_host获取
        self.user = mail_user
        self.passwd = mail_passwd
        self.host = mail_host
        self.sender_name = sender_name

    def __repr__(self):
        return u"Account({}, {}, {}, {})".format(self.user, self.passwd, self.host, self.sender_name)

    def check(self):
        pass

    def auto_get_host(self):
        host_dict = {"hust.edu.cn": "mail.hust.edu.cn", "163.com": "smtp.163.com"}
        pos = self.user.find("@")
        if -1 == pos:
            return
        domain = self.user[pos+1:]
        if domain in host_dict:
            self.host = host_dict[domain]


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
        # 每当轮询到第一个账户失败时就一直等，除非是第一次发送第一个账号失败 需要用self._send_too_many_mark
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
    BODY_TXT_ENCODE = 'gb18030'
    SPECIAL_STR_PATTERN = r'\{##[A-Z]##\}'     # 邮件正文或标题中的特殊字符

    def __init__(self, mail_sub, mail_body_path, mail_append_list):
        self._Sub = mail_sub    # 原始主题
        self._Body = ""  # 原始正文
        self._AppendList = mail_append_list
        self._BodyPath = mail_body_path

        # 暂存附件内容不用每次读取
        self._msg_append_list = []

        # 判断内容里面是否有特殊含义的字符需要替换（这样每封邮件都不一样，需要一封封发送）
        self._bool_special = self._is_special_content(self._Sub, self._Body)

    def init(self):
        err, err_info = ERROR_SUCCESS, u""
        try:
            f = open(self._BodyPath)
        except Exception, e:
            err = ERROR_OPEN_BODY_FAILED
            err_info = u"打开邮件正文失败\n{}".format(e)
            return err, err_info
        try:
            body = f.read()
        except Exception, e:
            err = ERROR_READ_BODY_FAILED
            err_info = u"读取邮件正文失败\n{}".format(e)
            return err, err_info
        try:
            raw_body = body.decode(MailContent.BODY_TXT_ENCODE)
        except Exception, e:
            err = ERROR_DECODE_BODY_FAILED
            err_info = u"邮件正文解码失败\n{}".format(e)
            return err, err_info

        self._Body = html_add_head(html_txt_elem(raw_body))
        return err, err_info

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
    def __init__(self, max_send_a_loop, xls_path, mail_db):
        self._MaxSendALoop = max_send_a_loop
        self._Path = xls_path
        self._MailColNo = 0
        self._SelectedSheets = []
        self._MailDB = mail_db

        self._xls = None
        self._mails_not_sent = []   # 待发送的
        self._mails_has_sent = []
        self._mails_sent_failed = []

    def read_sheets_before_init(self):     # 可能会出异常 打开失败，调用者注意
        err, err_info = ERROR_SUCCESS, u""
        try:
            self._xls = xlrd.open_workbook(self._Path)
        except Exception, e:
            err = ERROR_OPEN_XLS_FAILED
            err_info = u"打开Excel表格失败\n{}".format(e)
            return err, err_info, []
        return err, err_info, self._xls.sheet_names()

    # 注意selected_sheets从1开始，与用户看到的一致，与表格模块不一致 列名： 'A' 'B' ..
    # 暂不检查是否有重复的邮箱
    def init(self, user_selected_sheets, mail_which_col):
        self._init_set_data(user_selected_sheets, mail_which_col)
        err, err_info = self._create_not_sent_list()
        return err, err_info

    def delete_failed_sent(self):
        self._mails_sent_failed = []
        self._MailDB.del_all_failed_sent()

    def _init_set_data(self, user_selected_sheets, mail_which_col):
        self._MailColNo = ord(mail_which_col.upper()) - ord('A')
        self._SelectedSheets = user_selected_sheets[:]
        for i in range(len(self._SelectedSheets)):
            self._SelectedSheets[i] -= 1

    def _get_xls_mails(self):
        # 从xls中获取收件人数据 [有序]
        mails_read = []
        sheet_list = self._xls.sheets()
        err, err_info = ERROR_SUCCESS, u""
        for i in self._SelectedSheets:
            if i < 0 or i >= len(sheet_list):
                err = ERROR_XLS_SELECT_EXCEED
                err_info = u"该Excel最多只有{}张表，而你选择了{}".format(len(sheet_list), i + 1)
                break
            sheet = sheet_list[i]                # 取第几张sheet
            if self._MailColNo >= sheet.ncols:                   #如果这张表没有该列则跳过
                continue
            for each_ceil in sheet.col_values(self._MailColNo):    # sheet.col_values(列号) 获取sheet内一列
                if "" != str_find_mailbox(each_ceil):
                    mails_read.append(each_ceil)
        logging("Get {} mails from excel.".format(len(mails_read)))
        return err, err_info, mails_read

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
        err, err_info, mails_read = self._get_xls_mails()
        if err != ERROR_SUCCESS:
            return err, err_info

        try:
            last_sent = self._MailDB.get_success_sent()
        except Exception, e:
            err = ERROR_READ_MATRIX_DB_FAILED
            err_info = u"读取数据库中的已发送数据失败 {}".format(e)
            return err, err_info

        # 保存上次发送成功的到总进度中(上次失败的不管)，清除数据库中发送失败的
        self._mails_has_sent = last_sent[:]
        self._MailDB.del_all_failed_sent()

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
            failed_mails = []
        else:
            curr_mails = list(set(curr_mails) - set(failed_mails))
            self._mails_has_sent += curr_mails
            self._mails_sent_failed += failed_mails

        # step 为下次获取准备
        if len(self._mails_not_sent) <= self._MaxSendALoop:
            self._mails_not_sent = []
        else:
            for i in range(self._MaxSendALoop):
                self._mails_not_sent.pop(0)

        # 保存到成功/失败/进度到数据库
        self._MailDB.add_success_sent(curr_mails)
        self._MailDB.add_failed_sent(failed_mails)
        success_sent, failed_sent, not_sent = self.curr_progress()
        self._MailDB.save_sent_progress(success_sent, failed_sent, not_sent)

    @staticmethod
    def get_data_by_name(mail_name):   # 暂不实现
        return mail_name

    def curr_progress(self):
        success_num = len(self._mails_has_sent)
        failed_num = len(self._mails_sent_failed)
        not_send = len(self._mails_not_sent)
        return success_num, failed_num, not_send


class MailProc:
    """ 发送邮件的主流程 """
    MAX_SPECIAL_SEND_A_LOOP = 5                  # 特殊邮件一回合连续发送次数
    MAILS_TRY_AGAIN_WAIT_TIME = 5                # 出现临时错误重试的时间间隔 秒
    MAILS_UNKNOWN_ERROR_MAX_CONTINUE_TIME = 20   # 连续出现未知错误的最大次数
    ENCODE = "gb18030"

    def __init__(self, mail_matrix, accounts_manager, mail_content):
        """ mail_matrix  邮件矩阵对象 MailMatrix,
            accounts_list Account对象列表，多个账户轮换,
            mail_sub 邮件主题,
            mail_body 邮件正文(html)
            mail_append_list 附件列表(路径名) """
        self._MailMatrix = mail_matrix
        self._AccountsMange = accounts_manager
        self._Content = mail_content

        # 每回合发送邮件的数量
        if self._Content.is_special_content():
            self._MailMatrix.set_max_send_a_loop(MailProc.MAX_SPECIAL_SEND_A_LOOP)

        # 未知错误连续发生的次数
        self._unknown_error_continue_times = 0

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


class MailDB:
    """ 数据实时保存和持久化 """
    def __init__(self, path_db):
        self._path = path_db
        self._db = sqlite3.connect(self._path)
        self._c = self._db.cursor()

    def __del__(self):
        self._db.commit()
        self._db.close()

    def init(self):
        # 创建各个表(如果不存在)
        self._create_forever_table()
        self._create_tmp_table()
        self._create_dynamic_table()
        self._db.commit()

    def _create_forever_table(self):

        # 账户信息：用户名 密码 host 姓名
        self._c.execute("CREATE TABLE IF NOT EXISTS account ("
                        "username TEXT PRIMARY KEY NOT NULL, "
                        "passwd TEXT NOT NULL, "
                        "host TEXT, "
                        "sender_name TEXT)")

    def _create_tmp_table(self):

        # 邮件内容 标题 正文 附件路径(换行符分开不同的附件) id永远为0
        self._c.execute("CREATE TABLE IF NOT EXISTS mail_content ("
                        "id INTEGER PRIMARY KEY NOT NULL, "
                        "sub TEXT, "
                        "body TEXT, "
                        "appends TEXT)")

        # 收件人来源 (xls路径，选择的表(逗号隔开), 列) id永远为0
        self._c.execute("CREATE TABLE IF NOT EXISTS receiver ("
                        "id INTEGER PRIMARY KEY NOT NULL, "
                        "src_path TEXT, "
                        "selected TEXT, "
                        "col_name TEXT)")

        # 速度控制信息 (每账户每小时发送数量，每次发送数量)  id永远为0
        self._c.execute("CREATE TABLE IF NOT EXISTS speed_info ("
                        "id INTEGER PRIMARY KEY NOT NULL, "
                        "speed INTEGER, "
                        "each_time INTEGER)")

    def _create_dynamic_table(self):

        # 发送进度 id永远为0
        self._c.execute("CREATE TABLE IF NOT EXISTS sent_progress ("
                        "id INTEGER PRIMARY KEY NOT NULL, "
                        "success INTEGER NOT NULL, "
                        "failed INTEGER NOT NULL, "
                        "notsent INTEGER NOT NULL)")

        # 已发送成功的表
        self._c.execute("CREATE TABLE IF NOT EXISTS success_sent (mail TEXT NOT NULL)")

        # 发送失败的表
        self._c.execute("CREATE TABLE IF NOT EXISTS failed_sent (mail TEXT NOT NULL)")

    def clear_tmp_and_dynamic(self):
        # 清除临时数据和实时数据
        self.del_mail_content()
        self.del_receiver_data()
        self.del_speed_info()
        self.del_sent_progress()
        self.del_all_success_sent()
        self.del_all_failed_sent()

    # ---------------------------------------------------------------------------
    def save_accounts(self, account_list):
        # account_list:由Account对象组成的列表 每次保存都先删除原有信息 (用户名 密码 host 姓名)
        self._c.execute("DELETE FROM account")
        sql_arg = [(x.user, x.passwd, x.host, x.sender_name) for x in account_list]
        self._c.executemany("INSERT INTO account VALUES (?,?,?,?)", sql_arg)
        self._db.commit()

    def get_accounts(self):
        # 返回由Account对象组成的列表
        self._c.execute("SELECT * FROM account")
        ret = self._c.fetchall()
        return [Account(ret[i][0], ret[i][1], ret[i][2], ret[i][3]) for i in range(len(ret))]

    def del_all_accounts(self):
        # 删除所有账户
        self._c.execute("DELETE FROM account")
        self._db.commit()

    # ---------------------------------------------------------------------------
    def save_mail_content(self, sub, body, append_path_list):
        # 邮件内容： 标题 正文 附件路径列表 id永远为0 先删再加
        self._c.execute("DELETE FROM mail_content")
        append_str = "\n\n".join(append_path_list)   # 用两个换行符分开不同的附件路径
        sql_arg = (0, sub, body, append_str)
        self._c.execute("INSERT INTO mail_content VALUES (?,?,?,?)", sql_arg)
        self._db.commit()

    def get_mail_content(self):
        # 返回邮件内容：[ 标题, 正文, 附件路径列表 ] id永远为0
        self._c.execute("SELECT * FROM mail_content")
        ret = self._c.fetchall()
        if not ret:
            return []
        ret = ret[0]
        append_path_list = ret[3].split('\n\n')
        return [ret[1], ret[2], append_path_list]

    def del_mail_content(self):
        self._c.execute("DELETE FROM mail_content")
        self._db.commit()

    # ---------------------------------------------------------------------------
    def save_receiver_data(self, xls_path, selected_list, col_name):
        # 收件人来源 [xls表路径，选择的表(数字组成的列表), 列名] id永远为0
        self._c.execute("DELETE FROM receiver")
        str_list = [str(x) for x in selected_list]
        str_selected = ",".join(str_list)
        sql_arg = (0, xls_path, str_selected, col_name)
        self._c.execute("INSERT INTO receiver VALUES (?,?,?,?)", sql_arg)
        self._db.commit()

    def get_receiver_data(self):
        # 返回收件人来源的信息 [xls表路径，选择的表(数字组成的列表), 列名] id永远为0
        self._c.execute("SELECT * FROM receiver")
        ret = self._c.fetchall()
        if not ret:
            return []
        ret = ret[0]
        str_list = ret[2].split(",")
        selected_list = [int(x) for x in str_list]
        return [ret[1], selected_list, ret[3]]

    def del_receiver_data(self):
        self._c.execute("DELETE FROM receiver")
        self._db.commit()

    # ---------------------------------------------------------------------------
    def save_speed_info(self, num_each_account_hour, each_time_send):
        # 速度控制信息 (每账户每小时发送数量，每次发送数量)  id永远为0
        self._c.execute("DELETE FROM speed_info")
        sql_arg = (0, num_each_account_hour, each_time_send)
        self._c.execute("INSERT INTO speed_info VALUES (?,?,?)", sql_arg)
        self._db.commit()

    def get_speed_info(self):
        # 速度控制信息列表 [每账户每小时发送数量，每次发送数量]  id永远为0
        self._c.execute("SELECT * FROM speed_info")
        ret = self._c.fetchall()
        if not ret:
            return []
        ret = ret[0]
        return [ret[1], ret[2]]

    def del_speed_info(self):
        self._c.execute("DELETE FROM speed_info")
        self._db.commit()

    # ---------------------------------------------------------------------------
    def save_sent_progress(self, success_sent, failed_sent, not_sent):
        # 发送进度 (已发送成功的数量, 已发送失败的数量, 未发送的数量) id永远为0
        self._c.execute("DELETE FROM sent_progress")
        sql_arg = (0, success_sent, failed_sent, not_sent)
        self._c.execute("INSERT INTO sent_progress VALUES (?,?,?,?)", sql_arg)
        self._db.commit()

    def get_sent_progress(self):
        # 发送进度 (已发送成功的数量, 已发送失败的数量, 未发送的数量) id永远为0
        self._c.execute("SELECT * FROM sent_progress")
        ret = self._c.fetchall()
        if not ret:
            return []
        ret = ret[0]
        return [ret[1], ret[2], ret[3]]

    def del_sent_progress(self):
        self._c.execute("DELETE FROM sent_progress")
        self._db.commit()

    # ---------------------------------------------------------------------------
    def add_success_sent(self, list_success):
        if not list_success:
            return
        sql_arg = [(x,) for x in list_success ]
        self._c.executemany("INSERT INTO success_sent VALUES (?)", sql_arg)
        self._db.commit()

    def del_success_sent(self, list_to_del):
        if not list_to_del:
            return
        sql_arg = [(x,) for x in list_to_del ]
        self._c.executemany("DELETE FROM success_sent WHERE mail=?", sql_arg)
        self._db.commit()

    def del_all_success_sent(self):
        self._c.execute("DELETE FROM success_sent")
        self._db.commit()

    def get_success_sent(self):
        self._c.execute("SELECT * FROM success_sent")
        ret = self._c.fetchall()
        return [ret[i][0] for i in range(len(ret))]

    # ---------------------------------------------------------------------------
    def add_failed_sent(self, list_failed):
        if not list_failed:
            return
        sql_arg = [(x,) for x in list_failed ]
        self._c.executemany("INSERT INTO failed_sent VALUES (?)", sql_arg)
        self._db.commit()

    def del_failed_sent(self, list_to_del):
        if not list_to_del:
            return
        sql_arg = [(x,) for x in list_to_del ]
        self._c.executemany("DELETE FROM failed_sent WHERE mail=?", sql_arg)
        self._db.commit()

    def del_all_failed_sent(self):
        self._c.execute("DELETE FROM failed_sent")
        self._db.commit()

    def get_failed_sent(self):
        self._c.execute("SELECT * FROM failed_sent")
        ret = self._c.fetchall()
        return [ret[i][0] for i in range(len(ret))]

    # ---------------------------------------------------------------------------

# #############################################################################################################
# ############################################### UI 界面的接口 #################################################
# #############################################################################################################


class UIInterface:  # ????????????????????????????????????????????
    """ 用户的各种操作对应的处理   提供给上层UI进行使用(提示: 直接继承本类)"""
    def __init__(self):
        self._db = None
        self._path_me = u""
        self._same_program_check = CheckSameProgram()

        self._mail_matrix = None

    def event_form_load(self):
        print("The Event form load has ocurred.")
        self._path_me = chdir_myself()

        # 判断有无相同程序运行
        if self._same_program_check.has_same():
            self.proc_err_same_program()
            return

        # 打开MailDB判断上次情况
        self._db = MailDB(self._path_me + "\\" + 'send_mail.db')
        self._db.init()
        last_progress = self._db.get_sent_progress()   # 如果返回[]代表没有上次
        if last_progress:
            if last_progress[1] != 0 or last_progress[2] != 0:  # 失败或者未发送不为0
                is_recover = self.proc_ask_if_recover(last_progress[0], last_progress[1], last_progress[2])
                if is_recover:
                    # 回读所有的界面上的tmp数据然后UI显示
                    self._reload_db_tmp_data()
                else:
                    # 如果不恢复则清除db中的tmp和dynamic数据
                    self._db.clear_tmp_and_dynamic()
        # 回读所有的账户信息数据然后UI显示
        self._reload_db_account_data()

    def event_start_send(self):
        # 用户设置完所有数据后的处理
        data = self.proc_get_all_ui_data()
        # 按下按钮后当即把界面上的所有数据保存到db
        self._save_ui_data_to_db(data)
        # 创建发送邮件需要的对象



    # -----------------------------------------------------------------------------

    def _reload_db_tmp_data(self):
        data = {}
        tmp = self._db.get_mail_content()
        if tmp:
            data["Sub"], data["Body"], data["AppendList"] = tmp
        else:
            data["Sub"], data["Body"], data["AppendList"] = u"", u"", u""

        tmp = self._db.get_receiver_data()
        if tmp:
            data["XlsPath"], data["SelectedList"], data["ColName"] = tmp
        else:
            data["XlsPath"], data["SelectedList"], data["ColName"] = u"", [], u""

        tmp = self._db.get_speed_info()
        if tmp:
            data["EachHour"], data["EachTime"] = tmp
        else:
            data["EachHour"], data["EachTime"] = 0, 0

        # UI把它们都显示到界面上，并更新界面的静态数据
        self.proc_reload_tmp_data_to_ui(data)

    def _reload_db_account_data(self):
        account_list = self._db.get_accounts()
        # UI把账户信息显示到界面上，并更新界面的静态数据
        self.proc_reload_account_list_to_ui(account_list)

    def _save_ui_data_to_db(self, data):
        self._db.save_mail_content(data["Sub"], data["Body"], data["AppendList"])
        self._db.save_receiver_data(data["XlsPath"], data["SelectedList"], data["ColName"])
        self._db.save_speed_info(data["EachHour"], data["EachTime"])
        self._db.save_accounts(data["AccountList"])

    def _create_mail_objects(self, data):
        self._mail_matrix = XlsMatrix(data["EachTime"], data["XlsPath"], self._db)
        err, err_info, sheets = self._mail_matrix.read_sheets_before_init()
        if err != ERROR_SUCCESS:
            return err, err_info
        err, err_info = self._mail_matrix.init(data["SelectedList"], data["ColName"])
        if err != ERROR_SUCCESS:
            return err, err_info


    # ----------------------------- GUI 要重写的接口 -------------------------------------

    def proc_err_same_program(self):
        pass

    def proc_ask_if_recover(self, last_success_num, last_failed_num, last_not_sent):
        return False

    def proc_reload_tmp_data_to_ui(self, data):
        pass

    def proc_reload_account_list_to_ui(self, account_list):
        pass

    def proc_get_all_ui_data(self):
        return {}


class UITimer:
    """ 抽象类 UI界面需要继承并重写这个类的   (一次性与周期性混合的定时器)"""
    # ----------------------------- GUI 要重写的类 -------------------------------------
    def __init__(self, first_set_time=None, interval_time=None, callback_function=None):
        pass

    def set_tmp_time(self, tmp_time):
        pass

    def start(self, first_set_time=None):
        pass

    def stop(self):
        pass


# #####################################################################################################


class CheckSameProgram:
    """ 检查是否运行了另外一个相同的程序 """
    def __init__(self):
        self._s = None

    def has_same(self):
        ret = False
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   #定义socket类型，网络通信，TCP
        self._s = s
        try:
            s.bind(("127.0.0.1", PROGRAM_UNIQUE_PORT))   #套接字绑定的IP与端口
        except Exception, e:
            ret = True
        return ret

    def fini(self):
        self._s.close()


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


def os_get_curr_dir():
    return os.path.dirname(os.path.realpath(__file__))

def chdir_myself():
    p = os.path.dirname(os.path.realpath(__file__))
    print(u"Change dir to MyPath = " + p)
    os.chdir(p)
    return p


# ############################################################################################
# #######################################   测试   ############################################
# ############################################################################################
# ############################################################################################


def test_sql_db():
    db_path = ur'E:\点 石测试Haha\sendmail_test.db'
    db = MailDB(db_path)
    db.init()

    # ------------------------------------------
    print("\nSave account_list:")
    account1 = Account("M201571736@hust.edu.cn", "hjsg1qaz2wsx", "mail.hust.edu.cn", u"李嘉成")
    account2 = Account("U201313778@hust.edu.cn", "dian201313778", "mail.hust.edu.cn", u"")
    account3 = Account("M201571856@hust.edu.cn", "M201571856", "", u"李嘉成")
    account4 = Account("liangjinchao.happy@163.com", "ioqitwq!QAZ@WSX", "smtp.163.com", u"李嘉成")
    account5 = Account("dian@hust.edu.cn", "diangroup1", "mail.hust.edu.cn", u"李市民")
    account_list = [account1, account2, account3, account4, account5]
    db.save_accounts(account_list)
    ret = db.get_accounts()
    for acc in ret:
        print(u"{} {} {} {}".format(acc.user, acc.passwd, acc.host, acc.sender_name))
    print("Delete all accounts.")
    db.del_all_accounts()
    ret = db.get_accounts()
    for acc in ret:
        print(u"[{}] [{}] [{}] [{}] [{}]".format(acc.user, acc.passwd, acc.host, acc.sender_name))

    # ------------------------------------------
    print("\nSave mail_content")
    sub = u"再次分享内容：笛卡尔的思维"
    body = u"""
    早在1627 年笛卡尔所写的􀀁指导心灵探求真理
的原则􀀁 􀀁 一书中, 笛卡尔就明确谈到了思维和物体
相区分的思想。在原则12 中, 笛卡尔区分了纯粹智
性的( intellectuelles ) 东西和纯粹物质性
( mat􀀁rielles) 的东西。纯粹智性的东西, 是那些我
们无须借助任何物体形象, 而只需理智( l 'entede􀀁
ment) 在􀀁 自然光芒􀀁 的照耀下就能认识的东西, 我

    """
    append_path_list = [ ur'E:\X 发行资料\简报 点事 （2016年8月）.pdf',
                        ur'E:\X 发行资料\文本-内容.txt',
                       ]
    db.save_mail_content(sub, body, append_path_list)
    sub_, body_, append_path_list_ = db.get_mail_content()
    print(u"Sub = [{}]".format(sub_))
    print(u"Appends = {}".format(append_path_list_))
    # print(u"Body = [{}]".format(body_))             # body 有乱码不能打印
    print("Clear mail content")
    db.del_mail_content()
    if not db.get_mail_content():
        print "Delete success"

    # ------------------------------------------
    print("\nReceiver data Test")
    xls_path = ur'E:\点 石测试Haha\2014点石 你好.xls'
    selected_list = [4,5,6,7,8,9]
    col_name = "D"
    db.save_receiver_data(xls_path, selected_list, col_name)
    xls_path_, selected_list_, col_name_ = db.get_receiver_data()
    print(u"xls_path=[{}]\nselected={}\ncol_name={}".format(xls_path_, selected_list_, col_name_))
    print("Delete receiver data")
    if not db.get_receiver_data():
        print("Delete success")

    # ------------------------------------------
    print("\nSpeed info Test")
    db.save_speed_info(400, 40)
    speed, each_time = db.get_speed_info()
    print("Speed = {}, each time send {}".format(speed, each_time))
    print("Delete speed info")
    db.del_speed_info()
    if not db.get_speed_info():
        print("Delete success")

    # -------------------------------------------
    print("\nSent progress test")
    db.save_sent_progress(4000, 2000, 1000)
    a, b, c = db.get_sent_progress()
    print(u"Success: {}, Failed: {}, NotSend: {}".format(a, b, c))
    print("Delete progress")
    if not db.get_sent_progress():
        print("Delete success")

    # ---------------------------------------------
    print("\nSuccess Sent Test")
    db.add_success_sent(["Hello", "@", "", " ", "liangjinchao.happy@jfda.com"])
    print(db.get_success_sent())
    print("Delete some")
    db.del_success_sent(["Hello", " "])
    print(db.get_success_sent())
    print("Delete all")
    db.del_all_success_sent()
    print(db.get_success_sent())

    # ---------------------------------------------
    print("\nFailed Sent Test")
    db.add_failed_sent(["Hello", "@", "", " ", "liangjinchao.happy@jfda.com"])
    print(db.get_failed_sent())
    print("Delete some")
    db.del_failed_sent(["Hello", " "])
    print(db.get_failed_sent())
    print("Delete all")
    db.del_all_failed_sent()
    print(db.get_failed_sent())


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

    mail_db = MailDB(ur'D:\tmp\sendmail.db')
    mail_db.init()
    # mail_matrix = SimpleMatrix(2, mails)             # 一次循环最大发送数量
    mail_matrix = XlsMatrix(20, ur'E:\点 石测试Haha\2014点石 你好.xls', mail_db)
    err, err_info, l = mail_matrix.read_sheets_before_init()
    if err != ERROR_SUCCESS:
        print(err_info)
        return
    print(u"Get xls sheets:\n[{}]".format(u", ".join(l)))
    mail_matrix.init([3, 4], "E")
    # mail_matrix.init(range(len(l)), "C")

    accounts_list = [ account8 ]
    account_manger = AccountsMange(accounts_list)

    #mail_sub = ur"——邮件发送出问题，打扰了{}——".format(get_time_str())
    mail_sub = u"再次分享内容：笛卡尔的思维"

    append_list = [ ur'E:\X 发行资料\简报 点事 （2016年8月）.pdf',
                    ur'E:\X 发行资料\文本-内容.txt',
                  ]
    path_body = ur'E:\X 发行资料\文本-内容.txt'
    mail_content = MailContent(mail_sub, path_body, append_list)
    err, err_info = mail_content.init()
    if ERROR_SUCCESS != err:
        print(err_info)
        return

    mail = MailProc(mail_matrix, account_manger, mail_content)
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
        time.sleep(20)


def test_has_same_program():
    p = CheckSameProgram()
    if p.has_same():
        print("Has same program runing!")
    else:
        print("Only myself runing.")
        time.sleep(10)


if __name__ == "__main__":
    p = chdir_myself()
    logging_init("SendMail.log")
    test_send_mail()
    logging_fini()


