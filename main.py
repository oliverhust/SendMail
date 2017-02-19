#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import random
import copy
import xlrd
import xlwt
import smtplib
import imaplib
import email
import sqlite3
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from mylog import *
from cfg_data import *
from etc_func import *
from ndr import *

# import pdb;  pdb.set_trace()


SOFTWARE_VERSION_CURR = '0.0.0'


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

    def account_list(self):
        return self._AccountList[:]

    def send_too_many_proc(self, origin_err_info):
        # 每当轮询到第一个账户失败时就一直等，除非是第一次发送第一个账号失败 需要用self._send_too_many_mark
        err_info = origin_err_info
        if 1 == len(self._AccountList):
            self._send_too_many_mark = True
            err = ERROR_SEND_TOO_MANY_NEED_WAIT
            err_info += u"\n当前账号发送过多，等待一段时间后自动重试"
        elif 0 == self._CurrAccountId and self._send_too_many_mark:
            # 不换账号，继续尝试第一个，直到第一个成功
            account_next = self._AccountList[self._CurrAccountId]  # 在每次get的时候已经切换了
            err = ERROR_SEND_TOO_MANY
            err_info += u"\n当前邮箱发送过多，切换到账号{}".format(account_next.user)
        else:
            account_next = self._AccountList[self._CurrAccountId]  # 在每次get的时候已经切换了
            err = ERROR_SEND_TOO_MANY
            err_info += u"\n当前账号发送过多，切换到账号{}".format(account_next.user)
            # 只要进一次这里就永远被标记
            self._send_too_many_mark = True
        return err, err_info


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


class ExcelRead:
    """ Excel表格的读取等 """
    def __init__(self, xls_path):
        self._Path = xls_path
        self._xls = None

    def _open_excel_if_need(self):
        err, err_info = ERROR_SUCCESS, u""
        if self._xls is None:
            try:
                self._xls = xlrd.open_workbook(self._Path)
            except Exception, e:
                err = ERROR_OPEN_XLS_FAILED
                err_info = u"打开Excel表格失败\n{}".format(e)
                self._xls = None
        return err, err_info

    def get_sheet_names(self):
        err, err_info = self._open_excel_if_need()
        if err != ERROR_SUCCESS:
            return err, err_info, None
        return err, err_info, self._xls.sheet_names()

    def get_mails(self, selected_sheets, mail_which_col):
        err, err_info = self._open_excel_if_need()
        # 从xls中获取收件人数据 [有序]
        mails_read = []
        sheet_list = self._xls.sheets()
        for i in selected_sheets:
            if i < 0 or i >= len(sheet_list):
                err = ERROR_XLS_SELECT_EXCEED
                err_info = u"该Excel最多只有{}张表，而你选择了{}".format(len(sheet_list), i + 1)
                break
            sheet = sheet_list[i]                # 取第几张sheet
            if mail_which_col >= sheet.ncols:                   # 如果这张表没有该列则跳过
                continue
            for each_ceil in sheet.col_values(mail_which_col):    # sheet.col_values(列号) 获取sheet内一列
                if "" != str_find_mailbox(each_ceil):
                    mails_read.append(each_ceil)
        print_t(u"Get {} mails from excel.".format(len(mails_read)))
        return err, err_info, mails_read


class XlsMatrix:
    """ 由xls表格实现的邮件矩阵          从xls表格导入收件人信息存为矩阵(三维)
    1. 为MailProc发送时提供发件人列表   (策略:各域名邮箱均匀分布)
    2. 统计已成功/失败/未发送的邮件数量
    3. 保存(已成功和已失败的邮件)到MailDB，重启时从DB过滤已成功；提供clear_db供任务完成时调用
    """
    def __init__(self, max_send_a_loop, xls_path, mail_db):
        self._MaxSendALoop = max_send_a_loop
        self._MailColNo = 0
        self._SelectedSheets = []
        self._MailDB = mail_db

        self._excel = ExcelRead(xls_path)
        self._mails_not_sent = []   # 待发送的
        self._mails_has_sent = []
        self._mails_sent_failed = []

    def get_sheet_names(self):     # 可能会打开失败，调用者注意
        return self._excel.get_sheet_names()

    # 注意selected_sheets从1开始，与用户看到的一致，与表格模块不一致 列名： 'A' 'B' ..
    # 暂不检查是否有重复的邮箱
    def init(self, user_selected_sheets, mail_which_col):
        self._init_set_data(user_selected_sheets, mail_which_col)
        err, err_info = self._create_not_sent_list()
        return err, err_info

    def delete_failed_sent(self):
        self._mails_sent_failed = []

    def _init_set_data(self, user_selected_sheets, mail_which_col):
        self._MailColNo = ord(mail_which_col.upper()) - ord('A')
        self._SelectedSheets = user_selected_sheets[:]
        for i in range(len(self._SelectedSheets)):
            self._SelectedSheets[i] -= 1

    @staticmethod
    def _random_sort_mails(mails_input):
        mails_origin = mails_input[:]
        mails_new = []
        # logging(u"Origin mail list is:\n{}".format(mails_origin))
        while mails_origin:   # 不断从mails_origin移动到mails_new直到mails_origin为空
            index_r = random.randint(0, len(mails_origin)-1)
            # 从mails_origin头开始选择与mails_origin[index_r]相同域名的邮箱
            for i, each_mail in enumerate(mails_origin):
                if str_is_domain_equal(each_mail, mails_origin[index_r]):
                    mails_new.append(each_mail)
                    mails_origin.pop(i)
                    break
        # logging(u"New mail list is:\n{}".format(mails_new))
        return mails_new

    def _create_not_sent_list(self):
        # 根据db的已发送和当前读取的生成待发送列表
        err, err_info, mails_read = self._excel.get_mails(self._SelectedSheets, self._MailColNo)
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

        # 保存到成功/进度到数据库
        self._MailDB.add_success_sent(curr_mails)

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

        # 未知错误连续发生的次数
        self._unknown_error_continue_times = 0

    @staticmethod
    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(),
                           addr.encode('utf-8') if isinstance(addr, unicode) else addr))

    @staticmethod
    def check_account_login(user_name, passwd, host):
        s = smtplib.SMTP_SSL()
        try:
            s.connect(host)
        except Exception, e:
            err = ERROR_CONNECT_FAILED
            err_info = u"连接服务器失败\n{}".format(e)
            return err, err_info
        try:
            s.login(user_name, passwd)
        except Exception, e:
            err = ERROR_LOGIN_FAILED
            err_info = u"认证失败:可能是账号或密码错误\n{}".format(e)
            return err, err_info
        return ERROR_SUCCESS, u""

    @staticmethod
    def send_one_group(mail_list, account, mail_content, use_ssl=True):
        fail_mail = []  # 部分发送失败的邮件

        err, err_info, msg = mail_content.to_msg()
        if err != ERROR_SUCCESS:
            return err, err_info, fail_mail

        msg['From'] = MailProc._format_addr(u"{}<{}>".format(account.sender_name, account.user))
        msg['BCC'] = ";".join(mail_list)

        print_t(u"Start to send a group")
        if use_ssl:
            s = smtplib.SMTP_SSL()
        else:
            s = smtplib.SMTP()

        print(u"Connecting to host {}".format(account.host))
        try:
            s.connect(account.host)
        except Exception, e:
            err = ERROR_CONNECT_FAILED
            err_info = u"连接{}失败，请检查网络是否通畅\n错误信息: {}".format(account.host, e)
            return err, err_info, fail_mail

        print(u"Logining account {}".format(account.user))
        try:
            s.login(account.user, account.passwd)
        except Exception, e:
            err = ERROR_LOGIN_FAILED
            err_info = u"{}登录失败，账号或密码错误；也可能是该账号被封\n{}".format(account.user, e)
            return err, err_info, fail_mail

        print(u"Start to send email...")
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
        print_t(u"The email has sent.")
        # print_t("Send to " + repr(mail_list) + " | " + err_info + " | " + repr(fail_mail))

        return err, err_info, fail_mail

    def _send_try(self, mail_list):
        ret = self.send_one_group(mail_list,
                                  self._AccountsMange.get_an_account(),
                                  self._Content)
        return ret

    def _send_policy1(self):
        """ 返回：错误码, log信息(显示), 已发送列表, 发送失败列表, (下一个邮件矩阵位置 x, y) """
        # ret默认为异常退出，一封也没发出去，下次将会再次尝试
        ret = {"ErrCode": ERROR_SUCCESS, "ErrLog": "", "SuccessList": [], "FailedList": [],
               "CurrProgress": self._MailMatrix.curr_progress()}  # (成功, 失败, 未发送) 的数量

        # 先测试邮件内容是否正常
        err, err_info, tmp_msg = self._Content.to_msg()
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
            # 如果未发送为0则表示刚才发完了最后一组
            if 0 == ret["CurrProgress"][2]:
                err = ERROR_FINISH
                ret["ErrCode"] = ERROR_FINISH
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
        ret = self._send_policy1()
        print_t(ret)
        return ret


