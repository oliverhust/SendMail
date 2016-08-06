#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from mylog import *
from mail_list import *

import pdb; pdb.set_trace()

ERROR_SUCCESS = 0
ERROR_FINISH = 1
ERROR_PAUSE = 2 # 预留，未用
ERROR_OPEN_APPEND_FAILED = 3
ERROR_READ_APPEND_FAILED = 4
ERROR_SEND_TOO_MANY = 5
ERROR_SEND_TOO_MANY_NEED_WAIT = 6
ERROR_CONNECT_FAILED = 7
ERROR_LOGIN_FAILED = 8
ERROR_SEND_FAILED_UNKNOWN = 9
ERROR_SEND_FAILED_UNKNOWN_TOO_MANY = 10
ERROR_SOME_EMAILS_FAILED = 11


class Account:
    def __init__(self, mail_user, mail_passwd, mail_host, sender_name):
        self.user = mail_user
        self.passwd = mail_passwd
        self.host = mail_host
        self.sender_name = sender_name

    def auto_get_host(self):
        pass


class MailProc:
    """ 发送邮件的主流程 """
    MAILS_IN_GROUP = 40       # 一次最大发送数量
    MAILS_TRY_AGAIN_WAIT_TIME = 5  # 出现临时错误重试的时间间隔
    MAILS_UNKNOWN_ERROR_MAX_CONTINUE_TIME = 20 # 连续出现未知错误的最大次数
    ENCODE = "utf-8"

    def __init__(self, mail_matrix, accounts_list, mail_sub, mail_body, mail_append_list):
        """
        mail_matrix  邮件矩阵，邮件被一行行发送,
        accounts_list Account对象列表，多个账户轮换,
        mail_sub 邮件主题,
        mail_body 邮件正文(html)
        mail_append_list 附件列表(路径名)"""
        self._MailMatrix = mail_matrix
        self._AccountsList = accounts_list
        self._MailSub = mail_sub
        self._MailBody = mail_body
        self._MailAppendList = mail_append_list

        # 当前发送账号
        self._CurrAccountID = 0
        # 暂存当前要发送的邮件矩阵中的起始位置
        self._CurrLine = 0
        self._CurrRow  = 0
        # 暂存附件内容不用每次读取
        self._MsgAppendList = []
        # 未知错误连续发生的次数
        self._UnKnowErrorContinueTimes = 0

        # 当第一次尝试完第二个账户该标志位就会一直被置True
        self._PolicyTooManyMark = False

    @staticmethod
    def send_one_group(mail_list, account, mail_sub, mail_body, msg_append_list):
        err = ERROR_SUCCESS
        err_info = ""
        fail_mail = []  # 部分发送失败的邮件

        me = account.sender_name + "<"+account.user+">"

        msg = MIMEMultipart()
        msg['Subject'] = mail_sub
        msg['From'] = me
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
            fail_mail = s.sendmail(me, mail_list, msg.as_string())
        except smtplib.SMTPRecipientsRefused, e:
            err = ERROR_SEND_TOO_MANY
            err_info = u"当前账号{}发送邮件过多被拒: {}".format(account.user, e)
        except Exception, e:
            err = ERROR_SEND_FAILED_UNKNOWN
            err_info = u"未知原因，暂时发送失败: {}".format(e)
        else:
            fail_mail = fail_mail.keys()
            if len(fail_mail) != 0:
                err = ERROR_SOME_EMAILS_FAILED
        s.close()
        logging("After send a group:\n" + err_info)

        return err, err_info, fail_mail

    def _group_mail_get(self):
        if self._CurrLine >= len(self._MailMatrix):
            return ERROR_FINISH
        return self._MailMatrix[self._CurrLine][self._CurrRow : self._CurrRow+MailProc.MAILS_IN_GROUP]

    def _group_mail_step(self):
        self._CurrRow += MailProc.MAILS_IN_GROUP
        if self._CurrRow >= len(self._MailMatrix[self._CurrLine]):
            self._CurrRow = 0
            self._CurrLine += 1

    def _read_append(self):
        """ 读取附件，失败则暂停 """
        if self._MsgAppendList:   #如果已经读取了就返回
            return ERROR_SUCCESS, u""
        ret = ERROR_SUCCESS, u"读取附件成功"
        for each_append in self._MailAppendList:
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
            self._MsgAppendList.append(msg_append)
        logging(ret[1])
        return ret

    def _send_try(self, mail_list):
        ret = self.send_one_group(mail_list,
                                  self._AccountsList[self._CurrAccountID],
                                  self._MailSub,
                                  self._MailBody,
                                  self._MsgAppendList)
        return ret

    def _send_policy_too_many_proc(self, old_err_info):
        """ 每当轮询到第一个账户失败时就一直等，除非是第一次发送第一个账号失败 需要用self._PolicyTooManyMark"""
        err_info = old_err_info
        if 1 == len(self._AccountsList):
            err = ERROR_SEND_TOO_MANY_NEED_WAIT
        elif 0 == self._CurrAccountID and self._PolicyTooManyMark:
            # 不换账号，继续尝试第一个，直到第一个成功
            err = ERROR_SEND_TOO_MANY_NEED_WAIT
            err_info = u"所有邮箱都已发送太多邮件被拒，将从第一个开始重新尝试"
        else:
            self._CurrAccountID = (self._CurrAccountID + 1) % len(self._AccountsList)
            account_next = self._AccountsList[self._CurrAccountID]
            err = ERROR_SEND_TOO_MANY
            err_info += u"\n切换到账号{}".format(account_next.user)
            # 只要进一次这里就永远被标记
            self._PolicyTooManyMark = True
        return err, err_info

    def _send_policy1(self):
        """ 返回：错误码, log信息(显示), 已发送列表, 发送失败列表, (下一个邮件矩阵位置 x, y) """
        # ret默认为异常退出，一封也没发出去，下次将会再次尝试
        ret = {"ErrCode": ERROR_SUCCESS, "ErrLog": "", "SuccessList": [], "FailedList": [],
               "SendPos": (self._CurrLine, self._CurrRow)}

        err, err_info = self._read_append()
        if ERROR_SUCCESS != err:
            ret["ErrCode"], ret["ErrLog"] = err, err_info
            return ret

        mail_list = self._group_mail_get()
        if mail_list == ERROR_FINISH:
            ret["ErrCode"], ret["ErrLog"] = ERROR_FINISH, u"所有邮件都已尝试发送"
            return ret

        # 根据发送结果进行本次发送的自我处理
        err, err_info, fail_mail = self._send_try(mail_list)
        ret["ErrCode"], ret["ErrLog"] = err, err_info

        # 全部发送成功
        if ERROR_SUCCESS == err:
            self._group_mail_step()   # 将发送位置在矩阵中向前
            ret["SuccessList"] = mail_list
            ret["SendPos"] = (self._CurrLine, self._CurrRow)
        # 部分发送成功(除此之外其他情况都是全部失败)
        elif ERROR_SOME_EMAILS_FAILED == err:
            time.sleep(MailProc.MAILS_TRY_AGAIN_WAIT_TIME)
            ret_tmp = self._send_try(fail_mail)
            if ret_tmp[0] == ERROR_SUCCESS:
                self._group_mail_step()   # 将发送位置在矩阵中向前
                ret["ErrCode"], ret["ErrLog"] = ERROR_SUCCESS, ""
                ret["SuccessList"] = mail_list
                ret["FailedList"] = []
                ret["SendPos"] = (self._CurrLine, self._CurrRow)
            else:
                ret["SuccessList"] = [ i for i in mail_list if i not in fail_mail ]
                ret["FailedList"] = fail_mail
        # 发送太多被拒
        elif ERROR_SEND_TOO_MANY == err:
            err, err_info = self._send_policy_too_many_proc(err_info)
            ret["ErrCode"], ret["ErrLog"] = err, err_info

        # 未知错误全组失败，将自动再次尝试
        if ERROR_SEND_FAILED_UNKNOWN == err:
            self._UnKnowErrorContinueTimes += 1
            # 未知错误连续发生次数过多
            if self._UnKnowErrorContinueTimes >= MailProc.MAILS_UNKNOWN_ERROR_MAX_CONTINUE_TIME:
                ret["ErrCode"] = ERROR_SEND_FAILED_UNKNOWN_TOO_MANY
                ret["ErrLog"] = u"未知错误连续发生次数过多，请排查原因"
        else:
            self._UnKnowErrorContinueTimes = 0

        # 其他错误交给GUI处理
        return ret

    def send_once(self, user_signal = 0):
        """ 主要发送函数 该函数需被反复调用来发送
        user_singnal: 继续、暂停、终止
        返回：错误码, log信息(显示), 已发送列表, 发送失败列表, (下一个邮件矩阵位置 x, y)
        """
        return self._send_policy1()


