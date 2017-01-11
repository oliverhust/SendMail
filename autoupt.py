#!/usr/bin/python
# -*- coding: utf-8 -*-

# 在所有程序启动之前执行，所有东西要单独操作(数据库，日志)

# 尽可能导入尽可能多的库，但不要太大的
import asynchat
import glob


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
    pass


# 数据库的虚接口，需要外部实现
# 注意：数据库的升级由新程序自行实现
class AuptDB:

    def __init__(self):
        pass

    def set_software_version(self, version):   # str
        pass

    def get_software_version(self):   # str
        pass

    def set_last_check_update(self, dt):    # datetime()精确到天
        pass

    def get_last_check_update(self):     # 返回datetime()精确到天
        pass

    def set_check_update_interval(self, interval):   # 单位：天
        pass

    def get_check_update_interval(self):     # 单位：天
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
            f_down = urllib2.urlopen(self._url_version)
        except Exception, e:
            raise AuptErr(u"下载版本信息失败: {}".format(e))

        str_down = f_down.read()
        ver = re.findall(match_regex, str_down)
        if not ver:
            raise AuptErr(u"找不到版本号信息: {}".format(repr(str_down[:512])))

        return ver[0]

    def fetch_pkg(self):
        if ".zip" not in self._url_pkg:
            raise AuptErr(u"安装包不是压缩文件格式")

        print_t(u"开始下载")
        try:
            f_down = urllib2.urlopen(self._url_pkg)
        except Exception, e:
            raise AuptErr(u"下载安装包失败: {}".format(e))
        print_t(u"下载安装包完成")

        r = f_down.read()
        print_t(u"读取完毕")

        return io.BytesIO(r)


class AuptPkg:

    def __init__(self, url_version, url_pkg, db):
        self.__download = AuptDownload(url_version, url_pkg)

    def get_pkg(self):
        # 暂时没写 ??????????????????????????????????????????????????
        return self.__download.fetch_pkg()


class AuptMake:

    _NEW_MAKE_DIR = u'Aupt'

    def __init__(self, pkg_bytes_io, exec_py='AutoUpdateMain', exec_func='run'):
        self._PkgBytesIO = pkg_bytes_io
        self._ExecPy = exec_py
        self._ExecFunc = exec_func
        self.__new_dir = None

    def make(self):
        self._mkdir_new_dir()
        self._make_etc_py()
        self._extract()

    def run(self):
        exec('from {} import {}'.format(self.module(), self._ExecPy))
        print_t(u"脚本导入完成")
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
            raise AuptErr(u"创建文件{}失败".format(full_path))

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


def print_t_init():
    global RUN_START_TIME
    RUN_START_TIME = time.time()


def print_t(log):
    # time_str = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    time_str = time.time() - RUN_START_TIME
    content = u"[%7.3f] %s" % (time_str, log)
    print(content)


def test():
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
    m = AuptMake(fetch_pkg)
    m.make()
    print_t(u"环境准备完成")
    m.run()
    print_t(u"脚本结束")


if __name__ == '__main__':
    test()
