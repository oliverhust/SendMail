#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import sys
import socket
import datetime
import platform
import subprocess

from err_code import *


g_check_same = None


def try_decode(str_raw, encoding_list=None):
    if encoding_list is None:
        encoding_list = ['gb18030', 'utf-8']

    err, err_info, text = ERROR_SUCCESS, u"", repr(str_raw)
    for each_encode in encoding_list:
        try:
            text = str_raw.decode(each_encode)
        except Exception, e:
            err, err_info = ERROR_DECODE_BODY_FAILED, unicode(e)
        else:
            err, err_info = ERROR_SUCCESS, u""
            break
    return err, err_info, text


def is_break_error(err):
    if ERROR_FINISH == err and \
       ERROR_OPEN_APPEND_FAILED == err and \
       ERROR_READ_APPEND_FAILED == err and \
       ERROR_CONNECT_FAILED == err and \
       ERROR_LOGIN_FAILED == err and \
       ERROR_SEND_FAILED_UNKNOWN_TOO_MANY == err:
        return True
    return False


def check_contain_chinese(check_str):
    try:
        str_decode = check_str.decode('utf-8')
    except Exception:
        return True
    for ch in str_decode:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def str_find_mailbox(mail_box):
    if type(mail_box) != str and type(mail_box) != unicode:
        return ""
    r = re.findall(r'\S+@\S+', mail_box)
    if r:
        if not check_contain_chinese(r[0]):
            return r[0]
    return ""


def str_get_domain(user_name):
    pos = user_name.find("@")
    if -1 != pos and pos + 1 < len(user_name):
        domain = user_name[pos+1:]
        return domain
    return ""


def str_is_domain_equal(mailbox1, mailbox2):
    if type(mailbox1) != str and type(mailbox1) != unicode:
        return False
    if type(mailbox2) != str and type(mailbox2) != unicode:
        return False
    pos1 = mailbox1.find("@")
    pos2 = mailbox2.find("@")
    if -1 == pos1 or -1 == pos2:
        return False
    domain1 = mailbox1[pos1+1:]
    domain2 = mailbox2[pos2+1:]
    if domain1 == domain2 and domain1 != "":
        return True
    return False


def str_is_contains(string, pattern_list):
    #  判断一个字符串中是否包含一个字符串列表中的任意一个字符串，存在返回匹配的索引，不存在返回-1
    for i, each_pattern in enumerate(pattern_list):
        if string.find(each_pattern) >= 0:
            return i
    return -1


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


# ############################## 系统相关  #######################################


def is_windows_system():
    return 'Windows' in platform.system()


def is_mac_system():
    return 'Darwin' in platform.system()


def os_shell(cmd):

    # 获取输出
    out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # 读取输出
    lines = out.stdout.read()

    # 编码转换
    try:
        result = lines.decode('utf-8')
    except:
        result = lines.decode('gb18030')
        print("Decode command {} output error.".format(repr(cmd)))

    out.wait()

    return result


def os_get_user_desktop():
    return os.path.join(os.path.expanduser("~"), 'Desktop')


def check_program_has_same(program_unique_port):
    global g_check_same
    ret = False
    g_check_same = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # 定义socket类型，网络通信，UDP
    try:
        g_check_same.bind(("127.0.0.1", program_unique_port))          # 套接字绑定的IP与端口
    except Exception:
        ret = True
    return ret


def check_program_has_same_fini():
    g_check_same.close()


def os_get_curr_dir():
    p = os.path.dirname(os.path.realpath(sys.argv[0]))
    p_decode = u"."
    try:
        p_decode = p.decode("gb18030")
    except Exception, e:
        print(u"Decode path of gb18030 failed:{}".format(e))
        try:
            p_decode = p.decode("utf-8")
        except Exception, e:
            print(u"Decode path of utf-8 failed:{}".format(e))
    print(u"Get MyPath = " + repr(p))

    return p_decode


def chdir_myself():
    p = os_get_curr_dir()
    if p != u".":
        os.chdir(p)
    return p


def get_time_str():
    now = datetime.datetime.now()
    time_str = now.strftime("%Y/%m/%d %H:%M:%S")
    return time_str


def print_t(log):
    time_str = get_time_str()
    content = u"[{}]\n{}".format(time_str, log)
    print(content)


def print_w(log):
    time_str = get_time_str()
    print(u"[{}][WARNING]\n{}".format(time_str, log))


def print_err(log):
    time_str = get_time_str()
    print(u"[{}][@@@ ERROR @@@]\n{}".format(time_str, log))
