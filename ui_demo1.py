# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys


class StandardDialog(QDialog):

    def __init__(self,parent=None):
        super(StandardDialog,self).__init__(parent)

        self.setWindowTitle("Standard Dialog")

        filePushButton=QPushButton(self.tr("文件对话框"))
        colorPushButton=QPushButton(self.tr("颜色对话框"))
        fontPushButton=QPushButton(self.tr("字体对话框"))

        self.fileLineEdit=QLineEdit()
        self.colorFrame=QFrame()
        self.colorFrame.setFrameShape(QFrame.Box)
        self.colorFrame.setAutoFillBackground(True)
        self.fontLineEdit=QLineEdit("Hello World!")

        layout=QGridLayout()
        layout.addWidget(filePushButton,0,0)
        layout.addWidget(self.fileLineEdit,0,1)
        layout.addWidget(colorPushButton,1,0)
        layout.addWidget(self.colorFrame,1,1)
        layout.addWidget(fontPushButton,2,0)
        layout.addWidget(self.fontLineEdit,2,1)

        self.setLayout(layout)

        self.connect(filePushButton,SIGNAL("clicked()"),self.openFile)
        self.connect(colorPushButton,SIGNAL("clicked()"),self.openColor)
        self.connect(fontPushButton,SIGNAL("clicked()"),self.openFont)

    def openFile(self):

        s=QFileDialog.getOpenFileName(self,"Open file dialog","/","Python files(*.py)")
        self.fileLineEdit.setText(str(s))

    def openColor(self):

        c=QColorDialog.getColor(Qt.blue)
        if c.isValid():
            self.colorFrame.setPalette(QPalette(c))

    def openFont(self):

        f,ok=QFontDialog.getFont()
        if ok:
            self.fontLineEdit.setFont(f)


class Geometry(QDialog):

    def __init__(self,parent=None):
        super(Geometry,self).__init__(parent)

        self.setWindowTitle("Geometry")

        Label1=QLabel("x0:")
        Label2=QLabel("y0:")
        Label3=QLabel("frameGeometry():")
        Label4=QLabel("pos():")
        Label5=QLabel("geometry():")
        Label6=QLabel("width():")
        Label7=QLabel("height():")
        Label8=QLabel("rect():")
        Label9=QLabel("size():")

        self.xLabel=QLabel()
        self.yLabel=QLabel()
        self.frameGeoLabel=QLabel()
        self.posLabel=QLabel()
        self.geoLabel=QLabel()
        self.widthLabel=QLabel()
        self.heightLabel=QLabel()
        self.rectLabel=QLabel()
        self.sizeLabel=QLabel()

        layout=QGridLayout()
        layout.addWidget(Label1,0,0)
        layout.addWidget(self.xLabel,0,1)
        layout.addWidget(Label2,1,0)
        layout.addWidget(self.yLabel,1,1)
        layout.addWidget(Label3,2,0)
        layout.addWidget(self.frameGeoLabel,2,1)
        layout.addWidget(Label4,3,0)
        layout.addWidget(self.posLabel,3,1)
        layout.addWidget(Label5,4,0)
        layout.addWidget(self.geoLabel,4,1)
        layout.addWidget(Label6,5,0)
        layout.addWidget(self.widthLabel,5,1)
        layout.addWidget(Label7,6,0)
        layout.addWidget(self.heightLabel,6,1)
        layout.addWidget(Label8,7,0)
        layout.addWidget(self.rectLabel,7,1)
        layout.addWidget(Label9,8,0)
        layout.addWidget(self.sizeLabel,8,1)

        self.setLayout(layout)

        self.updateLabel()

    def moveEvent(self,event):
        self.updateLabel()

    def resizeEvent(self,event):
        self.updateLabel()

    def updateLabel(self):
        temp=QString()

        self.xLabel.setText(temp.setNum(self.x()))
        self.yLabel.setText(temp.setNum(self.y()))
        self.frameGeoLabel.setText(temp.setNum(self.frameGeometry().x())+","+
                                   temp.setNum(self.frameGeometry().y())+","+
                                   temp.setNum(self.frameGeometry().width())+","+
                                   temp.setNum(self.frameGeometry().height()))

        self.posLabel.setText(temp.setNum(self.pos().x())+","+
                              temp.setNum(self.pos().y()))
        self.geoLabel.setText(temp.setNum(self.geometry().x())+","+
                              temp.setNum(self.geometry().y())+","+
                              temp.setNum(self.geometry().width())+","+
                              temp.setNum(self.geometry().height()))
        self.widthLabel.setText(temp.setNum(self.width()))
        self.heightLabel.setText(temp.setNum(self.height()))
        self.rectLabel.setText(temp.setNum(self.rect().x())+","+
                               temp.setNum(self.rect().y())+","+
                               temp.setNum(self.rect().width())+","+
                               temp.setNum(self.rect().height()))
        self.sizeLabel.setText(temp.setNum(self.size().width())+","+
                               temp.setNum(self.size().height()))


