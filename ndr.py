#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import imaplib
import email

from mylog import *
from cfg_data import *
from etc_func import *

# import pdb;  pdb.set_trace()


class RecvImap:
    """ 接受IMAP邮件 """
    DECODINGS = ['utf-8', 'gb18030']

    DATETIME_STR = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    def __init__(self, host, user, passwd, recv_size=32768):
        self._Host = host
        self._User = user
        self._Passwd = passwd
        self._RecvSize = int(recv_size)  # 一封邮件只接收前面多少个字节，None为无限制

        self._m = None  # IMAP连接

    def __del__(self):
        self.logout()

    def logout(self):
        if self._m is not None:
            self._m.logout()
            self._m = None

    def login(self, use_ssl=True):
        err, err_info = ERROR_SUCCESS, u""
        try:
            if use_ssl:
                self._m = imaplib.IMAP4_SSL(self._Host)
            else:
                self._m = imaplib.IMAP4(self._Host)
        except Exception, e:
            err = ERROR_IMAP_CONNECT_FAILED
            err_info = u"连接服务器{}失败: {}".format(self._Host, e)
            return err, err_info
        try:
            self._m.login(self._User, self._Passwd)
        except Exception, e:
            err = ERROR_IMAP_LOGIN_FAILED
            err_info = u"账号{}登录失败: {}".format(self._User, e)
        return err, err_info

    def search_from_since(self, from_who, datetime_since):   # 时间相等也算
        # 解析收到的邮件  {'Date': datetime, 'Suffix': u"", 'Body': u"", 'Delivery': None(字典)}
        # noinspection PyUnusedLocal
        for each_dir in self._for_each_directory():
            for parsed_msg in self._search_from_since_in_dir(from_who, datetime_since):
                yield parsed_msg

    @staticmethod
    def _try_decode(body, charset=None):
        if type(body) == unicode:
            return body
        if charset:
            charset_all = [charset] + RecvImap.DECODINGS
        else:
            charset_all = RecvImap.DECODINGS

        ret = None
        for each_charset in charset_all:
            try:
                ret = body.decode(each_charset)
            except:
                pass
            else:
                break

        if type(ret) != unicode:
            ret = unicode(repr(body))

        return ret

    @staticmethod
    def _try_get_charset(part):
        charset = part.get_charset()
        if charset is not None:
            return charset
        if 'Content-Type' in part:
            find_s = re.findall(r'charset="([^"]+)"', part['Content-Type'])
            if find_s:
                charset = find_s[0]
        return charset

    @staticmethod
    def _imap_str2datetime(str_date):
        time_str = re.findall(r'\d+ \w+ \d{4} \d+:\d+:\d+', str_date)
        if not time_str:
            return None
        my_str = time_str[0]
        for i, each_month in enumerate(RecvImap.DATETIME_STR):
            if each_month in my_str:
                my_str = my_str.replace(each_month, str(i+1))
        dt = datetime.datetime.strptime(my_str, "%d %m %Y %H:%M:%S")
        # dt = datetime.datetime.strptime(my_str, "%d %b %Y %H:%M:%S")
        return dt

    @staticmethod
    def _imap_datetime2str(dt):
        str_date = dt.strftime(u"%d-{}-%Y")   # 精确到天
        str_date = str_date.format(RecvImap.DATETIME_STR[dt.month-1])
        return str_date

    @staticmethod
    def _parse_email(dat):
        msg_all = {'Date': None, 'Suffix': u"", 'Body': u"", 'Delivery': None}
        part_count = len(dat) - 1
        if part_count <= 0:
            return msg_all

        for i in range(part_count):
            msg_tmp = RecvImap._parse_email_part(dat[i][1])
            # 添加msg_tmp到msg_all
            for k, v in msg_tmp.iteritems():
                if v:
                    msg_all[k] = v
        return msg_all

    @staticmethod
    def _parse_email_part(msg_part):
        msg_ret = {}
        msg = email.message_from_string(msg_part)

        if 'Date' in msg:
            msg_ret['Date'] = RecvImap._imap_str2datetime(msg['Date'])

        is_last_part_delivery = False
        had_read_first_txt = False

        for part in msg.walk():
            content_type = part.get_content_type()

            if content_type == 'message/delivery-status' and is_last_part_delivery is False:
                # 获取第一个message/delivery-status (必须是text/plain紧跟其后)
                is_last_part_delivery = True

            elif is_last_part_delivery:
                is_last_part_delivery = None  # 防止下一次又进入
                # noinspection PyTupleAssignmentBalance
                msg_ret['Delivery'] = RecvImap._get_part_delivery_dict(part)

            elif not part.is_multipart() and had_read_first_txt is False:
                # 取除message/delivery-status外的第一个非multipart (text/html)
                had_read_first_txt = True
                msg_ret['Body'], msg_ret['Suffix'] = RecvImap._get_part_payload_text(part)

        return msg_ret

    @staticmethod
    def _get_part_payload_text(part):
        content_type = part.get_content_type()
        if content_type == 'text/plain':
            suffix = 'text'
        elif content_type == 'text/html':
            suffix = 'html'
        else:
            suffix = 'unknown'

        charset = RecvImap._try_get_charset(part)
        payload = try_decode(part.get_payload(decode=True), charset, fail_ret_repr=True)
        return payload, suffix

    @staticmethod
    def _get_part_delivery_dict(part):
        charset = RecvImap._try_get_charset(part)
        ret_dict = {}
        for k, v in part.items():
            k_decode = try_decode(k, charset, fail_ret_repr=True)
            v_decode = try_decode(v, charset, fail_ret_repr=True)
            ret_dict[k_decode] = v_decode
        return ret_dict

    @staticmethod
    def _get_valid_mail_directory(unparsed_dir_list):
        not_need_dir_info = [r"\Drafts", r"\Sent", r"\Trash", r"\Junk"]
        final_dir_list = []
        for each_unparsed in unparsed_dir_list:
            tmp = re.findall(r'\(([^)]*)\)\s+"/"\s+"([^"]+)"', each_unparsed)
            if tmp:
                tmp_dir_info, tmp_dir_name = tmp[0][0], tmp[0][1]
                if str_is_contains(tmp_dir_info, not_need_dir_info) == -1:  # 不在not_need_dir中
                    final_dir_list.append(tmp_dir_name)
        return final_dir_list

    def _for_each_directory(self):
        d = self._m.list()
        print(u"Get all email dir: {}".format(d))
        if d[0] == 'OK':
            valid_dir_list = self._get_valid_mail_directory(d[1])
            print(u"Filter valid email dir: {}".format(valid_dir_list))
            for each_dir in valid_dir_list:
                print_t(u"IMAP select dir {}".format(each_dir))
                try:
                    ret_sel = self._m.select(each_dir, True)
                except Exception, e:
                    print(u"Select dir {} failed: {}".format(each_dir, e))
                    continue
                if ret_sel[0] != 'OK':
                    print(u"Select dir {} failed, reason: {}".format(each_dir, ret_sel[1]))
                    continue
                yield each_dir

    def _search_from_since_in_dir(self, from_who, datetime_since):   # 时间相等也算
        str_date = self._imap_datetime2str(datetime_since)
        print(u"Search imap: from [{}], since [{}]".format(from_who, str_date))

        if not from_who:
            typ, all_data = self._m.search(None, 'SINCE', str_date)
        else:
            typ, all_data = self._m.search(None, 'FROM', from_who, 'SINCE', str_date)
        if typ == 'OK':
            nums_all = all_data[0].split()
            print(u"Get email id in curr dir: {}".format(nums_all))
            if nums_all:
                num_list = self._get_since_num_list(nums_all, datetime_since)   # 二分查找
                for num in num_list:
                    parsed_msg = self._get_num_body(num, datetime_since)
                    if parsed_msg is not None:
                        yield parsed_msg

    def _get_since_num_list(self, nums_all, datetime_since):
        # 二分查找法找到第一封刚好大于datetime_since的邮件的num的位置  失败返回位置0
        start_pos = None
        if not nums_all:
            return []

        dt = None
        num_list = nums_all[:]
        x, y = 0, len(num_list) - 1   # 初始区间

        while True:
            mid = int((x + y) / 2)
            parsed_msg = self._get_num_body(num_list[mid], None)  # 获取指定邮件的时间
            dt = None if parsed_msg is None else parsed_msg['Date']
            if dt is None:   # 无法获取到时间的从num_list删除
                del(num_list[mid])
                if num_list:
                    y -= 1       # 重新计算区间
                else:
                    break
            elif dt < datetime_since:
                if mid + 1 < len(num_list):
                    x = mid + 1
                else:
                    break
            else:           # 大于或等于 (等于的情况下取第一个相等的)
                y = mid
                if x == y:
                    start_pos = mid
                    break

        if start_pos is None:
            print(u"Can not find start num suitable.")
            return []
        else:
            print(u"Get imap start num = {}, datetime = {}".format(num_list[start_pos], dt))
            index = nums_all.index(num_list[start_pos])
            return nums_all[index:][::-1]           # 不用num_list是用户可能删邮件 逆序 从新到旧

    def _get_num_body(self, num, must_datetime_since=None):
        # 获取指定序号(字符串)邮件的时间和内容 无法获取或时间不符则返回None
        num = str(num)

        # '(RFC822.HEADER BODY.PEEK[1])'   '(BODYSTRUCTURE)'
        try:
            if self._RecvSize:
                typ, dat = self._m.fetch(num, '(BODY.PEEK[]<0.{}>)'.format(self._RecvSize))
            else:
                typ, dat = self._m.fetch(num, '(BODY.PEEK[])')
        except:
            return None
        if typ != 'OK':
            return None

        # 解析收到的邮件  {'Date': None, 'Suffix': u"", 'Body': u"", 'Delivery': None}
        try:
            parsed_msg = self._parse_email(dat)
        except Exception, e:
            print("Parse an email failed, num = {}, err: {}".format(num, e))
            return None

        # 检查邮件的时间
        if not parsed_msg['Date']:
            print("A letter does not has time str, num = {}".format(num))
            return None
        elif must_datetime_since and parsed_msg['Date'] < must_datetime_since:
            return None

        return parsed_msg


