#!/usr/bin/python
# -*- coding: utf-8 -*-


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


class AuptErr(Exception):
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
        if os.path.basename(self._url_pkg)[-4:] != ".zip":
            raise AuptErr(u"安装包不是压缩文件格式")

        try:
            f_down = urllib2.urlopen(self._url_pkg)
        except Exception, e:
            raise AuptErr(u"下载安装包失败: {}".format(e))

        return io.BytesIO(f_down.read())


class PkgManager:

    def __init__(self, url_version, url_pkg, db):
        self.__download = AuptDownload(url_version, url_pkg)

    def get_pkg(self):
        # 暂时没写 ??????????????????????????????????????????????????
        return self.__download.fetch_pkg()


class AuptMake:

    _NEW_MAKE_DIR = u'Aupt'

    def __init__(self, pkg_bytes_io):
        self._pkg_bytes_io = pkg_bytes_io
        self._new_dir = None

    def make(self):
        self._mkdir_new_dir()
        self._make_etc_py()
        self._extract()

    @staticmethod
    def module():
        return AuptMake._NEW_MAKE_DIR

    def _make_etc_py(self):
        init_content = "#!/usr/bin/python\n# -*- coding: utf-8 -*-\n"
        self._new_file('__init__.py', init_content)

    def _extract(self):
        z = zipfile.ZipFile(self._pkg_bytes_io)
        try:
            z.extractall(self._new_dir)
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
        self._new_dir = mkdir_path

    def _new_file(self, file_name, file_content):
        full_path = os.path.join(self._new_dir, unicode(file_name))
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


def test():
    pkg = AuptDownload(None, r'https://github.com/oliverhust/SendMail/raw/master/version/version.zip')
    fetch_pkg = pkg.fetch_pkg()
    m = AuptMake(fetch_pkg)
    m.make()
    exec_py = 'AutoUpdateMain'
    exec 'from {} import {}'.format(m.module(), exec_py)
    exec '{}.run()'.format(exec_py)


if __name__ == '__main__':
    test()