class InputDlg(QDialog):
    def __init__(self,parent=None):
        super(InputDlg,self).__init__(parent)

        label1=QLabel(self.tr("姓名"))
        label2=QLabel(self.tr("性别"))
        label3=QLabel(self.tr("年龄"))
        label4=QLabel(self.tr("身高"))

        self.nameLabel=QLabel("TengWei")
        self.nameLabel.setFrameStyle(QFrame.Panel|QFrame.Sunken)
        self.sexLabel=QLabel(self.tr("男"))
        self.sexLabel.setFrameStyle(QFrame.Panel|QFrame.Sunken)
        self.ageLabel=QLabel("25")
        self.ageLabel.setFrameStyle(QFrame.Panel|QFrame.Sunken)
        self.statureLabel=QLabel("168")
        self.statureLabel.setFrameStyle(QFrame.Panel|QFrame.Sunken)

        nameButton=QPushButton("...")
        sexButton=QPushButton("...")
        ageButton=QPushButton("...")
        statureButton=QPushButton("...")

        self.connect(nameButton,SIGNAL("clicked()"),self.slotName)
        self.connect(sexButton,SIGNAL("clicked()"),self.slotSex)
        self.connect(ageButton,SIGNAL("clicked()"),self.slotAge)
        self.connect(statureButton,SIGNAL("clicked()"),self.slotStature)

        layout=QGridLayout()
        layout.addWidget(label1,0,0)
        layout.addWidget(self.nameLabel,0,1)
        layout.addWidget(nameButton,0,2)
        layout.addWidget(label2,1,0)
        layout.addWidget(self.sexLabel,1,1)
        layout.addWidget(sexButton,1,2)
        layout.addWidget(label3,2,0)
        layout.addWidget(self.ageLabel,2,1)
        layout.addWidget(ageButton,2,2)
        layout.addWidget(label4,3,0)
        layout.addWidget(self.statureLabel,3,1)
        layout.addWidget(statureButton,3,2)

        self.setLayout(layout)

        self.setWindowTitle(self.tr("资料收集"))

    def slotName(self):
        name,ok=QInputDialog.getText(self,self.tr("用户名"),
                                     self.tr("请输入新的名字:"),
                                     QLineEdit.Normal,self.nameLabel.text())
        if ok and (not name.isEmpty()):
            self.nameLabel.setText(name)

    def slotSex(self):
        list=QStringList()
        list.append(self.tr("男"))
        list.append(self.tr("女"))
        sex,ok=QInputDialog.getItem(self,self.tr("性别"),self.tr("请选择性别"),list)

        if ok:
            self.sexLabel.setText(sex)

    def slotAge(self):
        age,ok=QInputDialog.getInteger(self,self.tr("年龄"),
                                       self.tr("请输入年龄:"),
                                       int(self.ageLabel.text()),0,150)
        if ok:
            self.ageLabel.setText(str(age))

    def slotStature(self):
        stature,ok=QInputDialog.getDouble(self,self.tr("身高"),
                                          self.tr("请输入身高:"),
                                          float(self.statureLabel.text()),0,2300.00)
        if ok:
            self.statureLabel.setText(str(stature))


