#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from err_code import *
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


class HtmlImg:

    __re_correct = re.compile(ur'''(<img\b[^<>]*?\bsrc\s*=\s*['"]?\s*)file:///\s*([^'"<>]*)([^<>]*?/?\s*>)''')
    __re_img_src = re.compile(ur'''(<img\b[^<>]*?\bsrc\s*=\s*['"]?\s*)([^'"<>]*)([^<>]*?/?\s*>)''')

    def __init__(self, html_text):
        self._html = unicode(html_text)

    def html(self):
        return self._html

    def correct_img_src(self):
        # 去除粘贴图片路径前的 file:///
        self._html = self.__re_correct.subn(ur'\1\2\3', self._html)[0]
        return self._html

    def get_img_src(self):
        fd_all = self.__re_img_src.findall(self._html)
        return [x[1] for x in fd_all]

    def replace_img_src(self, replace_img_src_list):

        class ReRepl:
            def __init__(self):
                self._n = 0

            def __call__(self, match_obj):
                if self._n < len(replace_img_src_list):
                    replace_patt = u'{}{}{}'.format(match_obj.group(1),
                                                    replace_img_src_list[self._n],
                                                    match_obj.group(3))
                else:
                    replace_patt = match_obj.group(0)
                self._n += 1
                return replace_patt

        self._html = self.__re_img_src.sub(ReRepl(), self._html)
        return self._html


class MailResource:

    def __init__(self, resource_path, name=None, bin_data=None):

        self.path = resource_path
        if name is not None:
            self.name = name
        else:
            self.name = os.path.basename(resource_path)
        self.bin_data = bin_data

    def __repr__(self):
        return u"MailRC({}, {})".format(repr(self.path), repr(self.name))


class MailContent:
    """  邮件内容：主题、正文、附件 """
    ENCODE = 'gb18030'

    def __init__(self, mail_sub, mail_html_body, append_resource_list=None, body_resource_list=None):
        self._Sub = mail_sub    # 原始主题
        self._Body = mail_html_body  # html正文

        self._AppendList = []  # MailResource/path
        if append_resource_list:
            for each_append in append_resource_list:
                if isinstance(each_append, unicode):
                    self._AppendList.append(MailResource(each_append))
                elif isinstance(each_append, MailResource):
                    self._AppendList.append(each_append)

        self._BodyResourceList = []    # MailResource/path
        if body_resource_list:
            for each_resource in body_resource_list:
                if isinstance(each_resource, unicode):
                    self._BodyResourceList.append(MailResource(each_resource))
                elif isinstance(each_resource, MailResource):
                    self._BodyResourceList.append(each_resource)

        # 暂存附件/内部资源内容不用每次读取
        self.__msg = None

    def sub(self):
        return self._Sub

    def body(self):
        return self._Body

    def append_resource_list(self):
        return self._AppendList[:]

    def body_resource_list(self):
        return self._BodyResourceList[:]

    def to_msg(self):
        if self.__msg is not None:          # 暂存附件/内部资源内容不用每次读取
            return ERROR_SUCCESS, u"", self.__msg

        self.__msg = MIMEMultipart()        # __msg下面存放 MIMEMultipart('related')(含正文) 和 附件
        err, err_info = self.__load_body_resource()
        if err != ERROR_SUCCESS:
            return err, err_info, self.__msg

        err, err_info = self.__load_append_resource()
        return err, err_info, self.__msg

    def modify_body_with_resource(self):
        # 由于原html中的图片路径不能在邮件/数据库中传递，需要修改
        h = HtmlImg(self._Body)
        old_src_name = h.get_img_src()
        new_src_name = ["cid:" + os.path.basename(s) for s in old_src_name]  # 发送/存储的名字

        self._Body = h.replace_img_src(new_src_name)

        # 对应修改self._BodyResourceList中的name部分
        for i, old_rc in enumerate(self._BodyResourceList):
            if old_rc.name in old_src_name:
                old_rc.name = new_src_name[old_src_name.index(old_rc.name)]

    def fill_body_resource_bin_data(self):
        # 将资源文件的二进制数据读到内存(body_resource_list())
        err, err_info = ERROR_SUCCESS, u""
        for i in range(len(self._BodyResourceList)):
            if self._BodyResourceList[i].bin_data is None:
                err, err_info, bin_data = self.__body_resource_bin_data(i)
                if err != ERROR_SUCCESS:
                    break
                self._BodyResourceList[i].bin_data = bin_data
        return err, err_info

    def __load_body_resource(self):
        ret = ERROR_SUCCESS, u""

        self.__msg['Subject'] = self._Sub
        body_part = MIMEText(self._Body, 'html', MailContent.ENCODE)

        if not self._BodyResourceList:
            self.__msg.attach(body_part)
            return ret

        msg_resource = MIMEMultipart('related')
        msg_resource.attach(body_part)

        # 加载图片资源(目前只有图片)
        ret = self.__load_body_resource_img(msg_resource)
        if ret[0] != ERROR_SUCCESS:
            return ret

        self.__msg.attach(msg_resource)
        return ret

    def __load_append_resource(self):
        """ 读取附件，失败则暂停 """
        ret = ERROR_SUCCESS, u"读取附件成功"

        for each_append in self._AppendList:

            try:
                with open(each_append.path, 'rb') as f:
                    file_content = f.read()
            except IOError as e:
                ret = ERROR_OPEN_APPEND_FAILED, u"无法打开附件: {} \n{}".format(each_append.path, e)
                break

            msg_append = MIMEApplication(file_content)
            f_name = each_append.name.encode(MailContent.ENCODE)
            msg_append.add_header('Content-Disposition', 'attachment', filename=f_name)
            self.__msg.attach(msg_append)

        print(ret[1])
        return ret

    def __load_body_resource_img(self, msg_resource):
        # 加载图片资源
        for each_img in self._BodyResourceList:

            try:
                with open(each_img.path, 'rb') as f:
                    img_data = f.read()
            except IOError as e:
                return ERROR_READ_BODY_RESOURCE_FAILED, u"加载某个资源({})失败 {}".format(each_img.path, e)

            content_id = unicode(each_img.name)
            if content_id.startswith(u"cid:"):
                content_id = content_id[4:]

            m_img = MIMEImage(img_data)
            m_img.add_header('Content-ID', content_id)
            msg_resource.attach(m_img)

        return ERROR_SUCCESS, u""

    def __body_resource_bin_data(self, rc_index):
        # 将资源文件的二进制数据读到内存(body_resource_list())
        len_rc_list = len(self._BodyResourceList)
        if rc_index >= len_rc_list:
            return ERROR_READ_BODY_RESOURCE_FAILED, u"输入的资源索引值过大: {} > {}".format(rc_index, len_rc_list), ""

        try:
            with open(self._BodyResourceList[rc_index].path, 'rb') as f:
                bin_data = f.read()
        except IOError as e:
            return ERROR_READ_BODY_RESOURCE_FAILED, u"读取资源二进制数据失败: {}".format(e)

        return ERROR_SUCCESS, u"", bin_data


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



