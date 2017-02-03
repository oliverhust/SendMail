#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
import shutil
import random
from copy import deepcopy
import tempfile

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_editor import Ui_Dialog_Editor
from etc_func import html_escape, random_str


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

class TmpFile:

    _TMPDIR = None

    def __init__(self):
        pass

    @staticmethod
    def init():
        TmpFile._TMPDIR = tempfile.mkdtemp()

    @staticmethod
    def fini():
        if TmpFile._TMPDIR:
            shutil.rmtree(TmpFile._TMPDIR, ignore_errors=True)
            TmpFile._TMPDIR = None

    @staticmethod
    def qimage2tmp(qimage):
        file_path = TmpFile.rand_file_path()
        qimage.save(QString(file_path), u'jpg')
        return file_path

    @staticmethod
    def qvariant2tmp(qvariant):
        # 返回文件路径
        bin_content = str(qvariant.toByteArray())

        dst_file = TmpFile.rand_file_path(file_content=bin_content)
        return dst_file

    @staticmethod
    def copy(src_file):
        # 返回文件路径, 文件不存在则IOError
        dst_file = TmpFile.rand_file_path()

        shutil.copy(src_file, dst_file)
        return dst_file

    @staticmethod
    def rand_file_path(dirname=None, filename_len=16, file_content=None):
        # 返回一个随机文件名(带路径)，但默认不会创建文件。如果带file_content才会创建
        if not dirname:
            dir_self = TmpFile._TMPDIR
        else:
            dir_self = dirname

        file_name = random_str(filename_len)
        file_path = os.path.join(dir_self, file_name)

        if not file_content or not isinstance(file_content, str):
            return file_path

        f = open(file_path, 'wb')
        try:
            f.write(file_content)
        finally:
            f.close()

        return file_path

    @staticmethod
    def get_dir():
        return TmpFile._TMPDIR


# 装饰器：当信号来自程序设置产生时不处理
def _ignore_program_signal(func):
    def final_func(self, *args, **kwargs):
        ret = None
        if not self._is_program_signal:
            ret = func(self, *args, **kwargs)
            self.textEdit.setFocus()
        return ret
    return final_func


# 写完该类后把Ui_Dialog_Editor去掉
class BasicEditor(Ui_Dialog_Editor):

    _INIT_FONT_SIZE = 16

    # html img r'''<img\b[^<>]*?\bsrc\s*=\s*['"]?\s*([^'"<>]*)[^<>]*?/?\s*>'''
    __re_html_img = re.compile(ur'''(<img\b[^<>]*?\bsrc\s*=\s*['"]?\s*)file:///([^'"<>]*)([^<>]*?/?\s*>)''')

    def __init__(self):
        super(BasicEditor, self).__init__()
        self._is_program_signal = False

    def setup_basic_editor(self):
        self._is_program_signal = False

        self.textEdit.currentCharFormatChanged.connect(self.__slot_curr_pos_fmt_changed)
        self.Button_B.clicked.connect(self.__slot_bold_press)
        self.Button_I.clicked.connect(self.__slot_italic_press)
        self.Button_U.clicked.connect(self.__slot_underline_press)
        self.fontBox.activated.connect(self.__slot_font_box_changed)
        self.fontSizeBox.valueChanged.connect(self.__slot_font_size_changed)
        self.Button_AddPic.clicked.connect(self.__slot_insert_picture)

        self.textEdit.canInsertFromMimeData = self.__can_insert_mine_data
        self.textEdit.insertFromMimeData = self.__insert_from_mine_data

        self.textEdit.setFontPointSize(self._INIT_FONT_SIZE)

    def set_html(self, html_str):
        self.textEdit.setHtml(QString(html_str))

    def to_html(self):
        return self.textEdit.toHtml()

    def __set_edit_tools_status(self, text_char_fmt):
        set_font = QFont(text_char_fmt.font())

        self._is_program_signal = True
        try:
            self.Button_B.setChecked(set_font.bold())
            self.Button_I.setChecked(set_font.italic())
            self.Button_U.setChecked(set_font.underline())
            self.fontBox.setCurrentFont(set_font)
            self.fontSizeBox.setValue(set_font.pointSize())
        finally:
            self._is_program_signal = False

    def __slot_curr_pos_fmt_changed(self, *args, **kwargs):
        # 当前光标的字体发生变化(如移动光标)
        print(u"Curr_pos_fmt_changed, set tool status")
        set_cursor = QTextCursor(self.textEdit.textCursor())

        # # 当前字体有选择文本时工具状态保持为字体发生变化时刻 已选择部分第一个字的字体
        # if set_cursor.hasSelection():
        #    set_position = min(set_cursor.position(), set_cursor.anchor()) + 1
        #    set_cursor.setPosition(set_position)

        self.__set_edit_tools_status(set_cursor.charFormat())

    @_ignore_program_signal
    def __slot_bold_press(self, *args, **kwargs):
        print(u"User pressed bold: {}".format(self.Button_B.isChecked()))
        fmt = QTextCharFormat()
        if self.Button_B.isChecked():
            fmt.setFontWeight(QFont.Bold)
        else:
            fmt.setFontWeight(QFont.Normal)
        self.__merge_format(fmt)

    @_ignore_program_signal
    def __slot_italic_press(self, *args, **kwargs):
        print(u"User pressed italic: {}".format(self.Button_I.isChecked()))
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.Button_I.isChecked())
        self.__merge_format(fmt)

    @_ignore_program_signal
    def __slot_underline_press(self, *args, **kwargs):
        print(u"User pressed underline: {}".format(self.Button_U.isChecked()))
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.Button_U.isChecked())
        self.__merge_format(fmt)

    @_ignore_program_signal
    def __slot_font_box_changed(self, *args, **kwargs):
        print(u"User font Box changed, set as new font")
        fmt = QTextCharFormat()
        user_set_font = self.fontBox.currentFont()
        fmt.setFont(user_set_font)
        self.__merge_format(fmt)

    @_ignore_program_signal
    def __slot_font_size_changed(self, *args, **kwargs):
        print(u"User font size changed to {}, set as new size".format(self.fontSizeBox.value()))
        fmt = QTextCharFormat()
        point_size = self.fontSizeBox.value()
        fmt.setFontPointSize(point_size)
        self.__merge_format(fmt)

    def __merge_format(self, fmt):
        cursor = self.textEdit.textCursor()
        cursor.mergeCharFormat(fmt)
        self.textEdit.mergeCurrentCharFormat(fmt)

    # -----------------------------------------------------------------------------------------
    # 插入图片/html
    def __slot_insert_picture(self):
        img = QImage(r'E:\MyDocuments\Python\SendMail\pic\Emotions\28.gif')
        curr_cursor = self.textEdit.textCursor()
        curr_cursor.insertImage(img)

    def __can_insert_mine_data(self, source):
        if source.hasImage():
            return True
        else:
            return QTextEdit.canInsertFromMimeData(self.textEdit, source)

    def __insert_from_mine_data(self, source):
        curr_cursor = self.textEdit.textCursor()

        if source.hasImage():
            # 插入图片：复制一份到临时目录，然后用html插入
            new_file = TmpFile.qimage2tmp(QImage(source.imageData()))
            html_img = r'<img src="{}" />'.format(html_escape(new_file))
            curr_cursor.insertHtml(html_img)

        elif source.hasHtml():
            # 插入超文本：替换里面所有的图片路径
            html_img = HtmlImg(unicode(source.html()))
            html_img.correct_img_src()
            img_src = html_img.get_img_src()
            for i in range(len(img_src)):
                img_src[i] = TmpFile.copy(img_src[i])
            html_img.replace_img_src(img_src)

            modify_html = html_img.html()
            curr_cursor.insertHtml(modify_html)

        elif source.hasText():
            # 可能存在同时hasHtml和hasText
            curr_cursor.insertText(source.text())

    @staticmethod
    def __html_moidfy(html_string):
        # 将用户复制粘贴的html进行处理
        return BasicEditor.__re_html_img.subn(r'\1\2\3', html_string)[0]