class MessageBoxDlg(QDialog):
    def __init__(self,parent=None):
        super(MessageBoxDlg,self).__init__(parent)
        self.setWindowTitle("Messagebox")
        self.label=QLabel("About Qt MessageBox")
        questionButton=QPushButton("Question")
        informationButton=QPushButton("Information")
        warningButton=QPushButton("Warning")
        criticalButton=QPushButton("Critical")
        aboutButton=QPushButton("About")
        aboutqtButton=QPushButton("About Qt")
        customButton=QPushButton("Custom")

        gridLayout=QGridLayout(self)
        gridLayout.addWidget(self.label,0,0,1,2)
        gridLayout.addWidget(questionButton,1,0)
        gridLayout.addWidget(informationButton,1,1)
        gridLayout.addWidget(warningButton,2,0)
        gridLayout.addWidget(criticalButton,2,1)
        gridLayout.addWidget(aboutButton,3,0)
        gridLayout.addWidget(aboutqtButton,3,1)
        gridLayout.addWidget(customButton,4,0)

        self.connect(questionButton,SIGNAL("clicked()"),self.slotQuestion)
        self.connect(informationButton,SIGNAL("clicked()"),self.slotInformation)
        self.connect(warningButton,SIGNAL("clicked()"),self.slotWarning)
        self.connect(criticalButton,SIGNAL("clicked()"),self.slotCritical)
        self.connect(aboutButton,SIGNAL("clicked()"),self.slotAbout)
        self.connect(aboutqtButton,SIGNAL("clicked()"),self.slotAboutQt)
        self.connect(customButton,SIGNAL("clicked()"),self.slotCustom)

    def slotQuestion(self):
        button=QMessageBox.question(self,"Question",
                                    self.tr("已到达文档结尾,是否从头查找?"),
                                    QMessageBox.Ok|QMessageBox.Cancel,
                                    QMessageBox.Ok)
        if button==QMessageBox.Ok:
            self.label.setText("Question button/Ok")
        elif button==QMessageBox.Cancel:
            self.label.setText("Question button/Cancel")
        else:
            return

    def slotInformation(self):
        QMessageBox.information(self,"Information",
                                self.tr("填写任意想告诉于用户的信息!"))
        self.label.setText("Information MessageBox")

    def slotWarning(self):
        button=QMessageBox.warning(self,"Warning",
                                   self.tr("是否保存对文档的修改?"),
                                   QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel,
                                   QMessageBox.Save)
        if button==QMessageBox.Save:
            self.label.setText("Warning button/Save")
        elif button==QMessageBox.Discard:
            self.label.setText("Warning button/Discard")
        elif button==QMessageBox.Cancel:
            self.label.setText("Warning button/Cancel")
        else:
            return

    def slotCritical(self):
        QMessageBox.critical(self,"Critical",
                             self.tr("提醒用户一个致命的错误!"))
        self.label.setText("Critical MessageBox")

    def slotAbout(self):
        QMessageBox.about(self,"About",self.tr("About事例"))
        self.label.setText("About MessageBox")

    def slotAboutQt(self):
        QMessageBox.aboutQt(self,"About Qt")
        self.label.setText("About Qt MessageBox")

    def slotCustom(self):
        customMsgBox=QMessageBox(self)
        customMsgBox.setWindowTitle("Custom message box")
        lockButton=customMsgBox.addButton(self.tr("锁定"),
                                          QMessageBox.ActionRole)
        unlockButton=customMsgBox.addButton(self.tr("解锁"),
                                            QMessageBox.ActionRole)
        cancelButton=customMsgBox.addButton("cancel",QMessageBox.ActionRole)

        customMsgBox.setText(self.tr("这是一个自定义消息框!"))
        customMsgBox.exec_()

        button=customMsgBox.clickedButton()
        if button==lockButton:
            self.label.setText("Custom MessageBox/Lock")
        elif button==unlockButton:
            self.label.setText("Custom MessageBox/Unlock")
        elif button==cancelButton:
            self.label.setText("Custom MessageBox/Cancel")


