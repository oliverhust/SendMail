#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

size_list = ['16x16', '32x32', '128x123', '256x256', '512x512']

for index, size in enumerate(size_list):
    os.system('convert -resize %s icon_512x512@2x.png icon_%s.png' % (size, size))
    if index > 0:
        os.system('convert -resize %s icon_512x512@2x.png icon_%s@2x.png' % (size, size_list[index - 1]))