# 装饰器
def maildb_multithread_safe(func):
    def proc_func(self, *args, **kwargs):
        if self._db is None:
            print("The mail db has been close, do not use it")
            return None
        self._lock.acquire()
        self._c = self._db.cursor()
        try:
            ret = func(self, *args, **kwargs)
        finally:
            self._c.close()
            self._lock.release()
        return ret
    return proc_func


class MailDB(threading.Thread):
    """ 数据实时保存和持久化，请勿为同一数据库创建多个对象 定时线程定时commit数据到磁盘
        如果需要频繁增删的数据不要写完就立即commit而是让定时线程自行commit """
    DEFAULT_DB_NAME = 'send_mail.db'
    _UNIQUE_DB = None

    def __init__(self, path_db=None):
        threading.Thread.__init__(self)
        self._path = path_db
        self._db = None
        self._c = None    # 游标
        self._lock = threading.RLock()   # 数据操作线程锁

        self._thread_need_close = False
        self._flush_thread_lock = threading.RLock()  # 定时线程的锁

    def close(self):    # 如果不close则定时线程一直运行
        self._force_unique_fini()
        if self._db is not None:
            self._flush_thread_close()
            self._db.commit()
            self._db.close()
            self._db = None

    def init(self):
        # 创建各个表(如果不存在)
        err, err_info = ERROR_SUCCESS, u""
        self._force_unique_init()
        self._set_default_path_if_void()

        try:
            self._db = sqlite3.connect(self._path, check_same_thread=False)
        except Exception, e:
            err = ERROR_READ_MATRIX_DB_FAILED
            err_info = u"打开数据库失败！\n{}".format(e)
            return err, err_info

        self._force_unique_set()
        print_t(u"Open database success, Ver = {}".format(sqlite3.version))

        self._c = self._db.cursor()
        self._create_forever_table()
        self._create_tmp_table()
        self._create_dynamic_table()

        try:
            self._db.commit()
        except Exception, e:
            err = ERROR_WRITE_MAIL_DB_FAILED
            err_info = u"写入数据库失败！没有写权限\n{}".format(e)

        self.start()  # 启动定时线程
        return err, err_info

    def _save(self):
        self._db.commit()

    def _set_default_path_if_void(self):
        if self._path:
            return
        self._path = self.mail_db_default_path()

    @staticmethod
    def mail_db_default_path():
        path_me = os_get_curr_dir()
        return os.path.join(path_me, MailDB.DEFAULT_DB_NAME)

    @staticmethod
    def _force_unique_init():
        # 只允许一个对象存在，在连接数据库前调用
        if MailDB._UNIQUE_DB:
            MailDB._UNIQUE_DB.close()

    def _force_unique_set(self):
        # 调用时刚创建了self._db
        MailDB._UNIQUE_DB = self

    @staticmethod
    def _force_unique_fini():
        # 在close开始的时候调用
        MailDB._UNIQUE_DB = None

    # 定时flush线程，外部不要调用
    def run(self):
        print("Thread maildb flush timer started.")
        while True:
            self._lock.acquire()
            if self._db is not None:
                # print("flushing mail db")
                self._db.commit()
            self._lock.release()

            # 把延时1秒拆分成多次是为了提高关闭的响应速度
            need_close = False
            spilt_times = 4
            for i in range(spilt_times):
                if self._flush_thread_get_need_close():
                    need_close = True
                    break
                time.sleep(1.0 / spilt_times)
            if need_close:
                break

    def _flush_thread_close(self, need_close=True):
        self._flush_thread_lock.acquire()
        self._thread_need_close = need_close
        self._flush_thread_lock.release()
        self.join()
        print("Thread maildb flush stopped.")

    def _flush_thread_get_need_close(self):
        self._flush_thread_lock.acquire()
        need_close = self._thread_need_close
        self._flush_thread_lock.release()
        return need_close

    def clear_forever(self):
        self.del_all_accounts()
        self.del_all_ndr_cfg()

    def clear_tmp_and_dynamic(self):
        # 清除临时数据和实时数据
        self.del_mail_content()
        self.del_receiver_data()
        self.del_speed_info()
        self.del_sent_progress()
        self.del_all_success_sent()
        self.del_start_time()
        self.del_all_used_accounts()
        self.del_all_ndr_mail()

    def _create_forever_table(self):

        # 账户信息：用户名 密码 host 姓名
        self._c.execute("CREATE TABLE IF NOT EXISTS account ("
                        "username TEXT PRIMARY KEY NOT NULL, "
                        "passwd TEXT NOT NULL, "
                        "host TEXT NOT NULL, "
                        "sender_name TEXT)")

        # 退信配置
        self._c.execute("CREATE TABLE IF NOT EXISTS ndr_cfg ("
                        "domain TEXT PRIMARY KEY NOT NULL, "
                        "enable TEXT NOT NULL, "
                        "imap_host TEXT NOT NULL, "
                        "use_ssl TEXT NOT NULL, "
                        "sys_email TEXT NOT NULL, "
                        "mail_pos TEXT NOT NULL, "
                        "mail_pos_key TEXT, "
                        "mail_patt TEXT NOT NULL, "
                        "info_pos TEXT NOT NULL, "
                        "info_pos_key TEXT, "
                        "info_patt TEXT NOT NULL) ")

    def _create_tmp_table(self):

        # 邮件内容 标题 正文 附件路径(换行符分开不同的附件) id永远为0
        self._c.execute("CREATE TABLE IF NOT EXISTS mail_content ("
                        "key TEXT NOT NULL, "
                        "value TEXT, "
                        "name TEXT, "
                        "bin BLOB)")

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

        # 退信处理的表：开始时间
        self._c.execute("CREATE TABLE IF NOT EXISTS start_time ("
                        "id INTEGER PRIMARY KEY NOT NULL, "
                        "start_time TEXT NOT NULL)")

        # 退信处理的表：曾使用过的账户
        self._c.execute("CREATE TABLE IF NOT EXISTS used_account ("
                        "username TEXT PRIMARY KEY NOT NULL, "
                        "passwd TEXT NOT NULL, "
                        "host TEXT NOT NULL, "
                        "sender_name TEXT)")

        # 曾经退信过的邮件地址和最后一封邮件的时间
        self._c.execute("CREATE TABLE IF NOT EXISTS ndr_mail ("
                        "mail TEXT PRIMARY KEY NOT NULL, "
                        "last_recv_time TEXT)")

    # ---------------------------------------------------------------------------
    @maildb_multithread_safe
    def save_accounts(self, account_list):
        # account_list:由Account对象组成的列表 每次保存都先删除原有信息 (用户名 密码 host 姓名)
        self._c.execute("DELETE FROM account")
        sql_arg = [(x.user, x.passwd, x.host, x.sender_name) for x in account_list]
        self._c.executemany("INSERT INTO account VALUES (?,?,?,?)", sql_arg)
        self._save()

    @maildb_multithread_safe
    def get_accounts(self):
        # 返回由Account对象组成的列表
        self._c.execute("SELECT * FROM account")
        ret = self._c.fetchall()
        return [Account(ret[i][0], ret[i][1], ret[i][2], ret[i][3]) for i in range(len(ret))]

    @maildb_multithread_safe
    def del_all_accounts(self):
        # 删除所有账户
        self._c.execute("DELETE FROM account")
        self._save()

    # ---------------------------------------------------------------------------
    @maildb_multithread_safe
    def save_mail_content(self, mail_content, save_bin_data=True):
        # MailContent类型 如果body的resource中含bin_data则把bin_data也存进去
        self._c.execute("DELETE FROM mail_content")

        if not mail_content:
            return

        sql_arg = [(u"sub", unicode(mail_content.sub()), u"", buffer("")),
                   (u"body", unicode(mail_content.body()), u"", buffer(""))]

        for rc_append in mail_content.append_resource_list():
            sql_arg.append((u"append", unicode(rc_append.path), unicode(rc_append.name), buffer("")))

        # 读取正文资源的二进制，如果没有则读取
        for i, rc_body in enumerate(mail_content.body_resource_list()):
            bin_data = ""
            if save_bin_data:
                if rc_body.bin_data:
                    bin_data = rc_body.bin_data
                else:
                    err, err_info, bin_data = mail_content.body_resource_bin_data(i)
                    if err != ERROR_SUCCESS:
                        continue
            sql_arg.append((u"body_resource", unicode(rc_body.path), unicode(rc_body.name), buffer(bin_data)))

        self._c.executemany("INSERT INTO mail_content VALUES (?,?,?,?)", sql_arg)
        self._save()

    @maildb_multithread_safe
    def get_mail_content(self):
        # 返回邮件内容：MailContent类型
        self._c.execute("SELECT * FROM mail_content")
        ret = self._c.fetchall()
        if not ret:
            return None

        sub = u""
        body = u""
        append_rc_list = []
        body_rc_list = []

        for key, value, name, blod in ret:
            if key == u"sub":
                sub = value
            elif key == u"body":
                body = value
            elif key == u"append":
                append_rc_list.append(MailResource(value, name))
            elif key == u"body_resource":
                body_rc_list.append(MailResource(value, name, str(blod)))

        return MailContent(sub, body, append_rc_list, body_rc_list)

    @maildb_multithread_safe
    def del_mail_content(self):
        self._c.execute("DELETE FROM mail_content")
        self._save()

    # ---------------------------------------------------------------------------
    @maildb_multithread_safe
    def save_receiver_data(self, xls_path, selected_list, col_name):
        # 收件人来源 [xls表路径，选择的表(数字组成的列表), 列名] id永远为0
        self._c.execute("DELETE FROM receiver")
        str_list = [str(x) for x in selected_list]
        str_selected = ",".join(str_list)
        sql_arg = (0, xls_path, str_selected, col_name)
        self._c.execute("INSERT INTO receiver VALUES (?,?,?,?)", sql_arg)
        self._save()

    @maildb_multithread_safe
    def get_receiver_data(self):
        # 返回收件人来源的信息 [xls表路径，选择的表(数字组成的列表), 列名] id永远为0
        self._c.execute("SELECT * FROM receiver")
        ret = self._c.fetchall()
        if not ret:
            return []
        ret = ret[0]
        str_list = ret[2].split(",")
        selected_list = [int(x) for x in str_list if len(x) > 0]
        return [ret[1], selected_list, ret[3]]

    @maildb_multithread_safe
    def del_receiver_data(self):
        self._c.execute("DELETE FROM receiver")
        self._save()

    # ---------------------------------------------------------------------------
    @maildb_multithread_safe
    def save_speed_info(self, num_each_account_hour, each_time_send):
        # 速度控制信息 (每账户每小时发送数量，每次发送数量)  id永远为0
        self._c.execute("DELETE FROM speed_info")
        sql_arg = (0, num_each_account_hour, each_time_send)
        self._c.execute("INSERT INTO speed_info VALUES (?,?,?)", sql_arg)

    @maildb_multithread_safe
    def get_speed_info(self):
        # 速度控制信息列表 [每账户每小时发送数量，每次发送数量]  id永远为0
        self._c.execute("SELECT * FROM speed_info")
        ret = self._c.fetchall()
        if not ret:
            return []
        ret = ret[0]
        return [ret[1], ret[2]]

    @maildb_multithread_safe
    def del_speed_info(self):
        self._c.execute("DELETE FROM speed_info")

    # ---------------------------------------------------------------------------
    @maildb_multithread_safe
    def save_sent_progress(self, success_sent, failed_sent, not_sent):
        # 发送进度 (已发送成功的数量, 已发送失败的数量, 未发送的数量) id永远为0
        self._c.execute("DELETE FROM sent_progress")
        sql_arg = (0, success_sent, failed_sent, not_sent)
        self._c.execute("INSERT INTO sent_progress VALUES (?,?,?,?)", sql_arg)

    @maildb_multithread_safe
    def get_sent_progress(self):
        # 发送进度 (已发送成功的数量, 已发送失败的数量, 未发送的数量) id永远为0
        self._c.execute("SELECT * FROM sent_progress")
        ret = self._c.fetchall()
        if not ret:
            return []
        ret = ret[0]
        return [ret[1], ret[2], ret[3]]

    @maildb_multithread_safe
    def del_sent_progress(self):
        self._c.execute("DELETE FROM sent_progress")

    # ---------------------------------------------------------------------------
    @maildb_multithread_safe
    def add_success_sent(self, list_success):
        if not list_success:
            return
        sql_arg = [(x,) for x in list_success]
        self._c.executemany("INSERT INTO success_sent VALUES (?)", sql_arg)
        self._save()

    @maildb_multithread_safe
    def del_success_sent(self, list_to_del):
        if not list_to_del:
            return
        sql_arg = [(x,) for x in list_to_del]
        self._c.executemany("DELETE FROM success_sent WHERE mail=?", sql_arg)

    @maildb_multithread_safe
    def del_all_success_sent(self):
        self._c.execute("DELETE FROM success_sent")

    @maildb_multithread_safe
    def get_success_sent(self):
        self._c.execute("SELECT * FROM success_sent")
        ret = self._c.fetchall()
        return [ret[i][0] for i in range(len(ret))]

    @maildb_multithread_safe
    def is_exist_success_sent(self, mail):
        sql_arg = (mail, )
        self._c.execute("SELECT * FROM success_sent WHERE mail=?", sql_arg)
        ret = self._c.fetchall()
        if ret:
            return True
        return False

    # ---------------------------------------------------------------------------
    @maildb_multithread_safe
    def save_start_time(self, datetime_start):
        # 开始发送时间记录 id永远为0 datetime_start为datetime类型
        time_str = datetime_start.strftime(u"%Y/%m/%d %H:%M:%S")
        self._c.execute("DELETE FROM start_time")
        sql_arg = (0, time_str)
        self._c.execute("INSERT INTO start_time VALUES (?,?)", sql_arg)

    @maildb_multithread_safe
    def get_start_time(self):
        # 开始发送时间记录 id永远为0 datetime_start为datetime类型
        self._c.execute("SELECT * FROM start_time")
        ret = self._c.fetchall()
        if not ret:
            return []
        time_str = ret[0][1]
        datetime_start = datetime.datetime.strptime(time_str, u"%Y/%m/%d %H:%M:%S")
        return datetime_start

    @maildb_multithread_safe
    def del_start_time(self):
        self._c.execute("DELETE FROM start_time")

    # ---------------------------------------------------------------------------
    @maildb_multithread_safe
    def save_used_accounts(self, used_account_list):
        # "曾用账户"  used_account_list:由Account对象组成的列表 每次保存都先删除原有信息 (用户名 密码 姓名)
        self._c.execute("DELETE FROM used_account")
        sql_arg = [(x.user, x.passwd, x.host, x.sender_name) for x in used_account_list]
        self._c.executemany("INSERT INTO used_account VALUES (?,?,?,?)", sql_arg)

    @maildb_multithread_safe
    def get_used_accounts(self):
        # "曾用账户" 返回由Account对象组成的列表
        self._c.execute("SELECT * FROM used_account")
        ret = self._c.fetchall()
        return [Account(ret[i][0], ret[i][1], ret[i][2], ret[i][3]) for i in range(len(ret))]

    @maildb_multithread_safe
    def del_all_used_accounts(self):
        # 删除所有曾用账户
        self._c.execute("DELETE FROM used_account")

    # ---------------------------------------------------------------------------
    @maildb_multithread_safe
    def add_ndr_mail(self, mail, last_recv_time):
        time_str = last_recv_time.strftime("%Y/%m/%d %H:%M:%S")
        sql_arg = (mail, time_str)
        self._c.execute("REPLACE INTO ndr_mail VALUES (?,?)", sql_arg)

    @maildb_multithread_safe
    def get_ndr_mail(self, mail):
        # 返回[mail, datetime_last_recv], 没有则返回[]
        self._c.execute("SELECT * FROM ndr_mail WHERE mail=?", (mail, ))
        ret = self._c.fetchall()
        if not ret:
            return []
        time_str = ret[0][1]
        dt = datetime.datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S")
        return [ret[0][0], dt]

    @maildb_multithread_safe
    def del_ndr_mail(self, mail):
        self._c.execute("DELETE FROM ndr_mail WHERE mail=?", (mail, ))

    @maildb_multithread_safe
    def del_all_ndr_mail(self):
        self._c.execute("DELETE FROM ndr_mail")

    # ---------------------------------------------------------------------------

    @maildb_multithread_safe
    def add_ndr_cfg(self, cfg_ndr_list):
        if not cfg_ndr_list:
            return
        sql_arg = [x.to_tuple() for x in cfg_ndr_list if x.check()]
        self._c.executemany("INSERT INTO ndr_cfg VALUES (?,?,?,?,?,?,?,?,?,?,?)", sql_arg)

    @maildb_multithread_safe
    def get_ndr_cfg(self, domain):
        self._c.execute("SELECT * FROM ndr_cfg WHERE domain=?", (domain, ))
        ret = self._c.fetchall()
        if not ret:
            return []
        return CfgNdr(ret[0])

    @maildb_multithread_safe
    def del_ndr_cfg(self, domain):
        self._c.execute("DELETE FROM ndr_cfg WHERE domain=?", (domain, ))

    @maildb_multithread_safe
    def del_all_ndr_cfg(self):
        self._c.execute("DELETE FROM ndr_cfg")

    # ---------------------------------------------------------------------------