class MyQQ(QToolBox):
    def __init__(self,parent=None):
        super(MyQQ,self).__init__(parent)

        toolButton1_1=QToolButton()
        toolButton1_1.setText(self.tr("朽木"))
        toolButton1_1.setIcon(QIcon("image/9.gif"))
        toolButton1_1.setIconSize(QSize(60,60))
        toolButton1_1.setAutoRaise(True)
        toolButton1_1.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        toolButton1_2=QToolButton()
        toolButton1_2.setText(self.tr("Cindy"))
        toolButton1_2.setIcon(QIcon("image/8.gif"))
        toolButton1_2.setIconSize(QSize(60,60))
        toolButton1_2.setAutoRaise(True)
        toolButton1_2.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        toolButton1_3=QToolButton()
        toolButton1_3.setText(self.tr("了了"))
        toolButton1_3.setIcon(QIcon("image/1.gif"))
        toolButton1_3.setIconSize(QSize(60,60))
        toolButton1_3.setAutoRaise(True)
        toolButton1_3.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        toolButton1_4=QToolButton()
        toolButton1_4.setText(self.tr("张三虎"))
        toolButton1_4.setIcon(QIcon("image/3.gif"))
        toolButton1_4.setIconSize(QSize(60,60))
        toolButton1_4.setAutoRaise(True)
        toolButton1_4.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        toolButton1_5=QToolButton()
        toolButton1_5.setText(self.tr("CSDN"))
        toolButton1_5.setIcon(QIcon("image/4.gif"))
        toolButton1_5.setIconSize(QSize(60,60))
        toolButton1_5.setAutoRaise(True)
        toolButton1_5.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        toolButton2_1=QToolButton()
        toolButton2_1.setText(self.tr("天的另一边"))
        toolButton2_1.setIcon(QIcon("image/5.gif"))
        toolButton2_1.setIconSize(QSize(60,60))
        toolButton2_1.setAutoRaise(True)
        toolButton2_1.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        toolButton2_2=QToolButton()
        toolButton2_2.setText(self.tr("蓝绿不分"))
        toolButton2_2.setIcon(QIcon("image/6.gif"))
        toolButton2_2.setIconSize(QSize(60,60))
        toolButton2_2.setAutoRaise(True)
        toolButton2_2.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        toolButton3_1=QToolButton()
        toolButton3_1.setText(self.tr("老牛"))
        toolButton3_1.setIcon(QIcon("image/7.gif"))
        toolButton3_1.setIconSize(QSize(60,60))
        toolButton3_1.setAutoRaise(True)
        toolButton3_1.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        toolButton3_2=QToolButton()
        toolButton3_2.setText(self.tr("张三疯"))
        toolButton3_2.setIcon(QIcon("image/8.gif"))
        toolButton3_2.setIconSize(QSize(60,60))
        toolButton3_2.setAutoRaise(True)
        toolButton3_2.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        groupbox1=QGroupBox()
        vlayout1=QVBoxLayout(groupbox1)
        vlayout1.setMargin(10)
        vlayout1.setAlignment(Qt.AlignCenter)
        vlayout1.addWidget(toolButton1_1)
        vlayout1.addWidget(toolButton1_2)
        vlayout1.addWidget(toolButton1_3)
        vlayout1.addWidget(toolButton1_4)
        vlayout1.addWidget(toolButton1_5)
        vlayout1.addStretch()

        groupbox2=QGroupBox()
        vlayout2=QVBoxLayout(groupbox2)
        vlayout2.setMargin(10)
        vlayout2.setAlignment(Qt.AlignCenter)
        vlayout2.addWidget(toolButton2_1)
        vlayout2.addWidget(toolButton2_2)

        groupbox3=QGroupBox()
        vlayout3=QVBoxLayout(groupbox3)
        vlayout3.setMargin(10)
        vlayout3.setAlignment(Qt.AlignCenter)
        vlayout3.addWidget(toolButton3_1)
        vlayout3.addWidget(toolButton3_2)

        self.addItem(groupbox1,self.tr("我的好友"))
        self.addItem(groupbox2,self.tr("同事"))
        self.addItem(groupbox3,self.tr("黑名单"))


class MyTable(QTableWidget):
    def __init__(self,parent=None):
        super(MyTable,self).__init__(parent)
        self.setColumnCount(5)
        self.setRowCount(2)
        self.setItem(0,0,QTableWidgetItem(self.tr("性别")))
        self.setItem(0,1,QTableWidgetItem(self.tr("姓名")))
        self.setItem(0,2,QTableWidgetItem(self.tr("出生日期")))
        self.setItem(0,3,QTableWidgetItem(self.tr("职业")))
        self.setItem(0,4,QTableWidgetItem(self.tr("收入")))
        lbp1=QLabel()
        lbp1.setPixmap(QPixmap("image/4.gif"))
        self.setCellWidget(1,0,lbp1)
        twi1=QTableWidgetItem("Tom")
        self.setItem(1,1,twi1)
        dte1=QDateTimeEdit()
        dte1.setDateTime(QDateTime.currentDateTime())
        dte1.setDisplayFormat("yyyy/mm/dd")
        dte1.setCalendarPopup(True)
        self.setCellWidget(1,2,dte1)
        cbw=QComboBox()
        cbw.addItem("Worker")
        cbw.addItem("Famer")
        cbw.addItem("Doctor")
        cbw.addItem("Lawyer")
        cbw.addItem("Soldier")
        self.setCellWidget(1,3,cbw)
        sb1=QSpinBox()
        sb1.setRange(1000,10000)
        self.setCellWidget(1,4,sb1)