class NdrCfgProc:

    __CFG_HUST = {
            'Domain':       u'hust.edu.cn',
            'Enable':       True,
            'ImapHost':     u'mail.hust.edu.cn',
            'UseSSL':       False,
            'SysEmail':     u'postmaster@hust.edu.cn',
            'Mail':
            {
                            'Pos':      CfgNdr.POS_DELIVERY,
                            'PosKey':   u'Final-Recipient',
                            'RePatt':   RE_PATT_MAILBOX,
            },
            'Info':
            {
                            'Pos':      CfgNdr.POS_DELIVERY,
                            'PosKey':   u'Diagnostic-Code',
                            'RePatt':   u'.*',
            },
    }

    __CFG_HUST_MAIL = deepcopy(__CFG_HUST)
    __CFG_HUST_MAIL['Domain'] = u'mail.hust.edu.cn'

    __CFG_GMAIL = {
            'Domain':       u'gmail.com',
            'Enable':       True,
            'ImapHost':     u'imap.gmail.com',
            'UseSSL':       True,
            'SysEmail':     u'mailer-daemon@googlemail.com',
            'Mail':
            {
                            'Pos':      CfgNdr.POS_BODY,
                            'PosKey':   u'',
                            'RePatt':   RE_PATT_MAILBOX,
            },
            'Info':
            {
                            'Pos':      CfgNdr.POS_BODY,
                            'PosKey':   u'',
                            'RePatt':   ur'(?m)Technical details of permanent failure:\s+((?:.|\n)*?)\s+----- Original',
            },
    }

    # 所有的默认配置集合到这里
    __CFG_LIST_ALL = [__CFG_HUST, __CFG_HUST_MAIL, __CFG_GMAIL]
    __CFG_DEFAULT = {cfg['Domain']: CfgNdr(cfg) for cfg in __CFG_LIST_ALL}

    def __init__(self, mail_db):
        self.__db = mail_db

    def get_ndr_cfg(self, domain):
        # 如果数据库有则取数据库，没有且该域名有默认配置返回默认配置，不支持返回None
        db_ndr_cfg = self.__db.get_ndr_cfg(domain)
        if db_ndr_cfg:
            return db_ndr_cfg
        return self.default_ndr_cfg(domain)

    def get_ndr_cfg_by_user(self, user_email):
        domain = str_get_domain(user_email)
        if not domain:
            return None
        return self.get_ndr_cfg(domain)

    def add_ndr_cfg(self, ndr_cfg):
        # 用户设置并保存ndr_cfg到数据库
        return self.__db.add_ndr_cfg([ndr_cfg])

    def default_ndr_cfg(self, domain):
        if domain not in self.__CFG_DEFAULT:
            return None
        return self.__CFG_DEFAULT[domain]


