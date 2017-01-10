#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
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

# from mylog import *
# from cfg_data import *
# from etc_func import *
# from ndr import *

import pdb
# import pdb;  pdb.set_trace()


def import_all():
    for module_name in sys.modules.keys():
        if module_name[0] != '_' and -1 == module_name.find('.'):
            command = 'import {}'.format(module_name)
            print(command)
            exec command
            exec('print({})'.format(module_name))
            time.sleep(0.125)


if __name__ == '__main__':

    # import_all()
    # exec("import {}{}".format('urll', 'ib2'))
    while True:
        cmd = raw_input(u'>>> ')
        try:
            exec cmd
        except Exception, e:
            print(u"{} {}".format(type(e), e))