class Progess(QDialog):
    def __init__(self,parent=None):
        super(Progess,self).__init__(parent)
        self.setWindowTitle(self.tr("使用进度条"))
        numLabel=QLabel(self.tr("文件数目"))
        self.numLineEdit=QLineEdit("10")
        typeLabel=QLabel(self.tr("显示类型"))
        self.typeComboBox=QComboBox()
        self.typeComboBox.addItem(self.tr("进度条"))
        self.typeComboBox.addItem(self.tr("进度对话框"))

        self.progressBar=QProgressBar()

        startPushButton=QPushButton(self.tr("开始"))

        layout=QGridLayout()
        layout.addWidget(numLabel,0,0)
        layout.addWidget(self.numLineEdit,0,1)
        layout.addWidget(typeLabel,1,0)
        layout.addWidget(self.typeComboBox,1,1)
        layout.addWidget(self.progressBar,2,0,1,2)
        layout.addWidget(startPushButton,3,1)
        layout.setMargin(15)
        layout.setSpacing(10)

        self.setLayout(layout)

        self.connect(startPushButton,SIGNAL("clicked()"),self.slotStart)

    def slotStart(self):
        num=int(self.numLineEdit.text())

        if self.typeComboBox.currentIndex()==0:
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(num)

            for i in range(num + 1):
                self.progressBar.setValue(i)
                QThread.msleep(200)

        elif self.typeComboBox.currentIndex()==1:
            progressDialog=QProgressDialog(self)
            progressDialog.setWindowModality(Qt.WindowModal)
            progressDialog.setMinimumDuration(5)
            progressDialog.setWindowTitle(self.tr("请等待"))
            progressDialog.setLabelText(self.tr("拷贝..."))
            progressDialog.setCancelButtonText(self.tr("取消"))
            progressDialog.setRange(0,num)

            for i in range(num + 1):
                progressDialog.setValue(i)
                QThread.msleep(200)
                if progressDialog.wasCanceled():
                    return

################################################################################