class NdrContent:

    __SUGGEST = [
        (r'DNS query error', u'收件人有误：域名错误'),
        (r'try another server', u"对方原服务器不存在"),
        (r"can't receive outdomain", u"对方无法接收外域邮件"),
        (r'((user|mailbox|account|recipient).*(not exist|not found|disabled|unavailable|unknown|suspended))|'
         r'Invalid recipient|no such user', u'收件人不存在'),
        (r'Quota exceeded|size exceed|mailbox.* full|exceed.* limit|over quota', u'对方邮箱已满或禁用'),
        (r'user locked', u"收件人账户被锁定"),
        (r'too many recipient', u"单封邮件收件人过多"),
        (r'MX query return retry', u'MX解析错误，尝试重发'),
        (r'Connection frequency|frequency limited', u"发信服务器被拒:连接频繁"),
        (r'Can not connect|Connection timed out|Connection.* fail', u"无法连接该邮箱域名"),
        (r'Service unavailable.*Client Host.*blocked', u'发信服务器被加入黑名单'),
        (r'IP .* block list|Invalid IP|addr.* blacklist|black ip', u'发信服务器IP地址被封'),
        (r'Address rejected', u"发信服务器被拒"),
        (r"sending MTA's poor reputation|Mail content denied", u"被对方认为垃圾邮件"),
        (r'domain is notwelcome|Connection refused|Relaying denied|spam|spammers', u'被对方服务器拒收'),
    ]

    __RE_SUGGESTS = [re.compile(r'(?i)' + x[0]) for x in __SUGGEST]

    def __init__(self, ndr_cfg):
        self.__NdrCfg = ndr_cfg
        self.__re_mail = re.compile(ndr_cfg['Mail']['RePatt'])
        self.__re_info = re.compile(ndr_cfg['Info']['RePatt'])

    def recognize(self, parsed_msg):
        # 识别退信内容，不识别返回{}  返回格式 {'Mail': u'', 'Info': u'', 'Suggestion': u''}
        recgn_result = {}
        mail = self.__search_msg(parsed_msg, self.__NdrCfg['Mail'], self.__re_mail)
        info = self.__search_msg(parsed_msg, self.__NdrCfg['Info'], self.__re_info)
        if mail and info:
            recgn_result['Mail'] = mail
            recgn_result['Info'] = info
            recgn_result['Suggestion'] = self.__make_suggestion(info)
        return recgn_result

    @staticmethod
    def __search_msg(parsed_msg, search_info, regex_obj):
        # 按照搜索信息格式从消息搜索字符串 (若有多个匹配去第一个)
        results = []
        if search_info['Pos'] == CfgNdr.POS_BODY and parsed_msg['Body']:
            results = regex_obj.findall(parsed_msg['Body'])
        elif search_info['Pos'] == CfgNdr.POS_DELIVERY and parsed_msg['Delivery']:
            pos_key = search_info['PosKey']
            if pos_key in parsed_msg['Delivery']:
                results = regex_obj.findall(parsed_msg['Delivery'][pos_key])

        if not results:
            return []
        return results[0]

    @staticmethod
    def __make_suggestion(ndr_info):

        final_suggest = u""
        for i, re_obj in enumerate(NdrContent.__RE_SUGGESTS):
            if re_obj.search(ndr_info):
                final_suggest = NdrContent.__SUGGEST[i][1]

        return final_suggest


