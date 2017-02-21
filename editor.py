#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
from copy import deepcopy

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_editor import Ui_Dialog_Editor
from ui_editor_addlink import Ui_Dialog_AddLink
from ui_editor_addtable import Ui_Dialog_AddTable
from etc_func import html_escape
from cfg_data import TmpFile, HtmlImg, MailResource, MailContent


class WinAddLink(QDialog, Ui_Dialog_AddLink):
    # 插入超级链接窗口

    def __init__(self, parent=None):
        super(WinAddLink, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        self.Button_OK.clicked.connect(self.__slot_button_ok)
        self.Button_Cancel.clicked.connect(self.__slot_button_cancel)

        self._link = u""
        self._text = u""

    def __slot_button_ok(self):
        self._link = unicode(self.lineEdit_Link.text())
        if not self._link:
            QMessageBox.critical(self, u"Input Error", QString(u"请输入链接地址"))
            return

        self._text = unicode(self.lineEdit_Text.text())
        self.accept()

    def __slot_button_cancel(self):
        self.reject()

    def html(self):
        # 用户可能取消
        if not self._link:
            return u''

        # 如果不填则和链接名一致
        h_text = self._text if self._text else self._link
        h = u'<a href="{}" target="_blank">{}</a>'.format(html_escape(self._link),
                                                          html_escape(h_text))
        return h

    def link(self):
        return self._link

    def text(self):
        return self._text


class WinAddTable(QDialog, Ui_Dialog_AddTable):
    # 插入表格窗口   UI已经保证了数据的正确性

    def __init__(self, parent=None):
        super(WinAddTable, self).__init__(parent)
        self._row = None
        self._column = None
        self._align = None
        self._color = None
        self._borderWidth = None
        self._padding = None
        self._spacing = None

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        self.Button_OK.clicked.connect(self.__slot_button_ok)
        self.Button_Cancel.clicked.connect(self.__slot_button_cancel)
        self.Button_Color.clicked.connect(self.__slot_set_color)

        # 设置颜色 按钮
        self.__set_border_color(QColor(Qt.black))

    def table(self):
        fmt = QTextTableFormat()
        fmt.setCellSpacing(self._spacing)
        fmt.setCellPadding(self._padding)
        fmt.setAlignment(self._align)

        fmt.setBorderBrush(QBrush(self._color))
        fmt.setBorder(self._borderWidth / 2.0)
        fmt.setBorderStyle(QTextTableFormat.BorderStyle_Solid)  # 固定

        return self._row, self._column, fmt

    def __slot_button_ok(self):
        self._row = int(self.Box_Row.value())
        self._column = int(self.Box_Column.value())
        self._color = self._color
        self._borderWidth = int(self.Box_BorderWidth.value())
        self._padding = int(self.Box_Padding.value())
        self._spacing = int(self.Box_Space.value())

        if self.radioButton_Right.isChecked():
            self._align = Qt.AlignRight
        elif self.radioButton_Mid.isChecked():
            self._align = Qt.AlignCenter
        else:
            self._align = Qt.AlignLeft

        self.accept()

    def __slot_button_cancel(self):
        self.reject()

    def __slot_set_color(self):
        q_color = QColorDialog.getColor(Qt.black)
        if not q_color.isValid():
            return
        self.__set_border_color(q_color)

    def __set_border_color(self, q_color):
        self._color = q_color
        color_pix = QPixmap(self.Button_Color.width(), self.Button_Color.height())
        color_pix.fill(q_color)
        self.Button_Color.setIcon(QIcon(color_pix))


# 装饰器：当信号来自程序设置产生时不处理
def _ignore_program_signal(func):
    def final_func(self, *args, **kwargs):
        ret = None
        if self._set_by_program <= 0:
            ret = func(self, *args, **kwargs)
            self.textEdit.setFocus()
        else:
            print("Program signal")
        return ret
    return final_func


class BasicEditor(Ui_Dialog_Editor):

    _INIT_FONT_SIZE = 16

    def __init__(self):
        super(BasicEditor, self).__init__()
        self._set_by_program = 0

    def _setup_basic_editor(self):
        self._set_by_program = 0

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
        return unicode(self.textEdit.toHtml())

    def img_src(self):
        html_img = HtmlImg(self.textEdit.toHtml())
        html_img.correct_img_src()
        return html_img.get_img_src()

    # -----------------------------------------------------------------------------------------
    # 当光标的charFormat改变时工具按钮的状态对应改变

    def __set_edit_tools_status(self, char_fmt):
        set_font = QFont(char_fmt.font())

        self._set_by_program += 1
        try:
            self.Button_B.setChecked(set_font.bold())
            self.Button_I.setChecked(set_font.italic())
            self.Button_U.setChecked(set_font.underline())
            self.fontBox.setCurrentFont(set_font)
            self.fontSizeBox.setValue(set_font.pointSize())
            self.Button_SetUp.setChecked(char_fmt.verticalAlignment() == QTextCharFormat.AlignSuperScript)
            self.Button_SetDown.setChecked(char_fmt.verticalAlignment() == QTextCharFormat.AlignSubScript)
        finally:
            self._set_by_program -= 1

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
        # 插入图片：复制一份到临时目录
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
        old_char_fmt = QTextCharFormat(self.textEdit.currentCharFormat())

        new_win = WinAddLink()
        if not new_win.exec_():
            return

        h = new_win.html()
        curr_cursor = self.textEdit.textCursor()
        curr_cursor.insertText(QString(u' '))   # 在链接前插入一个空格
        curr_cursor.insertHtml(h)

        # 恢复原来的格式
        curr_cursor.setCharFormat(old_char_fmt)
        self.textEdit.setCurrentCharFormat(old_char_fmt)
        curr_cursor.insertText(QString(u' '))    # 在链接后插入一个空格
        self.textEdit.setFocus()

    def __slot_add_table(self):
        new_win = WinAddTable()
        if not new_win.exec_():
            return

        row, col, fmt = new_win.table()
        curr_cursor = self.textEdit.textCursor()
        curr_cursor.insertTable(row, col, fmt)


class EmailEditor(QDialog, BasicEditor, Ui_Dialog_Editor):

    _TAB_INDEX_EDIT = 0
    _TAB_INDEX_HTML = 1
    _TAB_INDEX_APPENDIX = 2

    _COL_APPENDIX_NAME = 0
    _COL_APPENDIX_PATH = 3

    _COLOR_WARNING = Qt.yellow
    _COLOR_ERROR = Qt.red

    def __init__(self, parent=None, gui_proc=None, mail_content=None):
        super(EmailEditor, self).__init__(parent)
        self._last_tab_index = EmailEditor._TAB_INDEX_EDIT   # 切换tab事件发生前
        self._last_html_str = None                 # 判断在两次切换tab之间用户是否改变了html
        self.__gui_proc = gui_proc
        self.__window_has_closed = False           # 窗口关闭标志
        self.__mail_content_finally = None      # 窗口关闭时的MailContent

        self.setupUi(self)
        self._setup_basic_editor()
        self.__init_table_appendix()    # 初始化表格

        if mail_content:
            self.recover_ui(mail_content)

        self.tabWidget.currentChanged.connect(self.__slot_edit_mode_change)  # 切换到页面
        self.Button_AddAppend.clicked.connect(self.__slot_add_appendix)
        self.Button_DelAppend.clicked.connect(self.__slot_del_appendix)
        self.table_Appendix.itemChanged.connect(self.__slot_appendix_item_changed)
        self.Button_Appendix.clicked.connect(self.__slot_jump_appendix_tab)

        self.Button_OK.clicked.connect(self.__slot_button_ok)
        self.Button_Cancel.clicked.connect(self.__slot_button_cancel)
        self.Button_Save.clicked.connect(self.__slot_button_save)
        self.closeEvent = self.__slot_win_close         # 窗口关闭事件

    def to_mail_content(self):
        # 如果窗口已经关闭，则返回关闭前的MailContent 返回的MailContent不包含bin_data
        if self.__window_has_closed:
            content = deepcopy(self.__mail_content_finally)
        else:
            sub = unicode(self.Edit_Sub.text())
            body = self.to_html()
            append_resources = self.__all_appendix()
            body_resources = [MailResource(i, i) for i in self.img_src()]
            content = MailContent(sub, body, append_resources, body_resources)

        return content

    def recover_ui(self, mail_content, modify_html=True):
        mail_content.rc_name_mode_edit()
        self.Edit_Sub.setText(QString(mail_content.sub()))
        self._ui_add_appends(mail_content.append_resource_list())
        if modify_html:
            mail_content.rc_data_mode_file()
        self.set_html(mail_content.body())

    def __init_table_appendix(self):
        self.table_Appendix.setColumnCount(4)
        # 设置单元格初始长度
        len_list = [400, 100, 75, 600]
        for i, each_len in enumerate(len_list):
            self.table_Appendix.setColumnWidth(i, each_len)

        headers = [u"附件名(可双击编辑)", u"大小", u"状态", u"路径"]
        tool_tips = [u"对方收到附件时显示的名字，如果附件名后缀名不是1~5个字符则提示是否输错",
                     u"附件大小", u"附件状态", u"附件的绝对路径"]
        for i, header in enumerate(headers):
            table_item = QTableWidgetItem(QString(unicode(header)))
            table_item.setTextColor(Qt.blue)
            if i < len(tool_tips) and tool_tips[i]:
                table_item.setToolTip(QString(tool_tips[i]))
            self.table_Appendix.setHorizontalHeaderItem(i, table_item)

    # 编辑模式变化(超文本编辑/html编辑/附件)
    def __slot_edit_mode_change(self, curr_index):
        last_index = self._last_tab_index
        self._last_tab_index = curr_index
        if curr_index == last_index:
            return

        if last_index == EmailEditor._TAB_INDEX_EDIT:
            html_str = QString(self.textEdit.toHtml())
            self._last_html_str = QString(html_str)
            self.PlainTextEdit_Html.setPlainText(html_str)
        elif last_index == EmailEditor._TAB_INDEX_HTML:
            html_str = self.PlainTextEdit_Html.toPlainText()
            if html_str != self._last_html_str:
                self.textEdit.setHtml(QString(html_str))

    # -----------------------------------------------------------------------------------------
    # 确认/取消/保存
    def __slot_button_ok(self):
        try:
            self.__mail_content_finally = self.to_mail_content()
        finally:
            self.__win_fini()

        self.accept()
        if self.__gui_proc:
            self.__gui_proc.save_mail_content(self.__mail_content_finally)

    def __slot_button_cancel(self, *args, **kwargs):
        self.__slot_win_close()

    def __slot_button_save(self):
        if self.__gui_proc:
            self.__gui_proc.save_mail_content(self.to_mail_content())

    # 窗口关闭事件
    def __slot_win_close(self, *args, **kwargs):
        # 从数据库里面取MailContent
        try:
            if self.__gui_proc:
                mail_content = self.__gui_proc.get_mail_content()
                if mail_content is not None:
                    mail_content.rc_data_mode_file()
                self.__mail_content_finally = mail_content
        finally:
            self.__win_fini()
            self.reject()

    def __win_fini(self):
        # 设置窗口关闭标记，关闭定时器
        self.__window_has_closed = True

    # -----------------------------------------------------------------------------------------
    # 增/删/编辑附件
    def __slot_add_appendix(self):
        s_list = QFileDialog.getOpenFileNames(self, QString(u"选择附件(可同时选中多个)"), "/", "All files(*.*)")
        self._ui_add_appends([unicode(each_append) for each_append in s_list])

    def __slot_del_appendix(self):
        selected = self.table_Appendix.selectedIndexes()
        # 从后往前删，否则会误删
        rows = sorted(list(set(s.row() for s in selected)), reverse=True)
        for each_row in rows:
            self.table_Appendix.removeRow(each_row)

        # 附件按钮文字改变
        self.__update_appendix_button_num()

    def __slot_appendix_item_changed(self, item):
        # 防止无穷递归
        if self._set_by_program > 0:
            return

        # 只有附件名可编辑
        # print(u"item_changed: row={}, column={}, text={}".format(item.row(), item.column(), item.text()))
        if item.column() != EmailEditor._COL_APPENDIX_NAME:
            return

        new_item = QTableWidgetItem(item)
        self._set_by_program += 1
        try:
            if not EmailEditor.__is_good_basename(unicode(item.text())):
                new_item.setBackgroundColor(EmailEditor._COLOR_WARNING)
                self.table_Appendix.setItem(item.row(), item.column(), new_item)
                new_item.setSelected(False)
            else:
                new_item.setBackgroundColor(Qt.transparent)
                self.table_Appendix.setItem(item.row(), item.column(), new_item)
                new_item.setSelected(False)
        finally:
            self._set_by_program -= 1

    def __slot_jump_appendix_tab(self):
        if self.tabWidget.currentIndex() != EmailEditor._TAB_INDEX_APPENDIX:
            self.tabWidget.setCurrentIndex(EmailEditor._TAB_INDEX_APPENDIX)

    def _ui_add_appends(self, full_append_path_list):
        # full_append_path_list的元素为字符串/MailResource类型
        for each_append in full_append_path_list:
            if isinstance(each_append, unicode) and each_append:
                self.__table_set_one_appendix(each_append)
            elif isinstance(each_append, MailResource) and each_append.path:
                self.__table_set_one_appendix(each_append.path, each_append.name)

        # 附件按钮文字改变
        self.__update_appendix_button_num()

    def __table_set_one_appendix(self, append_path, append_name_in=u"", index=None):
        """
        :param append_path: 附件实际路径
        :param append_name_in: 附件在邮件中显示的名字
        :param index: 显示在表格中的第几行，从0开始
        :return: 无
        """
        old_row_count = self.table_Appendix.rowCount()
        index_set = index if index else old_row_count
        if index_set >= old_row_count:
            self.table_Appendix.setRowCount(index_set + 1)

        # 注意附件可能不存在
        append_name = append_name_in if append_name_in else os.path.basename(append_path)
        state_ok = u"OK"
        state = state_ok if os.path.isfile(append_path) else u"不存在"
        if state == state_ok:
            append_size = u"{} K".format((os.path.getsize(append_path) + 1023) / 1024)
        else:
            append_size = 0

        items = [append_name, append_size, state, append_path]      # 附件名 大小 状态 路径
        editable = [True, False, False, False]
        align_center = [False, True, True, False]
        back_color = [None if EmailEditor.__is_good_basename(append_name) else EmailEditor._COLOR_WARNING,
                      None,
                      None if state == state_ok else EmailEditor._COLOR_ERROR,
                      None]

        for i, item in enumerate(items):
            table_item = QTableWidgetItem(QString(unicode(item)))
            if i < len(editable) and not editable[i]:
                old_flag = table_item.flags()
                table_item.setFlags(old_flag & (~Qt.ItemIsEditable))
            if i < len(align_center) and align_center[i]:
                table_item.setTextAlignment(Qt.AlignCenter)
            if i < len(back_color) and back_color[i]:
                table_item.setBackgroundColor(back_color[i])
            self.table_Appendix.setItem(index_set, i, table_item)

    @staticmethod
    def __is_good_basename(file_basename):
        patt = ur'\.[a-zA-Z0-9_]{1,5}$'
        if re.search(patt, file_basename):
            return True
        return False

    def __update_appendix_button_num(self):
        num = self.table_Appendix.rowCount()
        if num > 0:
            self.Button_Appendix.setText(QString(u"附件({}个)".format(num)))
        else:
            self.Button_Appendix.setText(QString(u"附件"))

    def __all_appendix(self):  # 返回由MailResource组成的列表
        num = self.table_Appendix.rowCount()
        appendix_list = []
        for i in range(num):
            path = unicode(self.table_Appendix.item(i, EmailEditor._COL_APPENDIX_PATH).text())
            name = unicode(self.table_Appendix.item(i, EmailEditor._COL_APPENDIX_NAME).text())
            appendix_list.append(MailResource(path, name))
        return appendix_list


def init():
    TmpFile.init()


def fini():
    TmpFile.fini()


def main():
    init()
    try:
        QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))
        app = QApplication(sys.argv)
        win = EmailEditor()
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

