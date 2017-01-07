#!/usr/bin/python
# -*- coding: utf-8 -*-

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