class NdrProc(threading.Thread, NdrCfgProc):
    """  退信处理 主线程+真正接收退信的线程"""
    def __init__(self, account_list, mail_db):
        threading.Thread.__init__(self)
        NdrCfgProc.__init__(self, mail_db)
        self._AccountList = account_list[:]    # 只用其中的用户名密码
        self._start_time = None
        self._db = mail_db
        self._accounts_last_time = {}

        # 线程共享数据
        self._lock = threading.RLock()
        self._err_info = u""
        self._unread_data_num = 0
        self._user_pause = False
        self._has_finish_a_loop = False
        # ndr_data_list: [{'Date': datetime, 'Mail': u'', 'Info': u'', 'Suggestion': u''}...]
        self._ndr_data = []     # [{时间，退回的邮箱， 出错信息， 建议}...]

    def event_start_send(self, start_time=None):
        if start_time is None:
            self._start_time = datetime.datetime.now()
        else:
            self._start_time = start_time
        self._proc_with_db()

        # [debug] 测试接收功能
        # self._start_time = datetime.datetime(2016, 8, 1, 16, 45, 56)

    def get_used_user_list(self):
        return [account.user for account in self._AccountList]

    def start_thread(self):
        self.start()

    def get_data(self):
        # 供外部定时调用 返回： 错误信息， Ndr信息， 总数， 是否已完成一轮
        # 其中Ndr信息为 [{'Date': datetime, 'Mail': u'', 'Info': u'', 'Suggestion': u''}...]
        self._lock.acquire()
        ndr_all_count = len(self._ndr_data)
        if self._unread_data_num > 0:
            ret = self._err_info, self._ndr_data[-self._unread_data_num:], ndr_all_count, self._has_finish_a_loop
        else:
            ret = self._err_info, [], ndr_all_count, self._has_finish_a_loop
        self._unread_data_num = 0
        self._err_info = u""
        self._lock.release()
        return ret

    def get_all_ndr_data(self):  # 仅限线程终止后调用
        return self._ndr_data

    def stop_proc(self):
        # 尝试停止和等待子线程
        self._lock.acquire()
        self._user_pause = True
        self._lock.release()
        self.join()

    def run(self):
        # 线程运行的任务  出错则下一个账号
        str_start_time = self._start_time.strftime(u"%Y/%m/%d %H:%M:%S")
        while not self._get_is_user_paused():
            self._write_err_info(u"开始接收退信:since {}".format(str_start_time), True)
            for account in self._AccountList:

                ndr_cfg = self.get_ndr_cfg_by_user(account.user)
                if ndr_cfg and ndr_cfg.is_enable():
                    self._write_err_info(u"当前账号: {}".format(account.user))
                    m = RecvImap(ndr_cfg.get_imap_host(), account.user, account.passwd)
                    err, err_info = m.login(ndr_cfg.use_ssl())
                    if err == ERROR_SUCCESS:
                        ndr_content = NdrContent(ndr_cfg)
                        since_time = self._account_last_time_get(account.user, self._start_time)  # 每轮结束每个账号的时间自动向后推
                        for msg in m.search_from_since(ndr_cfg.get_sys_email(), since_time):

                            recgn_result = ndr_content.recognize(msg)  # 同一封信件多次循环中可能会被返回多次(时间相同)
                            if recgn_result:    # 能识别
                                self._each_ndr_proc(recgn_result, msg['Date'])  # 如果已存在不会重复添加
                            self._account_last_time_save(account.user, msg['Date'])
                            if self._get_is_user_paused():  # 用户终止操作,不可恢复
                                break
                    else:
                        self._write_err_info(err_info)
                    m.logout()
                else:
                    self._write_err_info(u"跳过账号: {}".format(account.user))
                if self._get_is_user_paused():
                    break

            self._set_has_finish_a_loop()
            if self._test_pause_and_sleep(60):
                break

        self._write_err_info(u'终止接收退信操作', True)

    # -------------------------------------------------------------------------
    def _proc_with_db(self):
        # 查询数据库有无记录，有的话比较合并[曾用账号]，开始时间不变；没有的话就直接写入
        dt_old = self._db.get_start_time()
        if dt_old:
            account_list_old = self._db.get_used_accounts()
            users_old = [x.user for x in account_list_old]
            save_account_list = account_list_old[:]
            for each_account in self._AccountList:    # 如果现在的账户有新的就添加到"曾用账户"
                if each_account.user not in users_old:   # 通过用户名来判断
                    print(u"Add a new used-account {}".format(each_account.user))
                    save_account_list.append(each_account)
            self._db.save_used_accounts(save_account_list)
            # 更新本地数据
            self._start_time = dt_old
            self._AccountList = save_account_list
        else:
            self._db.save_start_time(self._start_time)
            self._db.save_used_accounts(self._AccountList)

    def _thread_db_del_success_sent(self, list_to_del_origin):
        # 从DB中删除已成功的(存在才删)，并把它添加到失败的，更新DB中的进度
        list_to_del = []
        for each_del in list_to_del_origin:
            if self._db.is_exist_success_sent(each_del):
                list_to_del.append(each_del)
        if not list_to_del:
            return

        self._db.del_success_sent(list_to_del)
        progress = self._db.get_sent_progress()
        if progress:
            success, failed, not_sent = progress
            success -= len(list_to_del)
            failed += len(list_to_del)
            self._db.save_sent_progress(success, failed, not_sent)

    def _thread_db_is_a_new_ndr(self, curr_mail, mail_time):
        # 有可能识别退信后重发成功，此时以前的退信应忽略
        old = self._db.get_ndr_mail(curr_mail)
        ret = False
        if old:
            old_dt = old[1]
            if mail_time > old_dt:
                ret = True
                self._db.add_ndr_mail(curr_mail, mail_time)
        else:
            ret = True
            self._db.add_ndr_mail(curr_mail, mail_time)
        return ret

    def _write_err_info(self, err_info, show_time=True):
        if show_time:
            now = datetime.datetime.now()
            time_str = now.strftime(u"%H:%M:%S")
            str_info = u"[{}] {}".format(time_str, err_info)
        else:
            str_info = err_info
        print(str_info)

        self._lock.acquire()
        self._err_info += str_info + u"\n"
        self._lock.release()

    def _each_ndr_proc(self, recgn_result, mail_time):   # 入参：[时间，退回的邮箱， 出错信息， 建议]
        self._lock.acquire()
        try:
            curr_mail = recgn_result['Mail']
            for each_entry in self._ndr_data:
                if each_entry['Mail'] == curr_mail:
                    return    # 防止重复添加
            if not self._thread_db_is_a_new_ndr(curr_mail, mail_time):   # 判断且保存最新值
                return         # 如果是一封以前已经处理过的NDR就不用再处理了

            self._unread_data_num += 1
            ndr_data = deepcopy(recgn_result)
            ndr_data['Date'] = mail_time
            self._ndr_data.append(ndr_data)
            self._thread_db_del_success_sent([curr_mail])     # 实时从DB中删除已发送成功的
            self._write_err_info(u"接收到邮箱{}的退信".format(curr_mail), True)
        finally:
            self._lock.release()

    def _set_has_finish_a_loop(self, status=True):
        self._lock.acquire()
        self._has_finish_a_loop = status
        self._lock.release()

    def _get_is_user_paused(self):
        self._lock.acquire()
        ret = self._user_pause
        self._lock.release()
        return ret

    def _account_last_time_save(self, username, dt):
        # 和原有的最新时间比较，保存最新的邮件的时间，以便下次发送的时间从该时间开始
        if username not in self._accounts_last_time:
            self._accounts_last_time[username] = dt
        else:
            old_dt = self._accounts_last_time[username]
            if dt > old_dt:
                self._accounts_last_time[username] = dt

    def _account_last_time_get(self, username, since_time=None):
        # 获取当前账号的已分析邮件的最新时间，如果该账户不存在则返回since_time
        if username in self._accounts_last_time:
            return self._accounts_last_time[username]
        else:
            return since_time

    def _test_pause_and_sleep(self, sleep_seconds):
        ret = False
        if self._get_is_user_paused():
            ret = True
        else:
            self._write_err_info(u"完成一轮接收,等待{}秒后继续...".format(sleep_seconds))
            for i in range(sleep_seconds):
                time.sleep(1)
                if self._get_is_user_paused():
                    ret = True
                    break
        return ret