class WinEditor(QMainWindow, BasicEditor, Ui_Dialog_Editor):

    _TAB_INDEX_EDIT = 0
    _TAB_INDEX_HTML = 1

    def __init__(self, parent=None):
        super(WinEditor, self).__init__(parent)
        self._last_html_str = None

        self.setupUi(self)
        self.setup_basic_editor()

        # 切换到html
        self.tabWidget.currentChanged.connect(self._slot_edit_mode_change)

    # 编辑模式变化(超文本编辑/html编辑)
    def _slot_edit_mode_change(self, curr_index):

        if curr_index == self._TAB_INDEX_EDIT:
            html_str = self.PlainTextEdit_Html.toPlainText()
            if html_str != self._last_html_str:
                self.textEdit.setHtml(QString(html_str))
        elif curr_index == self._TAB_INDEX_HTML:
            html_str = QString(self.textEdit.toHtml())
            self._last_html_str = QString(html_str)
            self.PlainTextEdit_Html.setPlainText(html_str)


def init():
    TmpFile.init()


def fini():
    TmpFile.fini()


def main():
    init()
    try:
        QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))
        app = QApplication(sys.argv)
        win = WinEditor()
        win.show()
        app.exec_()
    finally:
        fini()


# ################################## 测试 #########################################

def expect_eq(a, b):
    if a == b:
        print("[     OK     ]")
    else:
        print("[   FAILED   ] " + "@" * 64)
        print("a = {}".format(a))
        print("b = {}".format(b))


def test_html_img():
    html_all = r'''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'SimSun'; font-size:16pt; font-weight:400; font-style:normal;">
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Safasfasfasfasf </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><img src="file:///C:\Users\Oliver\AppData\Local\Temp\msohtmlclip1\01\clip_image001.png" width="511" height="511" /> </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Asf </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Sa </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">F </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Sa<img src="file:///C:\Users\Oliver\AppData\Local\Temp\msohtmlclip1\01\clip_image002.png" width="32" height="32" /> </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Fas </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">asfas </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">sfsa </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">asdfas </p></body></html>
    '''

    ht = HtmlImg(html_all)

    print("\nOrigin imgage src:")
    print(ht.get_img_src())
    expect_eq(ht.get_img_src(), [r'file:///C:\Users\Oliver\AppData\Local\Temp\msohtmlclip1\01\clip_image001.png',
                                 r'file:///C:\Users\Oliver\AppData\Local\Temp\msohtmlclip1\01\clip_image002.png'])

    print("\nCorrect html image:")
    ht.correct_img_src()
    print(ht.get_img_src())
    expect_eq(ht.get_img_src(), [r'C:\Users\Oliver\AppData\Local\Temp\msohtmlclip1\01\clip_image001.png',
                                 r'C:\Users\Oliver\AppData\Local\Temp\msohtmlclip1\01\clip_image002.png'])

    print("\nReplace html test:")
    new_src = [r'C:\dddd\TTTTTYYYYYYYYYYYYY.jpg', r'OKKKKKKKKKKKKKK.png']
    ht.replace_img_src(new_src)
    print(ht.get_img_src())
    expect_eq(ht.get_img_src(), new_src)


if __name__ == '__main__':
    main()
    # test_html_img()

