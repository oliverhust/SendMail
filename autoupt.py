#!/usr/bin/python
# -*- coding: utf-8 -*-

# 在所有程序启动之前执行，所有东西要单独操作(数据库，日志)

# 在aupt_import尽可能导入尽可能多的库，但不要太大的
import aupt_import

import re
import io
import os
import sys
import urllib2
import zipfile
import shutil
import time
import datetime


RUN_START_TIME = None


class AuptErr(Exception):

    def __init__(self, err_message):
        if type(err_message) == unicode:
            Exception.__init__(self, err_message.encode(sys.stdout.encoding))
        else:
            Exception.__init__(self, err_message)


# 数据库的虚接口，需要外部实现
# 注意：数据库的升级由新程序自行实现
class _AuptDB:

    def __init__(self):
        pass

    def init(self):
        pass

    def close(self):
        pass

    def set_software_version(self, version):   # str
        pass

    def get_software_version(self):   # str  如果没有保存则返回软件当前版本
        pass

    def set_last_check_update(self, dt):    # datetime()精确到天
        pass

    def get_last_check_update(self):     # 返回datetime()精确到天
        pass

    def set_dist_pkg(self, pkg_str):   # str类型
        pass

    def get_dist_pkg(self):   # str类型
        pass


class AuptDownload:

    def __init__(self, url_version, url_pkg):
        self._url_version = url_version
        self._url_pkg = url_pkg

    def fetch_version(self, match_regex=r'\d+(?:\.\d+)+'):
        try:
            f_down = urllib2.urlopen(self._url_version, timeout=1)
        except Exception, e:
            raise AuptErr(u"下载版本信息失败: {}".format(e))

        print_t(u"版本号地址已建立连接")
        str_down = f_down.read()
        ver = re.findall(match_regex, str_down)
        if not ver:
            raise AuptErr(u"找不到版本号信息: {}".format(repr(str_down[:512])))

        print_t(u"获得版本号 {}".format(ver[0]))

        return ver[0]

    def fetch_pkg(self):
        if ".zip" not in self._url_pkg:
            raise AuptErr(u"安装包不是压缩文件格式")

        print_t(u"开始下载")
        try:
            f_down = urllib2.urlopen(self._url_pkg, timeout=1)
        except Exception, e:
            raise AuptErr(u"下载安装包失败: {}".format(e))
        print_t(u"安装包下载连接完成")

        r = f_down.read()
        print_t(u"读取完毕")

        return io.BytesIO(r)


