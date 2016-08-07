#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
import logging
import xlrd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from mylog import *
from mail_list import *
#import pdb; pdb.set_trace()

#设置服务器，用户名、口令以及邮箱的后缀
MAIL_HOST = "mail.hust.edu.cn"
MAIL_USER = "M201571736@hust.edu.cn"
MAIL_PASS = "hjsg1qaz2wsx"
MAIL_POSTFIX = "hust.edu.cn"



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
    return(Head + Elems + "</body></html>\n\n\n\n")

###########################################################################
#                          将文本转换为Html中的元素
#参数：文本
#返回：文本元素
###########################################################################
def Html_TxtElem(txt):

    ret = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return("<pre>" + ret + "</pre>")


###########################################################################
#                            发送邮件函数
#mailto_list    收件人邮箱
#sub            邮件题目
#content_html   邮件内容
#append_list    附件列表
###########################################################################
def send_mail(mail_list, sub, content_html, append_list):

    ENCODE = 'utf-8'
    me = "刘泽宇" + "<"+MAIL_USER+">"

    msg = MIMEMultipart()
    msg['Subject'] = sub
    msg['From'] = me
    msg['BCC'] = ";".join(mail_list)

    msg_text = MIMEText(content_html, 'html', ENCODE)
    msg.attach(msg_text)

    logging("Read Appends")
    for each_append in append_list:
        f = open(each_append, 'rb')
        f_basename = os.path.basename(each_append).encode(ENCODE)
        msg_append = MIMEApplication(f.read())
        msg_append.add_header('Content-Disposition', 'attachment', filename=f_basename)
        msg.attach(msg_append)

    logging("Start to connect.")
    s = smtplib.SMTP()
    s.connect(MAIL_HOST)   #没网, 或DNS
    logging("Connetc success")
    s.login(MAIL_USER, MAIL_PASS) #用户名密码错误

    logging("Before Send Email, there are {} receivers.".format(len(mail_list)))
    try:
        err_mail = s.sendmail(me, mail_list, msg.as_string())
    except smtplib.SMTPRecipientsRefused, e:
        print("==============Catch SMTPRecipientsRefused Error================")
        print(e)
        print("-------")
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    logging("After Send Email.")
    s.close()
    print ("Send email success to " + repr(mail_list))


def test_send_email():
    print("---------------------test_send_email---------------------------")
    mail_list_my = [ "mmyzoliver@163.com", "1307408482@qq.com" ]
    mail_list = [mail_list_my[1]] + MAIL_LIST_ALL[1300:1300] + [mail_list_my[0]]
    subject = u'{}_HAHAH。此邮件为测试邮件， ——请删除, 谢谢——'.format(len(mail_list))
    body = u'''
2016年5月23日，李克强总理考察湖北十堰市民服务中心，细询营改增实施效果，并再次重申“所有行业税负只减不增”。
　　3月18日召开的国务院常务会议决定，为进一步减轻企业负担，促进经济结构转型升级，从今年5月1日起，将营改增试点范围扩大到建筑业、房地产业、金融业和生活服务业，并将所有企业新增不动产所含增值税纳入抵扣范围。4月30日，国务院印发《关于做好全面推开营改增试点工作的通知》和《全面推开营改增试点后调整中央与地方增值税收入划分过渡方案的通知》，要求各级政府平稳、有序开展工作，确保各行业税负只减不增。

　　截至目前，“营改增”攻坚战已在全国稳步有序铺展开来。房地产、建筑和生活服务业企业均已完成营改增后的首次报税，新增季度性报税的金融业和小规模纳税人也从7月1日起迎来首次申报期。预计营改增今年将为企业降低成本5000亿以上。
　　降费
　　2、阶段性降低社保公积金费率，每年为企业减负1000亿
　　为减轻企业负担，增强企业活力，促进增加就业和职工现金收入，4月13日召开的国务院常务会议决定阶段性降低企业社保缴费费率和住房公积金缴存比例。
　　4月20日，人力资源与社会保障部与财政部联合发布《关于阶段性降低社会保险费率的通知》，决定阶段性降低社会保险费率。《通知》规定：
　　一、5月1日起两年内，企业职工基本养老保险单位缴费比例超过2
'''
    append_list = [ ur'E:\点石月刊 发行\2016年0804（点石月刊）  ok.pdf',
                    ur'E:\点石月刊 发行\简报邮件正文内容.txt'
                    ]
    body = Html_TxtElem(body)
    send_mail(mail_list, subject, body, append_list)


def test_xls():
    print("---------------------xls_test---------------------------")
    xls_path = ur'E:\SystemDirectory\Desktop\新人培训\ComwareV7R001D001 GKM 测试 NETCONF GdoiGmGroups STC .xlsx'
    data = xlrd.open_workbook(xls_path) # 打开xls文件
    tables = data.sheets()
    print("{} Tales name at all.".format(len(tables)))
    print(tables)
    print data.sheet_names()
    table = data.sheets()[1] # 打开第一张表
    nrows = table.nrows # 获取表的行数
    for i in range(nrows): # 循环逐行打印
        if i == 0: # 跳过第一行
            continue
        print table.row_values(i)[:13] # 取前十三列


def chdir_myself():
    p = os.path.dirname(os.path.realpath(__file__))
    print("Change dir to MyPath = " + p)
    os.chdir(p)
    return p

    
def main():
    p = chdir_myself()
    logging_init("Demo1.log")
    #test_xls()
    test_send_email()
    logging("Exit the program.")
    logging_fini()
    
    
if __name__ == "__main__":
    main()
