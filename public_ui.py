#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *


# #####################################################################
# ########################### 无边框窗口 ###############################
class NoFrameWin(QWidget):

    def __init__(self, parent=None):
        super(NoFrameWin, self).__init__(parent)
        self._dragPosition = 0  # 窗口移动用
        self.setWindowOpacity(1)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowSystemMenuHint|Qt.WindowMinMaxButtonsHint)
        self.setWindowModality(Qt.ApplicationModal)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        # 定义鼠标移动事件
        if event.buttons() == Qt.LeftButton:
            g_pos = event.globalPos()
            if type(g_pos) != QPoint or type(self._dragPosition) != QPoint:
                return
            self.move(event.globalPos() - self._dragPosition)
            event.accept()


# #####################################################################
# ########################## 无边框透明窗口 #############################
class TransParentWin(NoFrameWin):

    def __init__(self, parent=None):
        super(TransParentWin, self).__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