class AuptEnv:

    def __init__(self):
        self._db = None

    def init(self):
        path_db = MailDB.mail_db_default_path()
        self._db = sqlite3.connect(path_db)
        self._create_tables()

    def close(self):
        self._db.commit()
        self._db.close()

    def _create_tables(self):

        c = self._db.cursor()

        # 永久保存的全局信息
        c.execute("CREATE TABLE IF NOT EXISTS aupt_globals("
                  "key TEXT PRIMARY KEY NOT NULL, "
                  "value TEXT)")

        # 永久保存的全局信息
        c.execute("CREATE TABLE IF NOT EXISTS aupt_bins("
                  "key TEXT PRIMARY KEY NOT NULL, "
                  "value BLOB)")

        c.close()
        self._db.commit()

    def set_software_version(self, version):   # str
        c = self._db.cursor()
        sql_arg = (unicode(version), )
        c.execute("REPLACE INTO aupt_globals VALUES ('software_version',?)", sql_arg)
        c.close()
        self._db.commit()

    def get_software_version(self):   # str
        c = self._db.cursor()
        c.execute("SELECT * FROM aupt_globals WHERE key='software_version'")
        ret = c.fetchall()
        c.close()
        if not ret:
            return SOFTWARE_VERSION_CURR
        return ret[0][1]

    def set_last_check_update(self, dt):    # datetime()精确到天
        c = self._db.cursor()
        datetime_str = dt.strftime("%Y/%m/%d")
        sql_arg = (datetime_str, )
        c.execute("REPLACE INTO aupt_globals VALUES ('last_check_update',?)", sql_arg)
        c.close()
        self._db.commit()

    def get_last_check_update(self):     # 返回datetime()精确到天
        c = self._db.cursor()
        c.execute("SELECT * FROM aupt_globals WHERE key='last_check_update'")
        ret = c.fetchall()
        c.close()
        if not ret:
            return None
        dt = datetime.datetime.strptime(ret[0][1], "%Y/%m/%d")
        return dt

    def set_dist_pkg(self, pkg_str):   # str类型
        c = self._db.cursor()
        sql_arg = (buffer(pkg_str), )
        c.execute("REPLACE INTO aupt_bins VALUES ('dist_pkg',?)", sql_arg)
        c.close()
        self._db.commit()

    def get_dist_pkg(self):   # str类型
        c = self._db.cursor()
        c.execute("SELECT * FROM aupt_bins WHERE key='dist_pkg'")
        ret = c.fetchall()
        c.close()
        if not ret:
            return ""
        return str(ret[0][1])


