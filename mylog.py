#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import datetime

f_Logging = None


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
    print(u"Change dir to MyPath = " + repr(p))

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
    content = u"[{}] {}".format(time_str, log)
    print(content)


def print_w(log):
    time_str = get_time_str()
    print(u"[{}][WARNING] {}".format(time_str, log))


def print_err(log):
    time_str = get_time_str()
    print(u"[{}][@@@ ERROR @@@] {}".format(time_str, log))


def logging_init(file_name):
    global f_Logging
    print(u"Start to init logging.")
    d = chdir_myself()
    print(u"Change dir to {}".format(repr(d)))
    log_full = d + u"\\" + file_name
    try:
        f_Logging = open(log_full, "a")
    except Exception, e:
        print(u"Try to write log file {} failed.".format(repr(log_full)))
        return

    print(u"Redirect the print to file.")
    sys.stdout = f_Logging
    sys.stderr = f_Logging


def logging_fini():
    f_Logging.close()