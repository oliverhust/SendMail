#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from demo_ui import Ui_MainWindow

import Demo1

# Self Function
def PrintHello():
    print("Hello")

# Make main window class
class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)
        self.setupUi(self)
        # Connect button click event to PrintHello function
        self.pushButton.clicked.connect(PrintHello)

# End of main window class


# Main Function
if __name__=='__main__':
    Demo1.main()
    Program = QApplication(sys.argv)
    Window=MainWindow()
    Window.show()
    Program.exec_()