# #############################################################################################################
# ############################################### UI 界面的接口 #################################################
# #############################################################################################################


class UIInterface:
    """ 用户的各种操作对应的处理   提供给上层UI进行使用(提示: 直接继承本类)"""
    def __init__(self):
        self._db = None
        self._send_finish_time = None

        self._mail_matrix = None
        self._account_manger = None
        self._mail_content = None
        self._mail_proc = None
        self._ndr = None
        self._timer = None

    def event_init_ui_timer(self, ui_timer):
        self._timer = ui_timer

    def event_form_load(self):
        print(u"The Event form load occur.")

        # 打开MailDB判断上次情况
        self._db = MailDB()
        err, err_info = self._db.init()
        if ERROR_SUCCESS != err:
            self.proc_err_before_load(err, err_info)
            return

        # 询问用户是否恢复上次的数据
        is_recover = False
        last_progress = self._db.get_sent_progress()   # 判断用户上次有没有清除内容
        last_content = self._db.get_mail_content()
        if last_progress:
            is_recover = self.proc_ask_if_recover(last_progress[0], last_progress[1], last_progress[2])
        elif last_content:                             # 单纯的恢复发送内容
            is_recover = self.proc_ask_if_reload_ui(last_content.sub())
        if is_recover:
            self._reload_db_tmp_data()             # 回读所有的界面上的tmp数据然后UI显示
        else:
            self._db.clear_tmp_and_dynamic()       # 如果不恢复则清除db中的tmp和dynamic数据

        # 回读所有的账户信息数据然后UI显示
        self._reload_db_account_data()

    def event_main_exit_and_save(self):
        # 退出时用户点了"保存"
        data = self.proc_get_all_ui_data()
        self._save_ui_data_to_db(data)
        self._db.close()

    def event_main_exit_and_discard(self):
        if self._db:
            self._db.clear_tmp_and_dynamic()
            self._db.close()

    def event_main_exit_direct(self):
        if self._db:
            self._db.close()

    def event_start_send(self):
        # 用户设置完所有数据后的处理
        data = self.proc_get_all_ui_data()
        # 按下按钮后当即把界面上的所有数据保存到db
        self._save_ui_data_to_db(data)
        # 创建发送邮件需要的对象
        err, err_info = self._create_mail_objects(data)
        if err != ERROR_SUCCESS:
            self._delete_mail_objects()
            self.proc_err_before_send(err, err_info)
            return
        # 发送前的信息确认
        last_success_num, last_failed_num, will_send_num = self._mail_matrix.curr_progress()
        err, err_info, all_sheets_list = self._mail_matrix.get_sheet_names()
        if not self.proc_confirm_before_send(last_success_num, last_failed_num, will_send_num,
                                             all_sheets_list, data["SelectedList"]):
            self._delete_mail_objects()
            return
        # 启动UI定时器
        account_num = len(self._account_manger.account_list())
        period_time = int(3600000.0/data["EachHour"]*data["EachTime"]/account_num)
        print(u"[{}]Start Timer.The timer period is {} ms".format(get_time_str(), period_time))
        self._timer.setup(period_time, self.__send_timer_callback, 2000)
        self._timer.start()
        # 弹出进度条窗口并运行
        ret = self.proc_exec_progress_window(self._mail_matrix.curr_progress())
        print(u"Exit the progress windows.")
        # 窗口退出则停止定时器
        self._timer.stop()
        self._delete_mail_objects()
        # 发送完成且不被暂停则启动退信识别
        if ret:
            self._ndr_receive_process()

    def event_user_cancel_progress(self):
        # 窗口退出则停止定时器
        self._timer.stop()
        self._delete_mail_objects()

    def event_user_cancel_ndr(self):
        # 用户停止接收退信
        self._timer.stop()
        self._ndr.stop_proc()
        self._ndr_refresh_table()

    def event_save_ndr_to_excel(self):
        # 保存退信到表格   保存表格之前请先停止接收退信
        excel = ExcelWrite()
        ndr_data_list = self._ndr.get_all_ndr_data()
        return excel.save_ndr_data(ndr_data_list)

    def save_mail_content(self, mail_content):
        self._db.save_mail_content(mail_content)

    def get_mail_content(self):
        return self._db.get_mail_content()

    @staticmethod
    def check_account_login(user_name, passwd, host):
        return MailProc.check_account_login(user_name, passwd, host)

    # -----------------------------------------------------------------------------

    def _reload_db_tmp_data(self):
        data = {"MailContent": self._db.get_mail_content()}

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
        self._db.save_mail_content(data["MailContent"])
        self._db.save_receiver_data(data["XlsPath"], data["SelectedList"], data["ColName"])
        self._db.save_speed_info(data["EachHour"], data["EachTime"])
        self._db.save_accounts(data["AccountList"])

    def _create_mail_objects(self, data):
        self._mail_matrix = XlsMatrix(data["EachTime"], data["XlsPath"], self._db)
        err, err_info, sheets = self._mail_matrix.get_sheet_names()
        if err != ERROR_SUCCESS:
            return err, err_info
        err, err_info = self._mail_matrix.init(data["SelectedList"], data["ColName"])
        if err != ERROR_SUCCESS:
            return err, err_info

        self._account_manger = AccountsMange(data["AccountList"])

        self._mail_content = deepcopy(data["MailContent"])
        self._mail_content.rc_name_mode_mail()

        self._mail_proc = MailProc(self._mail_matrix, self._account_manger, self._mail_content)

        self._ndr = NdrProc(data["AccountList"], self._db)
        self._ndr.event_start_send()

        return err, err_info

    def _delete_mail_objects(self):
        self._mail_matrix = None
        self._account_manger = None
        self._mail_content = None
        self._mail_proc = None

    def __send_timer_callback(self):
        # 定时器的回调函数里面不要出现阻塞性任务，在阻塞过程中可能超时又再次回调，或者被别的定时器抢占
        print(u"[{}]Timer call back.".format(get_time_str()))
        fatal_err_code = (ERROR_OPEN_APPEND_FAILED, ERROR_READ_APPEND_FAILED)
        err_auto_retry = (ERROR_CONNECT_FAILED, ERROR_LOGIN_FAILED)

        ret = self._mail_proc.send_once()

        err, err_info = ret["ErrCode"], ret["ErrLog"]
        progress_info = unicode(time.strftime('[%Y-%m-%d %H:%M:%S]'))
        if ERROR_SUCCESS == err:
            progress_info += u"{}\nSend success to :\n{}".format(err_info, repr(ret["SuccessList"]))
            self.proc_update_progress(ret["CurrProgress"], progress_info)
        elif ERROR_FINISH == err:
            progress_info += u"{}\nSend success to :\n{}".format(err_info, repr(ret["SuccessList"]))
            self.proc_update_progress(ret["CurrProgress"], progress_info+u"\nSend Finished")
            self._timer.stop()  # 关闭定时器
            self._delete_mail_objects()
            # 分两种情况，用户确认后关闭发送
            success_num, failed_num, not_sent_num = ret["CurrProgress"]
            if 0 != failed_num:
                self.proc_finish_with_failed(success_num, failed_num, not_sent_num)
            else:
                self.proc_finish_all_success(success_num, failed_num, not_sent_num)
            self._send_finish_time = datetime.datetime.now()
        elif ERROR_SEND_TOO_MANY_NEED_WAIT == err:
            self.proc_update_progress(ret["CurrProgress"], progress_info+err_info)
            # 等待20分钟再尝试
            self._timer.set_tmp_time(20*60*1000)
        elif err in fatal_err_code:
            self._timer.stop()       # 关闭定时器
            self.proc_update_progress(ret["CurrProgress"], progress_info+err_info)
            self.proc_err_fatal_run(err, err_info)
        elif err in err_auto_retry:
            self.proc_err_auto_retry(err, err_info)
            self.proc_update_progress(ret["CurrProgress"], progress_info+err_info)
        elif ERROR_SEND_FAILED_UNKNOWN_TOO_MANY == err:
            self.proc_update_progress(ret["CurrProgress"], progress_info+err_info)
        elif ERROR_SOME_EMAILS_FAILED == err:
            progress_info += err_info + u"\n"
            progress_info += u"Success:\n{}\nFailed:\n{}".format(repr(ret["SuccessList"]), repr(ret["FailedList"]))
            self.proc_update_progress(ret["CurrProgress"], progress_info)
        elif ERROR_SEND_TOO_MANY == err:
            self.proc_update_progress(ret["CurrProgress"], progress_info+err_info)
        elif ERROR_SEND_FAILED_UNKNOWN == err:
            self.proc_update_progress(ret["CurrProgress"], progress_info+err_info)
        else:
            self.proc_update_progress(ret["CurrProgress"], progress_info+err_info)

    def _ndr_receive_process(self):
        if not self.proc_ask_if_ndr():
            return

        # 需要用户输入接收服务器地址
        # user_list = self._ndr.get_used_user_list()
        # user_host_dict = self.proc_input_recv_host(user_list)
        # self._ndr.update_recv_host(user_host_dict) # 保存配置 ?????????????????????????????????????????????????

        self._ndr.start_thread()
        self._timer.setup(1000, self.__ndr_timer_callback)
        self._timer.start()
        self.proc_exec_ndr_win(self._send_finish_time)
        self._timer.stop()
        self._ndr.stop_proc()

    def _ndr_refresh_table(self):
        err_info, ndr_data_list, ndr_all_count, has_finish_a_loop = self._ndr.get_data()
        self.proc_ndr_refresh_data(err_info, ndr_data_list, ndr_all_count, has_finish_a_loop)

    def __ndr_timer_callback(self):
        # 定时器的回调函数里面不要出现阻塞性任务，在阻塞过程中可能超时又再次回调，或者被别的定时器抢占
        self._ndr_refresh_table()

    # ----------------------------- GUI 要重写的接口 -------------------------------------
    def proc_err_before_load(self, err, err_info):
        pass

    def proc_ask_if_recover(self, last_success_num, last_failed_num, last_not_sent):
        return False

    def proc_ask_if_reload_ui(self, mail_sub):
        return False

    def proc_reload_tmp_data_to_ui(self, data):
        pass

    def proc_reload_account_list_to_ui(self, account_list):
        pass

    def proc_get_all_ui_data(self):
        return {}

    def proc_err_before_send(self, err, err_info):
        pass

    def proc_confirm_before_send(self, last_success_num, last_failed_num, will_send_num, all_sheets_list, select_list):
        return True

    def proc_exec_progress_window(self, init_progress):
        return True

    def proc_update_progress(self, progress_tuple=None, progress_info=None):
        pass

    def proc_finish_with_failed(self, success_num, failed_num, not_sent_num):
        pass

    def proc_finish_all_success(self, success_num, failed_num, not_sent_num):
        pass

    def proc_err_fatal_run(self, err, err_info):
        pass

    def proc_err_auto_retry(self, err, err_info):
        pass

    def proc_ask_if_ndr(self):
        return True

    def proc_input_recv_host(self, user_list):
        # 返回字典{user:host}  host对于不支持的账户填u""，与发送服务器一致则填None 用Account.get_recv_host辅助
        return {}

    def proc_exec_ndr_win(self, send_finish_datetime):
        pass

    def proc_ndr_refresh_data(self, err_info, ndr_data_list, ndr_all_count, has_finish_a_loop):
        pass


