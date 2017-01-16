#!/usr/bin/python
# -*- coding: utf-8 -*-

# 导入主py却不使用,初始化db,设置和启动Aupt

from autoupt import AuptMain
from main import AuptEnv
import Run_GUI


def run():
    env = AuptEnv()

    url_ver = r'http://git.oschina.net/mmyz/SendMail/raw/master/README.md'
    url_pkg = r'http://git.oschina.net/mmyz/SendMail/raw/master/version.zip'

    # url_ver = r'http://github.com/oliverhust/SendMail/raw/master/README.md'
    # url_pkg = r'http://github.com/oliverhust/SendMail/raw/master/version/version.zip'

    run_py, run_func = 'Run_GUI', 'main'
    aupt = AuptMain(env, url_ver, url_pkg, run_py, run_func)
    aupt.run()


if __name__ == '__main__':
    run()

