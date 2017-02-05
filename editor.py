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
    def copy(src_file):
        # 返回文件路径, 文件不存在则IOError异常
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
        self.Button_FontColor.clicked.connect(self.__slot_set_font_color)
        self.Button_BackColor.clicked.connect(self.__slot_set_back_color)
        self.Button_SetUp.clicked.connect(self.__slot_set_word_up)
        self.Button_SetDown.clicked.connect(self.__slot_set_word_down)
        self.Button_AddLink.clicked.connect(self.__slot_add_hyperlink)
        self.Button_AddTable.clicked.connect(self.__slot_add_table)
        self.Button_AddList.clicked.connect(self.__slot_add_list)
        self.Button_AddList2.clicked.connect(self.__slot_add_list2)

        # 对齐方式
        menu_align = QMenu()
        action_align_mid = menu_align.addAction(QString(u"居中"))
        action_align_mid.triggered.connect(self.__slot_set_alignment_mid)
        action_align_left = menu_align.addAction(QString(u"左对齐"))
        action_align_left.triggered.connect(self.__slot_set_alignment_left)
        action_align_right = menu_align.addAction(QString(u"右对齐"))
        action_align_right.triggered.connect(self.__slot_set_alignment_right)
        self.Button_Align.setMenu(menu_align)

        # 插入超文本
        self.textEdit.canInsertFromMimeData = self.__can_insert_mine_data
        self.textEdit.insertFromMimeData = self.__insert_from_mine_data

        self.textEdit.setFontPointSize(self._INIT_FONT_SIZE)

    def set_html(self, html_str):
        self.textEdit.setHtml(QString(html_str))

    def to_html(self):
        return self.textEdit.toHtml()

    # -----------------------------------------------------------------------------------------
    # 当光标的charFormat改变时工具按钮的状态对应改变

    def __set_edit_tools_status(self, char_fmt):
        set_font = QFont(char_fmt.font())

        self._is_program_signal = True
        try:
            self.Button_B.setChecked(set_font.bold())
            self.Button_I.setChecked(set_font.italic())
            self.Button_U.setChecked(set_font.underline())
            self.fontBox.setCurrentFont(set_font)
            self.fontSizeBox.setValue(set_font.pointSize())
            self.Button_SetUp.setChecked(char_fmt.verticalAlignment() == QTextCharFormat.AlignSuperScript)
            self.Button_SetDown.setChecked(char_fmt.verticalAlignment() == QTextCharFormat.AlignSubScript)
        finally:
            self._is_program_signal = False

    def __slot_curr_pos_fmt_changed(self, *args, **kwargs):
        # 当前光标的字体发生变化(如移动光标)
        # print(u"Curr_pos_fmt_changed, set tool status")
        set_cursor = QTextCursor(self.textEdit.textCursor())

        # # 当前字体有选择文本时工具状态保持为字体发生变化时刻 已选择部分第一个字的字体
        # if set_cursor.hasSelection():
        #    set_position = min(set_cursor.position(), set_cursor.anchor()) + 1
        #    set_cursor.setPosition(set_position)

        self.__set_edit_tools_status(set_cursor.charFormat())

    # -----------------------------------------------------------------------------------------
    # 粗体/斜体/下划线/字体及大小 设置

    @_ignore_program_signal
    def __slot_bold_press(self, *args, **kwargs):
        # print(u"User pressed bold: {}".format(self.Button_B.isChecked()))
        fmt = QTextCharFormat()
        if self.Button_B.isChecked():
            fmt.setFontWeight(QFont.Bold)
        else:
            fmt.setFontWeight(QFont.Normal)
        self.__merge_format(fmt)

    @_ignore_program_signal
    def __slot_italic_press(self, *args, **kwargs):
        # print(u"User pressed italic: {}".format(self.Button_I.isChecked()))
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.Button_I.isChecked())
        self.__merge_format(fmt)

    @_ignore_program_signal
    def __slot_underline_press(self, *args, **kwargs):
        # print(u"User pressed underline: {}".format(self.Button_U.isChecked()))
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.Button_U.isChecked())
        self.__merge_format(fmt)

    @_ignore_program_signal
    def __slot_font_box_changed(self, *args, **kwargs):
        # print(u"User font Box changed, set as new font")
        fmt = QTextCharFormat()
        user_set_font = self.fontBox.currentFont()
        fmt.setFont(user_set_font)
        self.__merge_format(fmt)

    @_ignore_program_signal
    def __slot_font_size_changed(self, *args, **kwargs):
        # print(u"User font size changed to {}, set as new size".format(self.fontSizeBox.value()))
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
        suffix = "Image files(*.jpg;*.jpeg;*.png;*.bmp;*.gif;*.tiff;*.pbm;*.pgm;*.ppm;*.xbm;*.xpm)"
        s_list = QFileDialog.getOpenFileNames(self, QString(u"插入图片(可多选)"), "/", suffix)
        s_list = [unicode(y) for y in s_list if y]

        for src in s_list:
            self._insert_qimage(QImage(src))
            # self.textEdit.textCursor().insertImage(QImage(src))

    def __can_insert_mine_data(self, source):
        if source.hasImage():
            return True
        else:
            return QTextEdit.canInsertFromMimeData(self.textEdit, source)

    def __insert_from_mine_data(self, source):
        if source.hasImage():
            # 插入图片：复制一份到临时目录，然后用html插入
            self._insert_qimage(QImage(source.imageData()))
        elif source.hasHtml():
            # 插入超文本：替换里面所有的图片路径
            self._insert_html(source.html())
        elif source.hasText():
            # 可能存在同时hasHtml和hasText
            curr_cursor = self.textEdit.textCursor()
            curr_cursor.insertText(source.text())

    def _insert_qimage(self, qimage):
        # 插入图片：复制一份到临时目录，然后用html插入
        curr_cursor = self.textEdit.textCursor()
        new_file = TmpFile.qimage2tmp(qimage)
        curr_cursor.insertImage(qimage, new_file)
        # html_img = r'<img src="{}" />'.format(html_escape(new_file))
        # curr_cursor.insertHtml(html_img)

    def _insert_html(self, html_text):
        # 插入超文本：替换里面所有的图片路径
        curr_cursor = self.textEdit.textCursor()
        html_img = HtmlImg(unicode(html_text))
        html_img.correct_img_src()

        img_src = html_img.get_img_src()
        try:
            for i in range(len(img_src)):
                img_src[i] = TmpFile.copy(img_src[i])
        except IOError:
            return
        html_img.replace_img_src(img_src)

        modify_html = html_img.html()
        curr_cursor.insertHtml(modify_html)

    # -----------------------------------------------------------------------------------------
    # 段落对齐方式
    def __slot_set_alignment_mid(self):
        self.textEdit.setAlignment(Qt.AlignCenter | Qt.AlignAbsolute)

    def __slot_set_alignment_left(self):
        self.textEdit.setAlignment(Qt.AlignLeft | Qt.AlignAbsolute)

    def __slot_set_alignment_right(self):
        self.textEdit.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

    # -----------------------------------------------------------------------------------------
    # 颜色设置
    @_ignore_program_signal
    def __slot_set_font_color(self, *args, **kwargs):
        q_color = QColorDialog.getColor(Qt.black)
        if not q_color.isValid():
            return

        fmt = QTextCharFormat()
        brush = QBrush(q_color)
        fmt.setForeground(brush)
        self.__merge_format(fmt)

    @_ignore_program_signal
    def __slot_set_back_color(self, *args, **kwargs):
        q_color = QColorDialog.getColor(Qt.white)
        if not q_color.isValid():
            return

        fmt = QTextCharFormat()
        brush = QBrush(q_color)
        fmt.setBackground(brush)
        self.__merge_format(fmt)

    # -----------------------------------------------------------------------------------------
    # 上下标设置
    @_ignore_program_signal
    def __slot_set_word_up(self, *args, **kwargs):
        # 设置下标按钮复原
        self.Button_SetDown.setChecked(False)

        fmt = QTextCharFormat()
        if self.Button_SetUp.isChecked():
            fmt.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.AlignNormal)
        self.__merge_format(fmt)

    @_ignore_program_signal
    def __slot_set_word_down(self, *args, **kwargs):
        # 设置上标按钮复原
        self.Button_SetUp.setChecked(False)

        fmt = QTextCharFormat()
        if self.Button_SetDown.isChecked():
            fmt.setVerticalAlignment(QTextCharFormat.AlignSubScript)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.AlignNormal)
        self.__merge_format(fmt)

    # -----------------------------------------------------------------------------------------
    # 插入列表，列表2，超级链接，表格
    def __slot_add_list(self):
        curr_cursor = self.textEdit.textCursor()
        curr_cursor.insertList(QTextListFormat.ListDisc)

    def __slot_add_list2(self):
        curr_cursor = self.textEdit.textCursor()
        curr_cursor.insertList(QTextListFormat.ListDecimal)

    def __slot_add_hyperlink(self):
        pass

    def __slot_add_table(self):
        pass



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

