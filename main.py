#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from mylog import *
from mail_list import *

# import pdb; pdb.set_trace()

ERROR_SUCCESS = 0
ERROR_FINISH = 1
ERROR_PAUSE = 2
ERROR_OPEN_APPEND_FAILED = 3
ERROR_READ_APPEND_FAILED = 4
ERROR_SEND_TOO_MANY = 5
ERROR_SEND_ONE_TOO_MANY = 6

class Account:
    def __init__(self, mail_user, mail_passwd, mail_host, sender_name):
        self.user = mail_user
        self.passwd = mail_passwd
        self.host = mail_host
        self.sender_name = sender_name


class MailProc:
    """ 发送邮件的主流程 """
    MAILS_IN_GROUP = 40
    EACH_GROUP_DALAY = 5000  # 毫秒
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
        self._CurrAccount = 0
        # 暂存当前要发送的邮件矩阵中的起始位置
        self._CurrLine = 0
        self._CurrRow  = 0
        # 暂存附件内容不用每次读取
        self._MsgAppendList = []

    def _group_mail_get(self):
        if self._CurrLine >= len(self._AccountsList):
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
            self._MailAppendList.append(msg_append)
        logging(ret[1])
        return ret

    def _send_one_group(self):
        mail_list = self._group_mail_get()
        if mail_list == ERROR_FINISH:
            return ERROR_FINISH, u"所有邮件都已尝试发送"
        err, err_info = self._read_append()
        if ERROR_SUCCESS != err:
            return err, err_info

        account = self._AccountsList[self._CurrAccount]
        me = account.sender_name + "<"+account.user+">"

        msg = MIMEMultipart()
        msg['Subject'] = self._MailSub
        msg['From'] = me
        msg['To'] = ";".join(mail_list)

        msg_text = MIMEText(self._MailBody, 'html', MailProc.ENCODE)
        msg.attach(msg_text)

        for each_append in self._MsgAppendList:
            msg.attach(each_append)

        s = smtplib.SMTP()
        s.connect(account.host)
        s.login(account.user, account.passwd)
        try:
            err_mail = s.sendmail(me, mail_list, msg.as_string())
        except smtplib.SMTPRecipientsRefused, e:
            err_mail = mail_list
            if len(self._AccountsList) != 1:
                err = ERROR_SEND_TOO_MANY
                self._CurrAccount =  (self._CurrAccount + 1) % len(self._AccountsList)
                account_next = self._AccountsList[self._CurrAccount]
                err_info = u"当前账号{}发送邮件过多被拒，切换到账号{}".format(account.user, account_next.user)
            else:
                err = ERROR_SEND_ONE_TOO_MANY
                err_info = u"当前账号{}发送邮件过多被拒，等待再次尝试".format(account.user)
        err_mail = err_mail.keys()

        s.close()
        logging("Send email success to " + repr(mail_list))
        return err, err_info

    def send_once(self, user_signal):
        """ 主要发送函数 该函数需被反复调用来发送
        user_singnal: 继续、暂停、终止
        返回：错误码, log信息(显示), 已发送列表, 发送失败列表
        """
        pass


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
    account1 = Account("M201571736@hust.edu.cn", "hjsg1qaz2wsx", "mail.hust.edu.cn", u"毛竹徐")
    account2 = Account("U201313778@hust.edu.cn", "dian201313778", "mail.hust.edu.cn", u"毛竹徐")
    mail_matrix = [ [""] ]
    i = 35
    n = 0
    while n < 200:
        mail_matrix.append(MAIL_LIST_ALL[n: n+i])
        n += i
        i += 1
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





if __name__ == "__main__":
    p = chdir_myself()
    logging_init("SendMail.log")
    test_send_mail()
    logging_fini()