class AuptMake:

    _NEW_MAKE_DIR = u'AuptRunNewDir'

    def __init__(self, exec_py_name='AutoUpdateMain', exec_func='run'):
        self._ExecPy = exec_py_name
        self._ExecFunc = exec_func
        self._PkgBytesIO = None
        self.__new_dir = None

    def make_ext_version(self, new_pkg_bytes_io):
        self._PkgBytesIO = new_pkg_bytes_io
        self._mkdir_new_dir()
        self._make_etc_py()
        self._extract()

    def run_ext_version(self):
        exec('from {} import {}'.format(self.module(), self._ExecPy))
        print_t(u"脚本导入完成")
        exec('{}.{}()'.format(self._ExecPy, self._ExecFunc))

    def run_base_version(self):
        exec ('import {}'.format(self._ExecPy))
        print_t(u"导入旧版本程序完成")
        exec('{}.{}()'.format(self._ExecPy, self._ExecFunc))

    @staticmethod
    def module():
        return AuptMake._NEW_MAKE_DIR

    def _make_etc_py(self):
        init_content = "#!/usr/bin/python\n# -*- coding: utf-8 -*-\n"
        self._new_file('__init__.py', init_content)

    def _extract(self):
        z = zipfile.ZipFile(self._PkgBytesIO)
        try:
            z.extractall(self.__new_dir)
        except Exception, e:
            raise AuptErr(u"解压源码包失败: {}".format(e))

    def _mkdir_new_dir(self):
        run_path = AuptMake._get_run_path()
        mkdir_path = os.path.join(run_path, AuptMake._NEW_MAKE_DIR)
        if os.path.exists(mkdir_path):
            if os.path.isdir(mkdir_path):
                shutil.rmtree(mkdir_path)
            else:
                raise AuptErr(u"存在同名文件: {}".format(mkdir_path))

        try:
            os.mkdir(mkdir_path)
        except Exception, e:
            raise AuptErr(u"没有权限新建目录: {}".format(e))
        self.__new_dir = mkdir_path

    def _new_file(self, file_name, file_content):
        full_path = os.path.join(self.__new_dir, unicode(file_name))
        try:
            f = open(full_path, 'w')
        except Exception, e:
            raise AuptErr(u"创建文件{}失败: {}".format(full_path, e))

        f.write(file_content)
        f.close()

    @staticmethod
    def _get_run_path():
        run_path = ''
        if len(sys.path) == 1:
            run_path = sys.path[0]
        else:
            for each_path in sys.path:
                if '/var' in each_path or 'temp' in each_path.lower():
                    run_path = each_path
                    break
        if not run_path:
            return u'.'
            # raise AuptErr(u"不能识别的运行环境: {}".format(sys.path))

        return AuptMake._try_decode(run_path)

    @staticmethod
    def _try_decode(str_to_decode):
        charset_all = ['utf-8', 'gb18030']

        ret = None
        for each_charset in charset_all:
            try:
                ret = str_to_decode.decode(each_charset)
            except:
                pass
            else:
                break

        if type(ret) != unicode:
            raise AuptErr(u"无法解码的路径名: {}".format(repr(str_to_decode)))
        return ret


class AuptExec:

    TYPE_INVALID = 0
    TYPE_BASE = 1
    TYPE_DB = 2
    TYPE_DOWNLOAD = 3

    def __init__(self, db, run_py, run_func):
        self.__db = db
        self.__make = AuptMake(run_py, run_func)
        self.__download_pkg_io = None
        self.__run_type = self.TYPE_INVALID

    def update_pkg_in_db(self, version, pkg_io):
        if pkg_io:
            self.__download_pkg_io = pkg_io
            pkg_io.seek(0)
            pkg_str = pkg_io.read()
            self.__db.set_dist_pkg(pkg_str)
            self.__db.set_software_version(version)

    def run_prepare(self):
        if self.__download_pkg_io:
            self.__run_type = self.TYPE_DOWNLOAD
            self.__make.make_ext_version(self.__download_pkg_io)
        else:
            pkg_str = self.__db.get_dist_pkg()
            if not pkg_str:
                self.__run_type = self.TYPE_BASE
                return

            self.__run_type = self.TYPE_DB
            pkg_io = io.BytesIO(pkg_str)
            self.__make.make_ext_version(pkg_io)

    # 根据有无新旧版本/base版本来运行
    def run(self):
        if self.__run_type == self.TYPE_INVALID or self.__run_type == self.TYPE_BASE:
            self.run_base_version()
        else:
            self.__make.run_ext_version()

    def run_base_version(self):
        self.__make.run_base_version()