class StringListDlg(QDialog):
    """
    主对话框
    """
    def __init__(self, fruit, parent=None):
        super(StringListDlg, self).__init__(parent)
        self.fruit = fruit
        #字符串列表
        self.fruits = QListWidget()
        #for f in self.fruit:
        #    self.fruits.addItem(QListWidgetItem(f))
        self.fruits.addItems(fruit)
        #按钮
        btn_add = QPushButton('&Add...')
        btn_edit = QPushButton('&Edit...')
        btn_remove = QPushButton('&Remove...')
        btn_up = QPushButton('&Up')
        btn_down = QPushButton('&Down')
        btn_sort = QPushButton('&Sort')
        btn_close = QPushButton('&Close')
        #垂直布局
        v_box = QVBoxLayout()
        v_box.addWidget(btn_add)
        v_box.addWidget(btn_edit)
        v_box.addWidget(btn_remove)
        v_box.addWidget(btn_up)
        v_box.addWidget(btn_down)
        v_box.addWidget(btn_sort)
        v_box.addStretch(1)
        v_box.addWidget(btn_close)
        #水平布局
        h_box = QHBoxLayout()
        h_box.addWidget(self.fruits)
        h_box.addLayout(v_box)
        #设置布局
        self.setLayout(h_box)
        self.resize(QSize(400,300))
        self.setWindowTitle(u'水果')
        #连接信号和槽
        btn_add.clicked.connect(self.add)
        btn_edit.clicked.connect(self.edit)
        btn_remove.clicked.connect(self.remove)
        btn_up.clicked.connect(self.up)
        btn_down.clicked.connect(self.down)
        btn_sort.clicked.connect(self.sort)
        btn_close.clicked.connect(self.close)

    #定义槽
    def add(self):
        #添加
        add = FruitDlg('Add fruit',self)
        if add.exec_():
            fruit_added = add.fruit
            self.fruits.addItem(fruit_added)
            print(fruit_added)

    def edit(self):
        #编辑
        row = self.fruits.currentRow()
        fruit = self.fruits.takeItem(row)
        edit = FruitDlg('Edit fruit', fruit.text(), self)
        if edit.exec_():
            print(edit.fruit)
            self.fruits.addItem(edit.fruit)


    def remove(self):
        #移除
        if QMessageBox.warning(self, u'确认', u'确定要删除?', QMessageBox.Ok | QMessageBox.Cancel) == QMessageBox.Ok:
            item_deleted = self.fruits.takeItem(self.fruits.currentRow())
            #将读取的值设置为None
            item_deleted = None

    def up(self):
        #上移
        #当前元素索引
        index = self.fruits.currentRow()
        if index > 0:
            #索引号减1
            index_new = index - 1
            #取元素值，并在新索引位置插入
            self.fruits.insertItem(index_new, self.fruits.takeItem(self.fruits.currentRow()))
            #设置当前元素索引为新插入位置，可以使得元素连续上移
            self.fruits.setCurrentRow(index_new)

    def down(self):
        #下移
        index = self.fruits.currentRow()
        if index < self.fruits.count():
            index_new = index + 1
            self.fruits.insertItem(index_new, self.fruits.takeItem(self.fruits.currentRow()))
            self.fruits.setCurrentRow(index_new)

    def sort(self):
        #排序
        self.fruits.sortItems(Qt.AscendingOrder)
    def close(self):
        #退出
        self.done(0)


#弹出对话框
#add
class FruitDlg(QDialog):
    def __init__(self, title, fruit=None, parent=None):
        super(FruitDlg, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)

        #label_0 = QLabel(u'Add fruit： 譬如苹果，香蕉，橘子，西瓜，火龙果，枣，梨子，榴莲')
        label_0 = QLabel(title)
        #让标签字换行
        label_0.setWordWrap(True)
        self.fruit_edit = QLineEdit(fruit)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        validator = QRegExp(r'[^\s][\w\s]+')
        self.fruit_edit.setValidator(QRegExpValidator(validator, self))

        v_box = QVBoxLayout()
        v_box.addWidget(label_0)
        v_box.addWidget(self.fruit_edit)
        v_box.addWidget(btns)
        self.setLayout(v_box)

        self.fruit = None

    def accept(self):
        #OK按钮
        self.fruit = unicode(self.fruit_edit.text())
        #self.done(0)
        QDialog.accept(self)

    def reject(self):
        #self.done(1)
        QDialog.reject(self)

######################################################################


def test1():
    app=QApplication(sys.argv)
    form=StandardDialog()
    form.show()
    app.exec_()


def test2():
    app=QApplication(sys.argv)
    form=Geometry()
    form.show()
    app.exec_()


def test3():
    app=QApplication(sys.argv)
    form=InputDlg()
    form.show()
    app.exec_()


def test4():
    app=QApplication(sys.argv)
    MessageBox=MessageBoxDlg()
    MessageBox.show()
    app.exec_()


def test5():
    app=QApplication(sys.argv)
    myqq=MyQQ()
    myqq.setWindowTitle("My QQ")
    myqq.show()
    app.exec_()


def test6():
    # 表格
    app=QApplication(sys.argv)
    myqq=MyTable()
    myqq.setWindowTitle("My Table")
    myqq.show()
    app.exec_()


def test7():
    app=QApplication(sys.argv)
    progess=Progess()
    progess.show()
    app.exec_()


def test8():
    app = QApplication(sys.argv)
    fruit = ["Banana", "Apple", "Elderberry", "Clementine", "Fig", "Guava", "Mango", "Honeydew Melon",
             "Date", "Watermelon", "Tangerine", "Ugli Fruit", "Juniperberry", "Kiwi",
             "Lemon", "Nectarine", "Plum", "Raspberry", "Strawberry", "Orange"]
    s = StringListDlg(fruit)
    s.show()
    app.exec_()

if __name__ == "__main__":
    QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))
    test8()
