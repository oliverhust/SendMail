#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


###########################################################################
#                            发送邮件函数
#mailto_list    收件人邮箱
#sub            邮件题目
#content_html   邮件内容
#append_list    附件列表
###########################################################################
def send_mail(mail_list, sub, content_html, append_list):

    ENCODE = 'utf-8'
    me=MAIL_USER+"<"+MAIL_USER+"@"+MAIL_POSTFIX+">"

    msg = MIMEMultipart()
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(mail_list)

    msg_text = MIMEText(content_html, 'html', ENCODE)
    msg.attach(msg_text)

    for each_append in append_list:
        f = open(each_append, 'rb')
        f_basename = os.path.basename(each_append).encode(ENCODE)
        msg_append = MIMEApplication(f.read())
        msg_append.add_header('Content-Disposition', 'attachment', filename=f_basename)
        msg.attach(msg_append)

    s = smtplib.SMTP()
    s.connect(MAIL_HOST)
    s.login(MAIL_USER, MAIL_PASS)
    s.sendmail(me, mail_list, msg.as_string())
    s.close()
    print ("Send email success to " + repr(mail_list))





if __name__ == "__main__":
    pass



