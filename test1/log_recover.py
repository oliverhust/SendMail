#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import xlrd
import xlwt
import xlutils


class Error(Exception):

    def __init__(self, error_info):
        self._ErrorInfo = error_info

    def __str__(self):
        return unicode(self._ErrorInfo)


class LogError(Error):
    pass


class LogRead:

    def __init__(self, log_file):
        self._LogFile = log_file
        self._f = None

    def get_start_time(self):
        pass

    def read_between_time(self, start_index, end_index):
        pass

    def get_mails(self):
        pass

    def _read_file(self):
        try:
            self._f = open(self._LogFile)
        except IOError, e:
            raise LogError(e)


class ExcelModify:

    def __init__(self):
        pass


class UI:

    def __init__(self):
        self._log_read = None
        self._excel_modify = None

    def

    def run(self):
        log_file_path = raw_input(u"输入log文件的路径名:")
        self._log_read = LogRead(log_file_path)
        try:
            self._log_read.


def main():
    ui_main = UI()
    ui_main.run()


if __name__ == '__main__':
    main()