class AuptMain:

    CHECK_INTERVAL_DAY = 7

    def __init__(self, db, url_version, url_pkg, run_py, run_func):
        self._db = db
        self._down = AuptDownload(url_version, url_pkg)
        self._exec = AuptExec(db, run_py, run_func)
        print_t_init()

    def run(self):
        try:
            self._db.init()
            self._prepare()
            self._exec.run_prepare()
        except Exception as e:
            self._db.close()
            print(u"发生异常，运行老版本: {}".format(e))
            self._exec.run_base_version()
        else:
            self._db.close()
            self._exec.run()

    def _prepare(self):
        if self._is_need_check():
            self._check_update()
        else:
            print(u"无需检查新版本")

    def _is_need_check(self):
        dt_last_check = self._db.get_last_check_update()
        if not dt_last_check:
            return True

        dt_diff = datetime.datetime.now() - dt_last_check
        if dt_diff.days > self.CHECK_INTERVAL_DAY:
            return True

        return False

    def _check_update(self):
        try:
            fetch_version = self._down.fetch_version()
        except AuptErr as e:
            print(e)
            return False

        # 获取最新版本信息成功
        old_version = self._db.get_software_version()
        if self._version_cmp(fetch_version, old_version) <= 0:
            self._db.set_software_version(old_version)
            self._db.set_last_check_update(datetime.datetime.now())
            print(u"没有更新的版本，新({}) 旧({})".format(fetch_version, old_version))
            return False

        # 有新版本，下载新版本
        try:
            pkg_io = self._down.fetch_pkg()
        except AuptErr as e:
            print(e)
            return False

        self._exec.update_pkg_in_db(fetch_version, pkg_io)
        self._db.set_last_check_update(datetime.datetime.now())
        return True

    @staticmethod
    def _version_cmp(version1, version2):
        if not version1:
            return 1
        if not version2:
            return -1

        num1_list = version1.split('.')
        num2_list = version2.split('.')
        count = max(len(num1_list), len(num2_list))

        for i in xrange(count):
            if i >= len(num1_list):
                return -1
            if i >= len(num2_list):
                return 1

            if num1_list[i] > num2_list[i]:
                return 1
            elif num1_list[i] < num2_list[i]:
                return -1

        return 0


def print_t_init():
    global RUN_START_TIME
    RUN_START_TIME = time.time()


def print_t(log):
    # time_str = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    time_str = time.time() - RUN_START_TIME
    content = u"[%7.3f] %s" % (time_str, unicode(log))
    print(content)


def test():
    import Run_GUI
    print_t_init()
    print_t(u"开始运行程序")

    # url_ver = r'https://coding.net/u/mmyzoliver/p/SendMail/git/raw/master/README.md'
    url_ver = r'http://git.oschina.net/mmyz/SendMail/raw/master/README.md'

    # url_pkg = r'http://bjbgp01.baidupcs.com/file/413c6bd77f9a3e12b80391f15db50e71?bkt=p3-1400413c6bd77f9a3e12b80391f15db50e71d2b5c673000000024cc6&fid=4044588379-250528-73886866994231&time=1484098660&sign=FDTAXGERLBH-DCb740ccc5511e5e8fedcff06b081203-umeyMVcYEJWBh2PMrjUvXQXr%2Frc%3D&to=hbjbgp&fm=Yan,B,G,e&sta_dx=150726&sta_cs=2&sta_ft=zip&sta_ct=0&sta_mt=0&fm2=Yangquan,B,G,e&newver=1&newfm=1&secfm=1&flow_ver=3&pkey=1400413c6bd77f9a3e12b80391f15db50e71d2b5c673000000024cc6&sl=81723466&expires=8h&rt=sh&r=498045650&mlogid=241232226608971775&vuk=4044588379&vbdid=678661293&fin=version.zip&fn=version.zip&slt=pm&uta=0&rtype=1&iv=0&isw=0&dp-logid=241232226608971775&dp-callid=0.1.1&csl=1024&csign=PjPitPnInxBSER%2BVYL52%2BGi4z5w%3D'
    # url_pkg = r'https://github.com/oliverhust/SendMail/raw/master/version/version.zip'
    url_pkg = r'http://git.oschina.net/mmyz/SendMail/raw/master/version.zip'

    pkg = AuptDownload(url_ver, url_pkg)

    fetch_ver = pkg.fetch_version()
    print_t(u"获得版本号 {}".format(fetch_ver))

    fetch_pkg = pkg.fetch_pkg()
    print_t(u"获取安装包完成")
    m = AuptMake()
    m.make_ext_version(fetch_pkg)
    print_t(u"环境准备完成")
    m.run_base_version()
    m.run_ext_version()
    print_t(u"脚本结束")


if __name__ == '__main__':
    test()