class NdrUnitTest:

    def __init__(self):
        pass

    @staticmethod
    def test_recv_imap():
        m = RecvImap("mail.hust.edu.cn", "dian@hust.edu.cn", "diangroup1")
        err, err_info = m.login()
        if err != ERROR_SUCCESS:
            print(err_info)
            return
        since_time = datetime.datetime(2016, 8, 14, 19, 38, 02)
        # for recv_time, body in m.search_from_since("1026815245@qq.com", since_time):
        for msg in m.search_from_since("postmaster@hust.edu.cn", since_time):
            print("\n\n\n--------------------------{}--------------------------------".format(msg['Date']))
            print(msg['Body'])

    @staticmethod
    def test_recv_imap2():
        from main import MailDB
        user = "dian@hust.edu.cn"
        m = RecvImap("mail.hust.edu.cn", user, "diangroup1")
        err, err_info = m.login()
        if err != ERROR_SUCCESS:
            print(err_info)
            return
        since_time = datetime.datetime(2016, 8, 14, 19, 38, 02)
        mail_db = MailDB(ur'E:\X 发行资料\sendmail_test.db')
        ndr_cfg_proc = NdrCfgProc(mail_db)
        ndr_cfg = ndr_cfg_proc.get_ndr_cfg_by_user(user)
        fail_content = NdrContent(ndr_cfg)
        for msg in m.search_from_since(ndr_cfg.get_sys_email(), since_time):
            print("\n--------------------------{}--------------------------------".format(msg['Date']))
            print(fail_content.recognize(msg))
        m.logout()

    @staticmethod
    def test_recv_imap3():  # gmail测试
        print("Test recv gmail imap")
        m = RecvImap("imap.gmail.com", "diannewletter@gmail.com", "diangroup")
        err, err_info = m.login()
        if err != ERROR_SUCCESS:
            print(err_info)
            return
        since_time = datetime.datetime(2016, 8, 14, 19, 38, 02)
        for msg in m.search_from_since("mailer-daemon@googlemail.com", since_time):
            print("\n\n\n--------------------------{}--------------------------------".format(msg['Date']))
            print(msg['Body'])

    @staticmethod
    def test_ndr_proc():
        from main import MailDB
        print("Test ndr proc start.")
        chdir_myself()
        db = MailDB(r'send_mail.db')
        db.init()
        success_list = [u'fa@fhj99.com', u"hahha@163.com", u"wangzhaoyang@chinaacc.c",
                        u"abcdefg@qq.com", u"hello_world@qqqc.com", u"uuasddpoa@163.com"]
        db.del_all_success_sent()
        db.clear_tmp_and_dynamic()
        # db.save_sent_progress(100, 20, 30)
        db.add_success_sent(success_list)

        account2 = Account("diannewletter@gmail.com", "diangroup", "smtp.gmail.com", u"李嘉成")
        account6 = Account("dian@hust.edu.cn", "diangroup1", "mail.hust.edu.cn", u"李世明")
        account_list = [account2, account6]

        ndr = NdrProc(account_list, db)
        ndr.event_start_send(datetime.datetime(2013, 8, 14, 18, 00, 02))
        time.sleep(5)

        ndr.start_thread()

        print("")
        old_get_data = None
        for i in range(90):
            get_data = ndr.get_data()
            if get_data[1:] != old_get_data:
                old_get_data = get_data[1:]
                err_info, ndr_data_list, ndr_all_count, has_finish_a_loop = get_data
                # print(u"Error Info: {}".format(err_info))
                print(u"\n"+u"<"*64)
                print(u"Count: {}\t\tHas Finish a loop: {}".format(ndr_all_count, has_finish_a_loop))
                print(u"Data: ")
                print(ndr_data_list)
                print(u"\n"+u">"*64)
            time.sleep(2)

        ndr.stop_proc()
        print(u"已发送成功的变为：")
        print(db.get_success_sent())
        db.close()


if __name__ == '__main__':
    NdrUnitTest.test_ndr_proc()