###########################################################################
#                          给个元素加上html头
#参数：html元素集
#返回：完整的html文本
###########################################################################
def Html_AddHead(Elems):

    Head = '''
<html>
<head>
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=gb2312">
</head>
<body>
'''
    return Head + Elems + "</body></html>\n\n\n\n"

###########################################################################
#                          将文本转换为Html中的元素
#参数：文本
#返回：文本元素
###########################################################################
def Html_TxtElem(txt):

    ret = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return("<pre>" + ret + "</pre>")


def chdir_myself():
    p = os.path.dirname(os.path.realpath(__file__))
    print("Change dir to MyPath = " + p)
    os.chdir(p)
    return p


def test_send_mail():
    account1 = Account("M201571736@hust.edu.cn", "hjsg1qaz2wsx", "mail.hust.edu.cn", u"李嘉")
    account2 = Account("U201313778@hust.edu.cn", "dian201313778", "mail.hust.edu.cn", u"李嘉")
    mail_matrix = [ [""] ]
    i = 35
    n = 0
    while n < 200:
        mail_matrix.append(MAIL_LIST_ALL[n: n+i])
        n += i
        i += 1
    mail_matrix = [["1026815245@qq.com", "mmyzoliver@163.com"], MAIL_LIST_ALL[1320:1320], [], ["1307408482@qq.com"]]
    accounts_list = [account1, account2]
    mail_sub = ur"——测试邮件不要管——"
    mail_body = """
    Python中是有查找功能的，四种方式：in、not in、count、index，后两种方式是列表的方法，下面以a_list = ['a','b','c','hello']，为例作介绍：
判断值是否在列表中，in操作符：
# 判断值a是否在列表中，并返回True或False
'a' in a_lis
判断值是否不在列表，not in操作符：
# 判断a是否不在列表中，并返回True或False
'a' not in a_list
统计指定值在列表中出现的次数，count方法：
# 返回a在列表中的出现的次数
a_list.count('a')
查看指定值在列表中的位置，index方法：
# 返回a在列表中每一次出现的位置，默认搜索整个列表
a_list.index('a')
# 返回a在指定切片内第一次出现的位置
    """
    mail_body = Html_AddHead(Html_TxtElem(mail_body))
    append_list = [ ur'E:\点石月刊 发行\2016年0804（点石月刊）  ok.pdf',
                    ur'E:\点石月刊 发行\简报邮件正文内容.txt',
                   ]
    mail = MailProc(mail_matrix, accounts_list, mail_sub, mail_body, append_list)
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
        elif ERROR_SEND_TOO_MANY_NEED_WAIT == err:
            print(u"真的发太多了，等等吧")
            time.sleep(20)
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
            time.sleep(5)
        elif ERROR_SOME_EMAILS_FAILED == err:
            print(u"部分发送失败")
            fail_list += ret["FailedList"]


if __name__ == "__main__":
    p = chdir_myself()
    logging_init("SendMail.log")
    test_send_mail()
    logging_fini()


