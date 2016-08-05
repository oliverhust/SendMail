#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

f_Logging = None


def logging(log):
    now = datetime.datetime.now()
    time_str = now.strftime("[%Y/%m/%d %H:%M:%S]")
    content = u"\n######## {} {}".format(time_str, log)
    logging_info(content)


def logging_warn(log):
    logging_info("[WARNING] "+"@"*16+" "+log+" "+"@"*16)


def logging_info(log):
    if isinstance(log, unicode):
        log = log.encode('gb18030')
    f_Logging.write(log + "\n")
    f_Logging.flush()


def logging_init(file_path):
    global f_Logging
    ret = 0
    try:
        f_Logging = open(file_path, "a")
    except Exception, e:
        f_Logging = None
        ret = 1
    else:
        f_Logging.write("\n" * 10 + "#" * 64)
        logging("Start the program.")
    return 1


def logging_fini():
    f_Logging.close()