class UITimer:
    """ 抽象类 UI界面需要继承并重写这个类的   (一次性与周期性混合的定时器)"""
    # ----------------------------- GUI 要重写的类 -------------------------------------
    def __init__(self, parent=None):
        pass

    def setup(self, period_time, callback_function, first_set_time=None):
        pass

    def start(self, first_set_time=None):
        pass

    def set_tmp_time(self, tmp_time):
        pass

    def stop(self):
        pass


class ExcelWrite:
    """ 写Excel表格  """
    def __init__(self, xls_path=None):
        self._Path = xls_path

        self._wb = None
        self._sheet = None

        # 字体样式
        self._s_head = None
        self._s_data = None

    def save_ndr_data(self, ndr_data_list):
        self._ndr_init()
        self._ndr_write(ndr_data_list)
        err, err_info = self._ndr_save()
        if ERROR_SUCCESS != err:
            return err, err_info
        err, err_info = self._ndr_open_xls()
        if ERROR_SUCCESS == err:
            err_info = self._Path
        return err, err_info

    # ------------------------------------------------------------------
    @staticmethod
    def _style(front_name, height, bold=False):
        style = xlwt.XFStyle()           # 初始化样式
        font = xlwt.Font()               # 为样式创建字体
        font.name = front_name           # 'Times New Roman'
        font.bold = bold
        font.color_index = 4
        font.height = height
        style.font = font
        return style

    def _ndr_set_path(self):
        if self._Path is not None:
            return self._Path
        now = datetime.datetime.now()
        time_str = now.strftime(u"%Y%m%d_%H%M%S")
        file_name = u"退信邮箱_{}.xls".format(time_str)
        dir_name = os_get_user_desktop()
        self._Path = os.path.join(dir_name, file_name)
        return self._Path

    def _ndr_init(self):
        self._s_head = self._style('Malgun Gothic Semilight', 270, True)
        self._s_data = self._style('Malgun Gothic Semilight', 270)

        self._wb = xlwt.Workbook()
        self._sheet = self._wb.add_sheet(u"退信列表")

        self._sheet.col(0).width = 40 * 256
        self._sheet.col(1).width = 60 * 256
        self._sheet.col(2).width = 30 * 256
        self._sheet.col(3).width = 100 * 256

        self._sheet.write(0, 0, u"邮箱", self._s_head)
        self._sheet.write(0, 1, u"退信原因/建议", self._s_head)
        self._sheet.write(0, 2, u"时间", self._s_head)
        self._sheet.write(0, 3, u"详细信息", self._s_head)

    def _ndr_write(self, ndr_data_list):
        # ndr_data_list: [{时间，退回的邮箱， 出错信息， 建议}...]
        # ndr_data_list: [{'Date': datetime, 'Mail': u'', 'Info': u'', 'Suggestion': u''}...]
        for i, each_ndr in enumerate(ndr_data_list):
            r = i + 1
            time_str = each_ndr['Date'].strftime(u"%Y/%m/%d %H:%M:%S")
            self._sheet.write(r, 0, each_ndr['Mail'], self._s_data)
            self._sheet.write(r, 1, each_ndr['Suggestion'], self._s_data)
            self._sheet.write(r, 2, time_str, self._s_data)
            self._sheet.write(r, 3, each_ndr['Info'], self._s_data)

    def _ndr_save(self):
        err, err_info = ERROR_SUCCESS, u""
        path = self._ndr_set_path()
        try:
            self._wb.save(path)
        except Exception, e:
            err = ERROR_WRITE_XLS_FAILED
            err_info = u"写Excel到{}失败:{}".format(path, e)
        return err, err_info

    def _ndr_open_xls_win(self):
        err, err_info = ERROR_SUCCESS, u""
        try:
            os.startfile(self._Path)
        except Exception, e:
            err = ERROR_START_XLS_FAILED
            err_info = u"尝试用本地程序打开表格{}失败:{}".format(self._Path, e)
        return err, err_info

    def _ndr_open_xls_mac(self):
        err, err_info = ERROR_SUCCESS, u""
        try:
            ret_info = os_shell(u"open {}".format(self._Path))
        except Exception, e:
            err = ERROR_START_XLS_FAILED
            err_info = u"尝试用本地程序打开表格{}失败:{}".format(self._Path, e)
        else:
            if ret_info != "":
                err = ERROR_START_XLS_FAILED
                err_info = u"尝试使用本地程序打开表格{}失败:{}".format(self._Path, ret_info)
        return err, err_info

    def _ndr_open_xls(self):
        if is_windows_system():
            return self._ndr_open_xls_win()
        elif is_mac_system():
            return self._ndr_open_xls_mac()
        else:
            return ERROR_START_XLS_FAILED, u"未知的操作系统：{}".format(platform.system())


