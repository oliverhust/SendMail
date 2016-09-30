#!/usr/bin/python
# -*- coding: utf-8 -*-

import re


class FileRW:

    def __init__(self, file_path):
        self._path = file_path

    def read(self):
        f = open(self._path)
        content = f.read()
        f.close()
        return content

    def write(self, new_content, new_file_path=None):
        if new_file_path is None:
            new_path = self._path
        else:
            new_path = new_file_path
        f = open(new_path, "w")
        f.write(new_content)
        f.close()


class ContentProc:
    # 一个段如果匹配这个列表中的任何一个都不进行处理
    NO_PROC_PATTERNS = [r'(\s+-{3,})+[ \t]*\n',
                        r'\+-+\+',
                        r'\.{10}',
                        r' {10,}']

    def __init__(self, origin_txt=""):
        self._origin_txt = origin_txt

    def run(self):
        seg_list = self._origin_txt.split('\n\n')
        for i, each_seg in enumerate(seg_list):
            seg_list[i] = self._seg_proc(each_seg)
        new_content = '\n\n'.join(seg_list)
        return new_content

    @staticmethod
    def _is_need_proc(origin_seg):
        ret = True
        for each_patt in ContentProc.NO_PROC_PATTERNS:
            if re.search(each_patt, origin_seg) is not None:
                ret = False
        return ret

    def _seg_proc(self, origin_seg):
        if not self._is_need_proc(origin_seg):
            return origin_seg
        new_seg = re.subn(r'(?m)(?<=.)\n[ \t]+', ' ', origin_seg)[0]
        return new_seg


def ui():
    print("A tool convert multi-line-string to single-line-string in rfcXXXX")
    old_file = raw_input("Input the rfc txt file path: \n")
    new_file = raw_input("Input output file path(Enter means replace old file): \n")
    if len(new_file) == 0:
        new_file = old_file
    return old_file, new_file



def main():
    # old_file = r'E:\SystemDirectory\Desktop\tmp.txt'
    # new_file = r'E:\SystemDirectory\Desktop\tmp_new.txt'
    old_file, new_file = ui()

    f = FileRW(old_file)
    origin_content = f.read()

    p = ContentProc(origin_content)
    new_content = p.run()
    f.write(new_content, new_file)


if __name__ == '__main__':
    main()