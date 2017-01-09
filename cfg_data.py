#!/usr/bin/python
# -*- coding: utf-8 -*-

from copy import deepcopy
from etc_func import str_get_domain


class Account:
    SEND_HOSTS = {"hust.edu.cn": "mail.hust.edu.cn",        "126.com": "smtp.126.com",
                  "163.com": "smtp.163.com",                "sina.cn": "smtp.sina.cn",
                  "sina.com": "smtp.sina.com.cn",           "sohu.com": "smtp.sohu.com",
                  "263.net": "smtp.263.net",                "gmail.com": "smtp.gmail.com",
                  "tom.com": "smtp.tom.com",                "yahoo.com": "smtp.mail.yahoo.com",
                  "yahoo.com.cn": "smtp.mail.yahoo.com",    "21cn.com": "smtp.21cn.com",
                  "qq.com": "smtp.qq.com",                  "x263.net": "smtp.263.net",
                  "foxmail.com": "smtp.foxmail.com",        "hotmail.com": "smtp.live.com",
                  "hainan.net": "smtp.hainan.net",          "139.com": "smtp.139.com", }

    RECV_HOSTS = {"hust.edu.cn": "mail.hust.edu.cn",        "mail.hust.edu.cn": "mail.hust.edu.cn", }

    def __init__(self, mail_user, mail_passwd, mail_host, sender_name):
        self.user = mail_user
        self.passwd = mail_passwd
        self.host = mail_host           # 发送和接收用的host不一样，只存发送的host到DB
        self.sender_name = sender_name

    def __repr__(self):
        return u"Account({}, {}, {})".format(self.user, self.host, self.sender_name)

    @staticmethod
    def get_send_host(user):
        domain = str_get_domain(user)
        if len(domain) == 0:
            return u""
        if domain in Account.SEND_HOSTS:
            host = unicode(Account.SEND_HOSTS[domain])
            return host
        return u""

    @staticmethod
    def get_recv_host(user):
        domain = str_get_domain(user)
        if len(domain) == 0:
            return u""
        if domain in Account.RECV_HOSTS:
            host = unicode(Account.RECV_HOSTS[domain])
            return host
        return u""

    def has_host(self):
        if self.host is None or len(self.host) == 0:
            return False
        return True


class CfgNdr(dict):
    # 接收退信的设置

    POS_INVALID = 'Invalid'
    POS_BODY = 'Body'
    POS_DELIVERY = 'Delivery'

    _VOID_CFG = {
            'Domain':       u'',
            'Enable':       False,
            'ImapHost':     u'',
            'UseSSL':       True,
            'SysEmail':     u'',

            # 后面两部分用来做内容识别(识别退信邮箱、退信错误信息)
            'Mail':
            {
                            'Pos':      POS_INVALID,
                            'PosKey':   u'',
                            'RePatt':   u'',
            },
            'Info':
            {
                            'Pos':      POS_INVALID,
                            'PosKey':   u'',
                            'RePatt':   u'',
            },
    }
    # 'MailPos':      POS_INVALID,
    # 'MailPosKey':   u'',
    # 'MailRePatt':   u'',
    # 'InfoPos':      u'',
    # 'InfoPosKey':   u'',
    # 'InfoRePatt':   u'',

    # noinspection PyTypeChecker
    def __init__(self, cfg_iter=None):
        if type(cfg_iter) == dict:
            dict.__init__(self, deepcopy(cfg_iter))
        elif type(cfg_iter) in (list, tuple, set) and cfg_iter:
            (self['Domain'], self['Enable'], self['ImapHost'], self['UseSSL'], self['SysEmail'],
             self['Mail']['Pos'], self['Mail']['PosKey'], self['Mail']['RePatt'],
             self['Info']['Pos'], self['Info']['PosKey'], self['Info']['RePatt']) = cfg_iter
        else:
            dict.__init__(self, deepcopy(self._VOID_CFG))

        if not self.check():
                print(u"Warning: invalid CfgNdr: {}".format(self))

    # noinspection PyTypeChecker
    def __getitem__(self, key):
        if key not in self:
            return None
        return dict.__getitem__(self, key)

    def check(self):
        if not set(self._VOID_CFG.keys()) <= set(self.keys()):
            return False
        if not set(self._VOID_CFG['Mail'].keys()) <= set(self['Mail'].keys()):
            return False
        if not set(self._VOID_CFG['Info'].keys()) <= set(self['Info'].keys()):
            return False
        return True

    def to_tuple(self):
        return (self['Domain'], self['Enable'], self['ImapHost'], self['UseSSL'], self['SysEmail'],
                self['Mail']['Pos'], self['Mail']['PosKey'], self['Mail']['RePatt'],
                self['Info']['Pos'], self['Info']['PosKey'], self['Info']['RePatt'])

    def is_enable(self):
        return self['Enable']

    def get_sys_email(self):
        return self['SysEmail']

    def get_imap_host(self):
        return self['ImapHost']

    def use_ssl(self):
        return self['UseSSL']



