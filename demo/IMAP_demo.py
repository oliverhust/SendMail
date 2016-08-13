#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import sys
import re
import time
import smtplib
import getpass, imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from mylog import *
from mail_list import *

#import pdb;  pdb.set_trace()


class Account:
    def __init__(self, mail_user, mail_passwd, mail_host, sender_name):
        self.user = mail_user
        self.passwd = mail_passwd
        self.host = mail_host
        self.sender_name = sender_name

    def auto_get_host(self):
        pass


def send_email(account, mail_list, sub, content_html, append_list):

    ENCODE = 'utf-8'
    me = account.sender_name + "<"+account.user+">"

    msg = MIMEMultipart()
    msg['Subject'] = sub
    msg['From'] = me
    msg['BCC'] = ";".join(mail_list)

    msg_text = MIMEText(content_html, 'html', ENCODE)
    msg.attach(msg_text)

    print_t("Read Appends")
    for each_append in append_list:
        f = open(each_append, 'rb')
        f_basename = os.path.basename(each_append).encode(ENCODE)
        msg_append = MIMEApplication(f.read())
        msg_append.add_header('Content-Disposition', 'attachment', filename=f_basename)
        msg.attach(msg_append)

    # --------------------------------------------------------------------------------------

    s = imaplib.IMAP4(account.host)
    s.login(account.user, account.passwd)




if __name__ == "__main__":
    pass