# ############################################################################################
# #####################################   测试用例   ##########################################
# ############################################################################################
# ############################################################################################

class UnitTest:

    def __init__(self):
        pass

    @staticmethod
    def test_sql_db():
        db_path = ur'D:\tmp\sendmail.db'
        db = MailDB(db_path)
        err, err_info = db.init()
        if ERROR_SUCCESS != err:
            print(err_info)
            return

        # ------------------------------------------
        print("\nSave account_list:")
        account1 = Account("M201571736@hust.edu.cn", "XXXXXXXXXXXXXXXXXX", "mail.hust.edu.cn", u"李嘉成")
        account2 = Account("U201313778@hust.edu.cn", "XXXXXXXXXXXXXXX", "mail.hust.edu.cn", u"")
        account3 = Account("XXXXXXXXXX@hust.edu.cn", "XXXXXXXXXX", "", u"李嘉成")
        account4 = Account("liangjinchao.happy@163.com", "XXXXXXXXXXXXXX", "smtp.163.com", u"李嘉成")
        account5 = Account("dian@hust.edu.cn", "XXXXXXXXX", "mail.hust.edu.cn", u"李市民")
        account_list = [account1, account2, account3, account4, account5]
        db.save_accounts(account_list)
        ret = db.get_accounts()
        for acc in ret:
            print(u"{} {} {} {}".format(acc.user, acc.passwd, acc.host, acc.sender_name))
        print("Delete all accounts.")
        db.del_all_accounts()
        ret = db.get_accounts()
        for acc in ret:
            print(u"[{}] [{}] [{}] [{}]".format(acc.user, acc.passwd, acc.host, acc.sender_name))

        # ------------------------------------------
        print("\nSave mail_content")
        sub = u"再次分享内容：笛卡尔的思维"
        body = ur'''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'SimSun'; font-size:16pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">你好dd的都是的<img src="E:\X 发行资料\exit.png" />啥的<img src="E:\X 发行资料\write_mail.png" />阿大声道</p></body></html>
        '''

        append_rc_list = [MailResource(ur'E:\X 发行资料\简报 点事 （2016年8月）.pdf', u'hha点事'),
                          ur'E:\X 发行资料\文本-内容.txt']

        body_rc_list = [MailResource(ur'E:\X 发行资料\exit.png', ur'E:\X 发行资料\exit.png'),
                        MailResource(ur'E:\X 发行资料\write_mail.png', ur'E:\X 发行资料\write_mail.png')]

        origin_mc = MailContent(sub, body, append_rc_list, body_rc_list)
        origin_mc.fill_body_resource_bin_data()
        db.save_mail_content(origin_mc)
        mc = db.get_mail_content()
        print(u"Sub = [{}]".format(mc.sub()))
        print(u"Appends = {}".format(mc.append_resource_list()))
        print(u"BodyRc = {}".format(mc.body_resource_list()))
        print(u"Body = [{}]".format(mc.body()))
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
        print("\nTest Sent progress")
        db.save_sent_progress(4000, 2000, 1000)
        a, b, c = db.get_sent_progress()
        print(u"Success: {}, Failed: {}, NotSend: {}".format(a, b, c))
        print("Delete progress")
        if not db.get_sent_progress():
            print("Delete success")

        # ---------------------------------------------
        print("\nTest Success Sent")
        db.add_success_sent(["Hello", "@", "", " ", "liangjinchao.happy@jfda.com"])
        print(db.get_success_sent())
        t = "Hello"
        print("Is the {} Exist: {}".format(t, db.is_exist_success_sent(t)))
        t = "Hello2"
        print("Is the {} Exist: {}".format(t, db.is_exist_success_sent(t)))
        print("Delete some")
        db.del_success_sent(["Hello", " "])
        print(db.get_success_sent())
        print("Delete all")
        db.del_all_success_sent()
        print(db.get_success_sent())
        t = "Hello"
        print("Is the {} Exist: {}".format(t, db.is_exist_success_sent(t)))
        t = "Hello2"
        print("Is the {} Exist: {}".format(t, db.is_exist_success_sent(t)))

        # ------------------------------------------
        print("\nTest Used Account")
        account1 = Account("M201571736@hust.edu.cn", "XXXXXXXXX", "mail.hust.edu.cn", u"李嘉成")
        account2 = Account("U201313778@hust.edu.cn", "XXXXXXXXXXXXXXX", "mail.hust.edu.cn", u"")
        account3 = Account("XXXXXXXXXX@hust.edu.cn", "XXXXXXXXXX", "", u"李嘉成")
        account4 = Account("liangjinchao.happy@163.com", "XXXXXXXXXX", "smtp.163.com", u"李嘉成")
        account5 = Account("dian@hust.edu.cn", "XXXXXXXXXXX", "mail.hust.edu.cn", u"李市民")
        account_list = [account1, account2, account3, account4, account5]
        db.save_used_accounts(account_list)
        ret = db.get_used_accounts()
        for acc in ret:
            print(u"{} {} {} {}".format(acc.user, acc.passwd, acc.host, acc.sender_name))
        print("Delete all accounts.")
        db.del_all_used_accounts()
        ret = db.get_used_accounts()
        for acc in ret:
            print(u"[{}] [{}] [{}] [{}]".format(acc.user, acc.passwd, acc.host, acc.sender_name))

        # ------------------------------------------
        print("\nTest Start Time")
        dt = datetime.datetime.now()
        print("Current datetime: {}".format(dt))
        db.save_start_time(dt)
        dt_get = db.get_start_time()
        print("Get start time: {}".format(dt_get))
        db.del_start_time()
        print("Delete start time")
        dt_get = db.get_start_time()
        if dt_get:
            print("Failed!Get start time: {}".format(dt_get))
        else:
            print("Delete start times success")

        # ------------------------------------------
        print("\nTest Ndr mail")
        db.add_ndr_mail("oliver@haha.com", datetime.datetime(2018, 2, 6, 8, 5, 6, 555))
        db.add_ndr_mail("abcde", datetime.datetime(1999, 2, 6, 8, 5, 6, 555))
        db.add_ndr_mail("qwertyui@haha.com", datetime.datetime(2018, 2, 6, 8, 5, 6, 555))
        mail = "abcde"
        print("Get {}:{}".format(mail, db.get_ndr_mail(mail)))
        mail = "qwertyui@haha.com"
        print("Get {}:{}".format(mail, db.get_ndr_mail(mail)))
        mail = "abcdef"
        print("Get {}:{}".format(mail, db.get_ndr_mail(mail)))
        mail = "oliver@haha.com"
        print("Get {}:{}".format(mail, db.get_ndr_mail(mail)))
        mail, dt = "qwertyui@haha.com", datetime.datetime(2222, 5, 7, 6, 2)
        db.add_ndr_mail(mail, dt)
        print("----Modify {} to {}----".format(mail, dt))
        mail = "abcde"
        print("Get {}:{}".format(mail, db.get_ndr_mail(mail)))
        mail = "qwertyui@haha.com"
        print("Get {}:{}".format(mail, db.get_ndr_mail(mail)))
        mail = "abcdef"
        print("Get {}:{}".format(mail, db.get_ndr_mail(mail)))
        mail = "oliver@haha.com"
        print("Get {}:{}".format(mail, db.get_ndr_mail(mail)))
        mail = "qwertyui@haha.com"
        db.del_ndr_mail(mail)
        print("----Delete {}----".format(mail))
        mail = "abcde"
        print("Get {}:{}".format(mail, db.get_ndr_mail(mail)))
        mail = "qwertyui@haha.com"
        print("Get {}:{}".format(mail, db.get_ndr_mail(mail)))
        mail = "abcdef"
        print("Get {}:{}".format(mail, db.get_ndr_mail(mail)))
        mail = "oliver@haha.com"
        print("Get {}:{}".format(mail, db.get_ndr_mail(mail)))

    @staticmethod
    def test_aupt_sql_db():
        print("\n----------- Test software version ------------------")

        db = AuptEnv()
        db.init()

        def print_software_version(_db):
            print("software_version: {}".format(_db.get_software_version()))
            print("last_check: {}".format(_db.get_last_check_update()))
            print("pkg: {}".format(repr(_db.get_dist_pkg())))

        db.set_software_version('1.0.31.5')
        db.set_last_check_update(datetime.datetime(2016, 4, 21))
        db.set_dist_pkg("aada\xFF\xAAdddddddddddc")

        print_software_version(db)

        db.set_software_version('2.30.4.5')
        db.set_dist_pkg("\xFF\xAAddddddddggg\xFF\xDD")

        print_software_version(db)

        db.set_last_check_update(datetime.datetime(2014, 4, 21))


        print_software_version(db)

    @staticmethod
    def test_sql_multithread():
        import thread

        def child_thread(db, no):
            times = 100
            in_list = [4, 3]
            if no < in_list[0]:
                my_type = 'Write'
                for c_i in xrange(times):
                    db.add_ndr_mail("oliver{}@{}.com".format(c_i, no), datetime.datetime.now())
            elif in_list[0] <= no < in_list[0] + in_list[1]:
                my_type = 'Delete'
                for c_i in xrange(times):
                    db.del_ndr_mail("oliver{}@{}.com".format(c_i, no))
            else:
                my_type = 'Get'
                for c_i in xrange(times):
                    db.get_ndr_mail("oliver{}@{}.com".format(c_i, no))
            print_t("{} ({}) Exit".format(no, my_type))

        db_path = ur'E:\X 发行资料\sendmail_test.db'
        mail_db = MailDB(db_path)
        err, err_info = mail_db.init()
        if ERROR_SUCCESS != err:
            print(err_info)
            return
        mail_db.del_all_ndr_mail()

        for i in range(10):
            thread.start_new_thread(child_thread, (mail_db, i))

        time.sleep(60)  # 等待足够长的时间
        mail_db.close()
        print("Exit Main thread")

    @staticmethod
    def test_send_mail():
        html_body = ur'''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'SimSun'; font-size:16pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">你好dd的都是的<img src="E:\X 发行资料\exit.png" />啥的<img src="E:\X 发行资料\write_mail.png" />阿大声道</p></body></html>
        '''

        account1 = Account("M201571736@hust.edu.cn", "XXXXXXXXXXXXXXXXX", "mail.hust.edu.cn", u"李嘉成")
        account2 = Account("U201313778@hust.edu.cn", "XXXXXXXXXXXXXXX", "mail.hust.edu.cn", u"李嘉成")
        account3 = Account("XXXXXXXXXX@hust.edu.cn", "XXXXXXXXXX", "mail.hust.edu.cn", u"李嘉成")
        account6 = Account("hustoliver@hainan.net", "qwertyui", "smtp.hainan.net", u"李世明")
        account7 = Account("mmyzoliver@hainan.net", "qwertyui", "smtp.hainan.net", u"李世明")
        account8 = Account("sys@d3p.com", "123456", "192.168.11.25", u"李世明")
        account9 = Account("mmyzoliver@gmail.com", "gjakl!QAZ@WSX", u"smtp.gmail.com", u"张珊")

        mails = [[""]]
        # i = 20
        # n = 0
        # while n < 1900:
        #    mails.append(MAIL_LIST_ALL[n: n+i])
        #    n += i
        #    i += 1
        # mails = [MAIL_LIST_ALL[1320:1800]]
        # mails =[["mmyzoliver@163.com"]]
        mails = [# ["hustoliver@hainan.net"],
                 ["mmyzoliver@163.com", "1026815245@qq.com"],
                 # MAIL_LIST_ALL[1320:1800],
                 ["M201571736@hust.edu.cn"],
                 ["1307408482@qq.com"],
                 ]

        mail_db = MailDB(ur'D:\tmp\sendmail.db')
        mail_db.init()
        # mail_matrix = SimpleMatrix(2, mails)             # 一次循环最大发送数量
        mail_matrix = XlsMatrix(20, ur'E:\X 发行资料\我的点石邮箱16-7-2修改.xls', mail_db)
        err, err_info, l = mail_matrix.get_sheet_names()
        if err != ERROR_SUCCESS:
            print(err_info)
            return
        print(u"Get xls sheets:\n[{}]".format(u", ".join(l)))
        mail_matrix.init(range(3, 9), "D")
        # mail_matrix.init(range(len(l)), "C")

        accounts_list = [account9]
        account_manger = AccountsMange(accounts_list)

        # mail_sub = ur"——邮件发送出问题，打扰了{}——".format(get_time_str())
        mail_sub = u"再次分享内容：笛卡尔的思维"

        append_list = [MailResource(ur'E:\X 发行资料\简报 点事 （2016年8月）.pdf', u'hha点事'),
                       ur'E:\X 发行资料\文本-内容.txt',
                      ]

        resource_list = [MailResource(ur'E:\X 发行资料\exit.png', ur'E:\X 发行资料\exit.png'),
                         MailResource(ur'E:\X 发行资料\write_mail.png', ur'E:\X 发行资料\write_mail.png')]

        mail_content = MailContent(mail_sub, html_body, append_list, resource_list)
        mail_content.rc_name_mode_mail()
        err, err_info, tmp_msg = mail_content.to_msg()
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

    @staticmethod
    def test_has_same_program():
        p = check_program_has_same(42412)
        if p.has_same():
            print("Has same program running!")
        else:
            print("Only myself running.")
            time.sleep(10)


if __name__ == "__main__":
    UnitTest.test_sql_db()

