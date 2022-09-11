#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @ Date: 2021-07-26 11:49
# @ Author: paperClub


import os
from PyQt5 import QtWidgets
from PyQt5.Qt import QLabel, QPushButton, \
    QLineEdit, QWidget, pyqtSignal, QThread,\
    QObject, pyqtProperty, QApplication, \
    QHBoxLayout, QVBoxLayout, QPixmap, Qt,\
    QPainter, QPainterPath, QMenuBar, QTabWidget,\
    QFileDialog, QGraphicsView, QGraphicsScene, \
    QPropertyAnimation, QGraphicsPixmapItem, \
    QMessageBox, QTextEdit


import sys, qtawesome

try:
    from api_service import *
except Exception as import_error:
    print(f"import_error: {import_error}")


############ 1. 左侧按钮 及 UI布局

### 一级菜单栏
LeftMenus = ["我的工具", "联系与帮助"]
menus_of_tools = ["文件转换", "图像处理", "数据绘图"]
menus_of_contaction = ["建议与反馈", "软件与版本"]
Meus = menus_of_tools + menus_of_contaction

#### 二级菜单栏
css_list = []
css_list.append('fa5.file')  # 文件转换
css_list.append('fa5s.image')  # 图像处理
css_list.append('fa5s.chart-bar')  # 数据绘图
css_list.append('fa5.envelope')  # 建议与反馈
css_list.append('fa5b.windows')  # 软件与版本

#### 三级菜单栏（左侧）
docmentconvert_menus = ["格式转换", "提取拆分", "处理合并"]  # 我的工具 ——> 文本处理
imageprocess_menus = ["转换缩放", "图像处理"]  # 我的工具 ——> 图像处理
data_visualization_menus = ["常用绘图"]  # 我的工具 ——> 数据绘图

menu_dict = {}
menu_dict[LeftMenus[0]] = menus_of_tools
menu_dict[LeftMenus[1]] = menus_of_contaction

OUT_DIR = os.path.join(os.getcwd(), 'Results')
if not os.path.exists(OUT_DIR): os.mkdir(OUT_DIR)


class QLabel_for_menuTitle(QLabel):
    """ 左侧 导航栏一级菜单栏 设置"""

    def __init__(self, text):
        super(QLabel_for_menuTitle, self).__init__()
        self.setText(text)
        self.setStyleSheet('''QLabel {padding: 12px; color:#ffff00;
                                    text-align: justify;
                                    border:none;
                                    border-bottom:1px solid white;
                                    font-weight:700;
                                    font-weight:bold; font-size:18px;
                                    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                            }''')
        self.setAlignment(Qt.AlignCenter)


class QPushButton_for_item(QPushButton):
    """ 左侧导航栏二级菜单栏 设置 """

    def __init__(self, icon_str, text):
        super(QPushButton_for_item, self).__init__()
        self.setIcon(qtawesome.icon(icon_str, color='white'))
        self.setText(text)
        self.adjustSize()


class QRegExp_QLineEdit(QLineEdit):
    '''
	对文本框进行重写，让文本框具有只允许输入0-9数学及‘，’和‘-’字符。其它不允许输入。且首字不能为0.
	'''

    def __init__(self):
        super(QRegExp_QLineEdit, self).__init__()
        self.setPlaceholderText("设置页码");
        self.setToolTip("例：1,2,5-7")
        self.textChanged.connect(self.exec_text)

    def exec_text(self):  # 锁定字符。
        for item_text in self.text():
            if item_text not in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ",", "-"):
                self.setText(self.text().replace(item_text, ""))

    def keyPressEvent(self, event):  # 键盘输入事件。
        num1_9_dict = {Qt.Key_1: "1", Qt.Key_2: "2", Qt.Key_3: "3",
                       Qt.Key_4: "4", Qt.Key_5: "5", Qt.Key_6: "6",
                       Qt.Key_7: "7", Qt.Key_8: "8", Qt.Key_9: "9"}
        for key in num1_9_dict:  # 对1-9进处理
            if event.key() == key:
                self.setText(self.text() + num1_9_dict[key])
        if event.key() == Qt.Key_Backspace:  # 对退格键进行处理
            if len(self.text()) > 0:
                self.setText(self.text()[0:len(self.text()) - 1])
        elif event.key() == Qt.Key_0:  # 对数学0进行处理
            if len(self.text()) > 0:
                self.setText(f"{self.text()}0")
        elif event.key() == Qt.Key_Minus:  # 对符号‘-’进行处理
            self.setText(f"{self.text()}-")
        elif event.key() == Qt.Key_Comma:  # 对符号‘，’进行处理。
            self.setText(f"{self.text()},".replace("，", ","))
        else:
            pass


class QRegExp_QLineEdit2(QLineEdit):
    '''
    图像缩放倍数 / 固定宽高等比缩放 / 图像压缩大小
    '''

    def __init__(self, name="设置", tip_str='2.5'):
        super(QRegExp_QLineEdit2, self).__init__()
        self.setPlaceholderText(name);
        self.setToolTip(f"例：{tip_str}")
        self.textChanged.connect(self.exec_text)

    def exec_text(self):  # 锁定字符。
        for item_text in self.text():
            if item_text not in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."):
                self.setText(self.text().replace(item_text, ""))

    def keyPressEvent(self, event):  # 键盘输入事件。
        factor_dict = {Qt.Key_1: "1", Qt.Key_2: "2", Qt.Key_3: "3",
                       Qt.Key_4: "4", Qt.Key_5: "5", Qt.Key_6: "6",
                       Qt.Key_7: "7", Qt.Key_8: "8", Qt.Key_9: "9",
                       Qt.Key_0: "0", Qt.Key_Period: "."}

        for key in factor_dict:  # 对1-9进处理
            if event.key() == key:
                self.setText(self.text() + factor_dict[key])
        if event.key() == Qt.Key_Backspace:  # 对退格键进行处理
            if len(self.text()) > 0:
                self.setText(self.text()[0:len(self.text()) - 1])

        else:
            pass



class QWidget_mergePDF(QWidget):
    """ PDF合并处理 """

    browse_clicked_signal = pyqtSignal(object)

    def __init__(self, parent):
        super(QWidget_mergePDF, self).__init__()
        self.parent = parent
        self.setting()
        self.add_btn()
        self.add_control()

    def get_QLineEdit_Text_for_filepath(self):
        list_temp = []
        for item_list in self.__control_list:
            list_temp.append(item_list['QLineEdit'].text())
        return list_temp

    def get_QLineEditObj_for_sender(self, sender):
        text_obj = None
        for item in self.__control_list:
            if item['QPushButton'] is sender:
                text_obj = item['QLineEdit']
                break
        return text_obj

    def setting(self):
        self.__Layout_main = QVBoxLayout()
        self.__layout_list = []
        self.__control_list = []
        self.setLayout(self.__Layout_main)
        self.path_dict = {}
        self.hide()
        self.setParent(self.parent)
        self.resize(self.parent.width() * 0.79, self.parent.height() - 30)
        self.move(self.parent.width() * 0.29, 30)
        self.QPushButton_Add = QPushButton("+", self)
        self.QPushButton_Add.setFixedWidth(50)
        self.QPushButton_Sub = QPushButton("-", self)
        self.QPushButton_Sub.setFixedWidth(50)
        self.QPushButton_Add.clicked.connect(self.add_control)
        self.QPushButton_Sub.clicked.connect(self.sub_control)

    def add_control(self):
        self.__control_list.append({'QLineEdit': QLineEdit(), 'QPushButton': QPushButton('浏览', self)})
        self.__layout_list.append(QHBoxLayout())
        self.__layout_list[len(self.__layout_list) - 1].addWidget(
            self.__control_list[len(self.__control_list) - 1]['QLineEdit'])
        self.__layout_list[len(self.__layout_list) - 1].addWidget(
            self.__control_list[len(self.__control_list) - 1]['QPushButton'])
        self.__Layout_main.insertLayout(self.__Layout_main.count() - 2, self.__layout_list[len(self.__layout_list) - 1])
        self.__control_list[len(self.__control_list) - 1]['QPushButton'].clicked.connect(self.selectPDFfile)

    def selectPDFfile(self):
        sender = self.sender()
        self.browse_clicked_signal.emit(self.sender())

    def sub_control(self):
        if self.__Layout_main.count() > 3:
            for i in range(2):
                self.__Layout_main.itemAt(self.__Layout_main.count() - 3).itemAt(i).widget().deleteLater()
            del self.__control_list[len(self.__control_list) - 1]
            del self.__layout_list[len(self.__layout_list) - 1]
            self.__Layout_main.removeItem(self.__Layout_main.itemAt(self.__Layout_main.count() - 3))
        else:
            QMessageBox.information(self.parent, '提示', '至少要保留一组。', QMessageBox.Ok)

    def add_btn(self):

        self.__layout_list.append(QHBoxLayout())
        self.__layout_list[len(self.__layout_list) - 1].addWidget(self.QPushButton_Add)
        self.__layout_list[len(self.__layout_list) - 1].addWidget(self.QPushButton_Sub)
        self.__Layout_main.addLayout(self.__layout_list[len(self.__layout_list) - 1])
        self.__Layout_main.addStretch()


class QThread_pdf2img(QThread):
    """ 多线程：PDF --> 图片"""

    def __init__(self, pdf_file):
        super(QThread_pdf2img, self).__init__()
        self.pdf_file = pdf_file

    def run(self):
        mytools_text._pdf_to_image(pdffile=self.pdf_file, output_dir=OUT_DIR)


class QThread_pdfextract_img(QThread):
    """ 多线程： PDF --> 提取页面中的 """

    def __init__(self, pdf_file):
        super(QThread_pdfextract_img, self).__init__()
        self.pdf_file = pdf_file

    def run(self):
        mytools_text._pdf_image_extract(pdffile=self.pdf_file, output_dir=OUT_DIR)


class QThread_pdf2word(QThread):
    '''
	由于PDF转WORD转换时间较长，容易造成页面假死，所以使用多PyQt5自带的多线程，来处理脚本。
	启动此线程等待的时间。可给用户进行一个等待提示。
	'''

    def __init__(self, pdf_file, doc_file):
        super(QThread_pdf2word, self).__init__()
        self.pdf_file = pdf_file
        self.doc_file = doc_file

    def run(self):
        mytools_text._pdf2word(self.pdf_file, self.doc_file)





class loading_animation_QObject(QObject):
    '''
	用于处理时间较长的脚本时，展现loading加载动画。增强世界友好性。
	'''

    def __init__(self):
        super(loading_animation_QObject, self).__init__()
        pixmap = QPixmap("css/loading.png")
        scaled = pixmap.scaled(20, 20)
        self.auto_animation()
        self.pixmap_item = QGraphicsPixmapItem(scaled)
        self.pixmap_item.setTransformOriginPoint(10, 10)  # 设置中心为旋转

    def _set_rotation(self, degree):
        self.pixmap_item.setRotation(degree)  # 自身改变旋转度数

    def setAnimationStop(self):
        self.animation.stop()
        self.hide()

    def auto_animation(self):
        self.animation = QPropertyAnimation(self, b'rotation')  # 动画类型
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)  # 初始角度
        self.animation.setEndValue(360)
        self.animation.setLoopCount(-1)  # 设置循环旋转

    rotation = pyqtProperty(int, fset=_set_rotation)  # 属性动画改变自身数值


class Main_Ui(QWidget):
    """ 主界面 """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.resize(1000, 800) ## 窗口初始化大小
        self.setFixedSize(1000, 800) ## 窗口固定
        ################ 1. UI左侧菜单栏  #######################
        self.main_layout = QHBoxLayout()  # 创建主部件的水平布局
        self.setLayout(self.main_layout)  # 设置窗口主部件布局水平布局
        self.left_widget = QWidget()  # 创建左侧部件
        self.left_widget.setFixedWidth(self.width() * 0.2)  # app宽度的2：8
        self.right_widget = QWidget()  # 创建右侧部件
        self.right_widget.setFixedWidth(self.width() * 0.8)
        self.left_widget.setObjectName('left_widget')
        self.right_widget.setObjectName('right_widget')
        self.main_layout.addWidget(self.left_widget)
        self.main_layout.addWidget(self.right_widget)
        self.left_layout = QVBoxLayout()  # 创建左侧部件的垂直布局
        self.right_layout = QVBoxLayout()
        self.left_widget.setLayout(self.left_layout)  # 设置左侧部件布局为网格
        self.right_widget.setLayout(self.right_layout)
        self.main_layout.addWidget(self.left_widget)
        self.main_layout.addWidget(self.right_widget)
        self.control_QLabel_dict = {}  # 创建两个字典用做批量控件的变量
        self.control_QPushButton_dict = {}
        n = 0
        self.control_QLabel_dict['img'] = QLabel(self)

        ### 图片添加圆角
        pixmapa = QPixmap("css/logo1.png")
        pixmap = QPixmap(180, 62)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.begin(self)  # 要将绘制过程用begin(self)和end()包起来
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)  # 一个是平滑，一个是缩放保持比例
        path = QPainterPath()
        path.addRoundedRect(10, 10, 150, 62, 10, 10)
        painter.setClipPath(path)
        painter.drawPixmap(10, 10, 150, 62, pixmapa)
        painter.end()

        self.control_QLabel_dict['img'].setPixmap(pixmap)  # 在label上显示图片
        self.control_QLabel_dict['img'].setAlignment(Qt.AlignLeft)
        self.left_layout.addWidget(self.control_QLabel_dict['img'])
        for key in menu_dict.keys():
            self.control_QLabel_dict[key] = QLabel_for_menuTitle(key)
            self.control_QLabel_dict[key].setObjectName('left_label')
            self.left_layout.addWidget(self.control_QLabel_dict[key])
            for item in menu_dict[key]:
                self.control_QPushButton_dict[item] = QPushButton_for_item(css_list[n], item)
                self.left_layout.addWidget(self.control_QPushButton_dict[item])
                self.control_QPushButton_dict[item].setObjectName('left_button')
                n += 1

        self.left_layout.addStretch()
        self.left_widget.setStyleSheet('''
                            QPushButton{border:none;color:white;}
                            QPushButton#left_label{
                                border:none;
                                border-bottom:1px solid white;
                                font-size:18px;
                                font-weight:700;
                                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                            }
                            QPushButton#left_button:hover{border-left:4px solid red;font-weight:700;}
                            QWidget#left_widget{
                            background:gray;
                            border-top:1px solid white;
                            border-bottom:1px solid white;
                            border-left:1px solid white;
                            border-top-left-radius:10px;
                            border-bottom-left-radius:10px;
                            }
                        ''')

        ################ 2. 顶部菜单栏  ####################
        mainMenu = QMenuBar(self)
        mainMenu.setFixedWidth(self.width())
        fileMenu = mainMenu.addMenu('首页')
        editMenu = mainMenu.addMenu('更新')
        viewMenu = mainMenu.addMenu('设置')

        self.main_layout.setMenuBar(mainMenu)

    def loading_QObject(self):  # loading动画
        self.loading_view = QGraphicsView()  # 创建视图
        self.loading_view.setStyleSheet("background-color:rgba(239,228,176,{});".format(255 * 0.5))  # 调节透明度
        self.loading_view.setParent(self)  # 将主窗设置成视图的父控件
        self.loading_view.show()
        self.loading_view.setFixedSize(self.width(), self.height())
        self.loading_scene = QGraphicsScene()  # 创建场景
        self.loading_view.setScene(self.loading_scene)  # 视图设置场景
        self.loading_animation_QObject = loading_animation_QObject()  # 实例化loading动画类
        self.loading_scene.addItem(self.loading_animation_QObject.pixmap_item)  # 将loading动画作为图元加入到场景内
        self.loading_animation_QObject.animation.start()  # loading动画启动。


class App_Exec():
    """ 功能函数 """

    def update_right_widget(self, sender):  # 根据发射源显示不同的widget页面。
        for layout_index in range(self.MainUi.right_layout.count()):  # 每将显示新的Widget页面时，需要对之前创建的布局进行清除操作。
            self.MainUi.right_layout.itemAt(layout_index).widget().deleteLater()  # 清除之前布局
        print(sender.y())

        if sender.text() == '文件转换':
            self.DocumentConvert_QWidget()

        elif sender.text() == '图像处理':
            self.ImageProcess_QWidget()

        elif sender.text() == '数据绘图':
            self.DataVisualization_QWidget()


        ### TODO: 展示信息
        elif sender.text() == '建议与反馈':
            text_content = u" 软件更新及使用请关注微信公众号【paperClub】，交流及建议微信: any1one。"
            feedback_text = QTextEdit(text_content)
            self.MainUi.right_layout.addWidget(feedback_text)

        elif sender.text() == '软件与版本':

            text_content = " paperBox免费开源软件(源码在微信公众号 paperClub 获取)，旨在为大家提高一下常用的小工具。"
            
            self.tools_vision_text = QTextEdit(text_content)

            self.MainUi.right_layout.addWidget(self.tools_vision_text)  #### 按钮可见


    def DocumentConvert_QWidget(self):
        ################# 文件转换函数

        docConvert_id_dict = {
            "请选择": -1,
            "pdf文件转图片": 0,
            "pdf提取页面图片": 1,
            "pdf转word": 2,
            "pdf转excel": 3,
            "pdf转网页": 4,
        }

        self.MainUi.right_layout.addWidget(self.show_widget(docmentconvert_menus))  #### 按钮可见
        self.__layout_0 = QHBoxLayout()
        self.__layout_1 = QHBoxLayout()
        self.__layout_2 = QHBoxLayout()

        """  右侧菜单栏： 文件转换 --> pdf转换 """
        
        self.text_dropdown0 = QtWidgets.QComboBox()
        self.text_dropdown0.addItems(list(docConvert_id_dict.keys()))
        self.QLabel_file_path0 = QLabel('打开文件：')
        self.QLineEdit_file_path0 = QLineEdit()
        self.QWidget_mergePDF = QWidget_mergePDF(self.QWidget_for_QTabWidget[docmentconvert_menus[0]])

        self.QPushButton_file_path0 = QPushButton('浏览')
        self.QPushButton_file_Submit0 = QPushButton('执行')

        self.__layout_0.addWidget(self.text_dropdown0, 1)
        self.__layout_0.addWidget(self.QLabel_file_path0, 1)
        self.__layout_0.addWidget(self.QLineEdit_file_path0, 5)
        self.__layout_0.addWidget(self.QPushButton_file_path0, 1)
        self.__layout_0.addWidget(self.QPushButton_file_Submit0, 1)
        self.QWidget_for_QTabWidget_layout[docmentconvert_menus[0]].addLayout(self.__layout_0)  #### 第一个按钮
        self.QWidget_for_QTabWidget_layout[docmentconvert_menus[0]].addStretch()
        self.text_dropdown0.currentTextChanged.connect(self.doc_leftButton0_stat)
        self.QPushButton_file_path0.clicked.connect(
            lambda: self.getFileDialogValue(self.QLineEdit_file_path0, '请选择PDF文件。', '*.pdf'))
        self.QPushButton_file_Submit0.clicked.connect(
            lambda: self.exec_DocConvert(docConvert_id_dict.get(self.text_dropdown0.currentText()),
                                         self.QLineEdit_file_path0.text()))

        """ 右侧菜单栏： 文件转换 --> pdf拆分 """
        docsExtract_id_dict = {
            " 请选择 ": -1,
            "删除pdf奇数页面": 0,
            "删除pdf偶数页面": 1,
            "删除pdf指定页面": 2,
            "生成指定页面pdf": 3,
            "生成指定页数pdf": 4,
        }

        self.QLabel_file_path1 = QLabel('打开文件：')
        self.QLineEdit_file_path1 = QLineEdit()
        """ 增加选项框"""
        self.QLineEdit_order1 = QRegExp_QLineEdit()  ### 页码设置
        self.QLineEdit_order1.hide()

        self.QLineEdit_file_path1.setReadOnly(True)
        self.QPushButton_file_path1 = QPushButton('浏览')
        self.QPushButton_file_Submit1 = QPushButton('执行')
        self.text_dropdown1 = QtWidgets.QComboBox()
        self.text_dropdown1.addItems(list(docsExtract_id_dict.keys()))

        self.__layout_1.addWidget(self.text_dropdown1, 1)
        self.__layout_1.addWidget(self.QLineEdit_order1, 1)  ##增加页码设置区域
        self.__layout_1.addWidget(self.QLabel_file_path1, 1)
        self.__layout_1.addWidget(self.QLineEdit_file_path1, 5)
        self.__layout_1.addWidget(self.QPushButton_file_path1, 1)
        self.__layout_1.addWidget(self.QPushButton_file_Submit1, 1)
        self.QWidget_for_QTabWidget_layout[docmentconvert_menus[1]].addLayout(self.__layout_1)  ## 第二个按钮： 提取分拆
        self.QWidget_for_QTabWidget_layout[docmentconvert_menus[1]].addStretch()
        self.text_dropdown1.currentTextChanged.connect(self.doc_leftButton1_stat)
        self.QPushButton_file_path1.clicked.connect(
            lambda: self.getFileDialogValue(self.QLineEdit_file_path1, '请选择文件', '*.pdf'))
        self.QPushButton_file_Submit1.clicked.connect(
            lambda: self.exec_DocExtract(docsExtract_id_dict.get(self.text_dropdown1.currentText()),
                                         self.QLineEdit_file_path1.text()))

        self.QWidget_for_QTabWidget_layout[docmentconvert_menus[1]].addLayout(self.__layout_1)  #### 第2个按钮
        self.QWidget_for_QTabWidget_layout[docmentconvert_menus[1]].addStretch()

        """ 右侧菜单栏： 文件转换 ——> pdf合并"""
        docProcess_id_dict = {
            " 请选择 ": -1,
            "pdf合并": 0,
        }

        self.text_dropdown2 = QtWidgets.QComboBox()
        self.text_dropdown2.addItems(list(docProcess_id_dict.keys()))
        self.QLabel_file_path2 = QLabel('打开文件：')
        self.QLineEdit_file_path2 = QLineEdit()

        self.QWidget_mergePDF = QWidget_mergePDF(self.QWidget_for_QTabWidget[docmentconvert_menus[2]])

        self.QPushButton_file_path2 = QPushButton('浏览')
        self.QPushButton_file_Submit2 = QPushButton('执行')
        self.__layout_2.addWidget(self.text_dropdown2, 1)
        self.__layout_2.addWidget(self.QLabel_file_path2, 1)
        self.__layout_2.addWidget(self.QLineEdit_file_path2, 5)
        self.__layout_2.addWidget(self.QPushButton_file_path2, 1)
        self.__layout_2.addWidget(self.QPushButton_file_Submit2, 1)
        self.QWidget_for_QTabWidget_layout[docmentconvert_menus[2]].addLayout(self.__layout_2)  #### 第一个按钮
        self.QWidget_for_QTabWidget_layout[docmentconvert_menus[2]].addStretch()
        self.text_dropdown2.currentTextChanged.connect(self.doc_leftButton2_stat)
        self.QPushButton_file_path2.clicked.connect(
            lambda: self.getFileDialogValue(self.QLineEdit_file_path2, '请选择PDF文件。', '*.pdf'))
        self.QPushButton_file_Submit2.clicked.connect(
            lambda: self.exec_DocProcess(docProcess_id_dict.get(self.text_dropdown2.currentText()),
                                         self.QLineEdit_file_path2.text()))
        self.QWidget_mergePDF.browse_clicked_signal.connect(
            lambda sender: self.getFileDialogValue(self.QLineEdit_file_path2, '请选择PDF文件。', '*.pdf', sender=sender))

    def exec_pdf_page_del(self):
        '''
		当条件满足时，对图片进行ocr提取。
		:return:
		'''
        if len(self.QLineEdit_file_path2.text()) <= 0:
            self.QMessageBox_info('文件路径不正确。')
        else:
            if self.text_dropdown2.currentIndex() == 0:  # ocr
                self.QMessageBox_info('未整改')

    def doc_leftButton0_stat(self):
        '''
		对pdf文本处理页面的下拉框文本变换做页面变换处理。增加或减少控件显示。
		:return:
		'''
        pass



    def doc_leftButton1_stat(self):
        """ 控制： 文件提取拆分 菜单栏 部分隐藏按钮"""
        self.QLineEdit_order1.hide()
        if self.text_dropdown1.currentText() == '生成指定页面pdf':
            self.QLineEdit_order1.show()

        elif self.text_dropdown1.currentText() == '生成指定页数pdf':
            self.QLineEdit_order1.show()

        elif self.text_dropdown1.currentText() == '删除pdf指定页面':
            self.QLineEdit_order1.show()

        elif self.text_dropdown1.currentText() == '生成指定页数pdf':
            self.QLineEdit_order1.show()

    def doc_leftButton2_stat(self):

        self.QWidget_mergePDF.hide()

        if self.text_dropdown2.currentText() == 'pdf合并':
            self.QWidget_mergePDF.show()

    def getFileDialogValue(self, obj, text, type_text, sender=None):
        '''
		用于打开一个窗口，让用户选择文件，从而获取路径。
		:param obj: 获取此参数主体的目的，获取路径后，直接对主体文本进行修改，当前主体为QLineEdit控件。
		:param text:窗口问候语，可根据情况自行改写。
		:param type_text: 样式文本，用于锁定扩展名格式。
		:param sender: 非必要参数，当有参数值传入时，此参数优先于obj参数。
		:return:
		'''
        get_text = self.openQFileDialog(text, type_text)
        if sender is None:
            obj.setText(get_text)
        else:
            # try:
            self.QWidget_mergePDF.get_QLineEditObj_for_sender(sender).setText(get_text)

    # except Exception as err:
    #     self.QMessageBox_info('未能获取到文件地址。'+str(err))

    def QMessageBox_info(self, text):
        QMessageBox.information(self.MainUi, '提示', text, QMessageBox.Ok)

    def format_page_extend(self, str_):
        '''
		:为提高代码可读性，对forma_page函数的一个补充
		:param str_:
		:return:
		'''
        try:
            item = str_.split('-')
            print(472, item)
            str_n = []
            for i in range(int(item[0]), int(item[1]) + 1):
                str_n.append(str(i))
            return str_n
        except Exception as err:
            print(477, err)
            return []

    def format_page(self, page_list_str):
        '''
		:用于将页码如：字符串1,2,4-7 转换成一个为[1,2,4,5,6,7]列表。
		:param page_list_str:
		:return:空列表或格式成功转换列表，可判断，当返回空列表时，用户输入的格式不正确。
		'''
        page_list_str = page_list_str.replace('，', ',')
        new_page_list_str = []
        try:
            if ',' in page_list_str:  #
                str_douhao_list = page_list_str.split(',')
                for item0 in str_douhao_list:
                    if '-' in item0:
                        page_list_str = self.format_page_extend(item0)
                        for i in page_list_str:
                            new_page_list_str.append(i)
                    else:
                        new_page_list_str.append(item0)
                return new_page_list_str
            elif '-' in page_list_str:
                return self.format_page_extend(page_list_str)
            else:
                try:
                    if page_list_str.isdigit():
                        new_page_list_str.append(str(page_list_str))
                        return new_page_list_str
                    else:
                        return new_page_list_str
                except:
                    return new_page_list_str
        except Exception as err:
            return new_page_list_str

    def exec_DocConvert(self, pdf_text_id, pdf_path):
        """ 文件格式转换 """

        if len(pdf_path) != 0 and pdf_text_id >= 0:
            if pdf_text_id == 0:  #### pdf文件转图片
                self.MainUi.loading_QObject()
                self.QThread_pdf2img = QThread_pdf2img(pdf_path)
                self.QThread_pdf2img.start()
                self.QThread_pdf2img.finished.connect(self.loading_stop)

            elif pdf_text_id == 1:  #### pdf提取页面图片：
                # mytools_text._pdf_image_extract(pdffile=pdf_path)
                # 多线程
                self.MainUi.loading_QObject()
                self.QThread_pdfextract_img = QThread_pdfextract_img(pdf_path)
                self.QThread_pdfextract_img.start()
                self.QThread_pdfextract_img.finished.connect(self.loading_stop)


            elif pdf_text_id == 2:  ####pdf转word

                try:
                    out_dir = OUT_DIR
                    save_word = os.path.join( out_dir, os.path.splitext(os.path.basename(pdf_path))[0] + ".docx")
                    self.MainUi.loading_QObject()
                    self.QThread_pdf2word = QThread_pdf2word(pdf_path, save_word)
                    self.QThread_pdf2word.start()
                    self.QThread_pdf2word.finished.connect(self.loading_stop)

                except Exception as err:
                    self.QMessageBox_info(' 参数错误 ')


            elif pdf_text_id == 3:  #### pdf转excel:
                # self.QMessageBox_info('功能开发中 ... ')
                save_dir = OUT_DIR
                try:
                    mytools_text._pdf_to_excel(pdf_path, save_dir)
                    self.QMessageBox_info('pdf转excel成功。')
                except Exception as error:
                    print(error)

            elif pdf_text_id == 4:  #####  pdf转网页
                save_html = os.path.join(OUT_DIR, os.path.splitext(os.path.basename(pdf_path))[0] + ".html")
                try:
                    mytools_text._pdf_to_html(pdf_path, html_path=save_html)
                    self.QMessageBox_info('pdf转html成功。')
                except Exception as error:
                    print(error)

    def exec_DocExtract(self, tool_id, file_path):
        """ 文件拆分与内容提取 """
        if len(file_path) > 0 and tool_id >= 0:
            if tool_id == 0:  ### 删除pdf奇数页面
                try:
                    mytools_text._delete_pdf_ODDpages(file_path)
                    self.QMessageBox_info('pdf页面删除成功。')
                except Exception as error:
                    print(error)

            elif tool_id == 1:  ### 删除pdf偶数页面
                try:
                    mytools_text._delete_pdf_Eventpages(file_path)
                    self.QMessageBox_info('pdf页面删除成功。')
                except Exception as error:
                    print(error)

            elif tool_id == 2:  ### 删除pdf指定页面
                try:
                    page_list = self.format_page(self.QLineEdit_order1.text())
                    page_list = list(map(int, page_list))
                    page_list = [i - 1 for i in page_list]
                    mytools_text._pdf_page_delete(pdffile=file_path, delete_pages=page_list, output_dir=OUT_DIR)
                    self.QMessageBox_info('pdf页面删除成功。')
                except Exception as error:
                    print(error)

            elif tool_id == 3:  ### 生成指定页面pdf
                page_list = self.format_page(self.QLineEdit_order1.text())
                page_list = list(map(int, page_list))
                page_list.sort()
                if len(page_list) <= 0:
                    self.QMessageBox_info('页码设置格式不正确。')
                else:
                    mytools_text._pdf_page_extract(file_path, page_list)
                    self.QMessageBox_info('文件拆分成功。')

            elif tool_id == 4:  ### 生成指定页数pdf
                page_list = self.format_page(self.QLineEdit_order1.text())
                page_list = list(map(int, page_list))
                page_list.sort()
                if len(page_list) <= 0:
                    self.QMessageBox_info('pdf文件分割页码设置错误')
                else:
                    mytools_text._pdf_page_segment(file_path, page_gap=page_list[0])
                    self.QMessageBox_info('pdf分割。')

    def exec_DocProcess(self, tool_id, file_path):
        """ 文件处理与合并 """
        if len(file_path) > 0 and tool_id >= 0:

            if tool_id == 0:  # pdf合并
                pdffileList = self.QWidget_mergePDF.get_QLineEdit_Text_for_filepath()
                pdffileList.insert(0, file_path)
                savefile = os.path.join(OUT_DIR, os.path.basename(pdffileList[0]))
                mytools_text._pdf_merger(pdffileList, savefile)
                self.QMessageBox_info('文件合并成功。')



    ############################ 图像处理
    def ImageProcess_QWidget(self):
        ################# 图像转换及缩放函数
        imgTransform_id_dict = {
            "请选择": -1,
            "图像等比缩放": 0,
            "固定边长等比缩放": 1,
            "图像压缩": 2,
        }


        self.MainUi.right_layout.addWidget(self.show_widget(imageprocess_menus))  #### 按钮可见
        self.__layout_img_0 = QHBoxLayout()
        self.__layout_img_1 = QHBoxLayout()


        ########################  图像转化与缩放
        self.QLabel_imgfile_path0 = QLabel('打开文件：')
        self.QLineEdit_image_file_path0 = QLineEdit()
        self.QLineEdit_img_order0_0 = QRegExp_QLineEdit2(name="缩放倍数", tip_str='0.5') ### 缩放因子
        self.QLineEdit_img_order0_1 = QRegExp_QLineEdit2(name="宽", tip_str="200")  ### 宽设置
        self.QLineEdit_img_order0_2 = QRegExp_QLineEdit2(name="高", tip_str="300")  ### 高设置
        self.QLineEdit_img_order0_3 = QRegExp_QLineEdit2(name="压缩至(kb)", tip_str="20.5") ### 压缩至 x kb
        self.QLineEdit_img_order0_0.hide()
        self.QLineEdit_img_order0_1.hide()
        self.QLineEdit_img_order0_2.hide()
        self.QLineEdit_img_order0_3.hide()

        self.QLineEdit_image_file_path0.setReadOnly(True)
        self.QPushButton_imgfile_path0 = QPushButton('浏览')
        self.QPushButton_imgfile_Submit0 = QPushButton('执行')
        self.image_dropdown0 = QtWidgets.QComboBox()
        self.image_dropdown0.addItems(list(imgTransform_id_dict.keys()))

        self.__layout_img_0.addWidget(self.image_dropdown0, 1)
        self.__layout_img_0.addWidget(self.QLineEdit_img_order0_0, 1)
        self.__layout_img_0.addWidget(self.QLineEdit_img_order0_1, 1)
        self.__layout_img_0.addWidget(self.QLineEdit_img_order0_2, 1)
        self.__layout_img_0.addWidget(self.QLineEdit_img_order0_3, 1)

        self.__layout_img_0.addWidget(self.QLabel_imgfile_path0, 1)
        self.__layout_img_0.addWidget(self.QLineEdit_image_file_path0, 5)
        self.__layout_img_0.addWidget(self.QPushButton_imgfile_path0, 1)
        self.__layout_img_0.addWidget(self.QPushButton_imgfile_Submit0, 1)
        self.QWidget_for_QTabWidget_layout[imageprocess_menus[0]].addLayout(self.__layout_img_0)  #### 第1个按钮
        self.QWidget_for_QTabWidget_layout[imageprocess_menus[0]].addStretch()
        self.image_dropdown0.currentTextChanged.connect(self.img_leftButton0_stat)
        self.QPushButton_imgfile_path0.clicked.connect(
            lambda: self.getFileDialogValue(self.QLineEdit_image_file_path0, '选择图片', '*.jpg;*.png;*.bmp'))
        self.QPushButton_imgfile_Submit0.clicked.connect(
            lambda: self.exec_ImgTransform(imgTransform_id_dict.get(self.image_dropdown0.currentText()),
                                           self.QLineEdit_image_file_path0.text()))
        self.QWidget_for_QTabWidget_layout[imageprocess_menus[0]].addLayout(self.__layout_img_0)
        self.QWidget_for_QTabWidget_layout[imageprocess_menus[0]].addStretch()




        ############################ 图像处理
        imgProcess_id_dict = {
            "请选择": -1,
            "彩图转灰色": 0,


        }
        self.image_dropdown1 = QtWidgets.QComboBox()
        self.image_dropdown1.addItems(list(imgProcess_id_dict.keys()))
        self.QLabel_file_path1 = QLabel('打开文件：')
        self.QLineEdit_image_file_path1 = QLineEdit()
        self.QPushButton_imgfile_path1 = QPushButton('浏览')
        self.QPushButton_imgfile_Submit1 = QPushButton('执行')


        self.__layout_img_1.addWidget(self.image_dropdown1)
        self.__layout_img_1.addWidget(self.QLabel_file_path1, 2)
        self.__layout_img_1.addWidget(self.QLineEdit_image_file_path1, 6)
        self.__layout_img_1.addWidget(self.QPushButton_imgfile_path1, 2)
        self.__layout_img_1.addWidget(self.QPushButton_imgfile_Submit1, 1)
        self.QWidget_for_QTabWidget_layout[imageprocess_menus[1]].addLayout(self.__layout_img_1)  #### 第2个按钮
        self.QWidget_for_QTabWidget_layout[imageprocess_menus[1]].addStretch()

        self.QPushButton_imgfile_path1.clicked.connect(
            lambda: self.getFileDialogValue(self.QLineEdit_image_file_path1, '选择图片', '*.jpg;*.png;*.bmp'))

        self.QPushButton_imgfile_Submit1.clicked.connect(
            lambda: self.exec_ImgProcess(imgProcess_id_dict.get(self.image_dropdown1.currentText()),
                                         self.QLineEdit_image_file_path1.text()))





    #### 图像转换与缩放

    def exec_ImgTransform(self, img_tool_id, file_path, out_dir=OUT_DIR):
        """ 图像转换缩放"""

        if len(file_path) !=0 and img_tool_id >=0:
            if img_tool_id == 0: # 图像等比缩放
                try:
                    resize_factor =  float(self.QLineEdit_img_order0_0.text())
                    save_file = os.path.join(out_dir, os.path.basename(file_path))
                    mytools_image._image_auto_resize(file_path, save_file, resize_factor)
                    self.QMessageBox_info(' 缩放处理完成。 ')
                except Exception as err:
                    self.QMessageBox_info(' 请检查输入输入参数！ ')
                    print(err)

            elif img_tool_id == 1: # 固定边长等比缩放
                resize_width = self.QLineEdit_img_order0_1.text()
                resize_hight = self.QLineEdit_img_order0_2.text()

                try:
                    resize_width = float(resize_width) if len(resize_width) > 0 else 0
                    resize_hight = float(resize_hight) if len(resize_hight) > 0 else 0
                    print(f"宽：{resize_width}, 高：{resize_hight}")

                    if resize_hight + resize_width > 0:
                        lenType = 5
                        if resize_width > 0 and resize_hight > 0:
                            lenType = 5
                        elif resize_width > 0 and resize_hight ==0:
                            lenType = 1
                        elif resize_width ==0 and resize_hight > 0:
                            lenType = 0

                        save_file = os.path.join(out_dir, os.path.basename(file_path))
                        mytools_image._image_resized(file_path, save_file, resize_width, resize_hight, lenType)
                        self.QMessageBox_info(' 处理完成。 ')

                except Exception as err:
                    self.QMessageBox_info(' 请检查输入输入参数！ ')
                    print(err)


            elif img_tool_id == 2:  # 图像压缩
                save_file = os.path.join(out_dir, os.path.basename(file_path))
                compress_factor = self.QLineEdit_img_order0_3.text()
                if len(compress_factor) > 0:
                    try:
                        compress_factor = float(compress_factor)
                        if compress_factor > 0:
                            mytools_image._image_compressed(compressType=1, imgPath=file_path, \
                                                            savefile = save_file, target_size= compress_factor)

                            self.QMessageBox_info(' 处理完成。 ')
                        else:
                            self.QMessageBox_info(' 目标大小必须大于 0 kb ')
                    except Exception as error:
                        self.QMessageBox_info(' 请检查输入输入参数！ ')
                        print(error)



    def exec_ImgProcess(self, img_tool_id, file_path, out_dir=OUT_DIR):
        """ 图像处理 """

        if len(file_path) !=0 and img_tool_id >=0:

            if img_tool_id == 0 : # 彩图转灰色
                save_file = os.path.join(out_dir, os.path.basename(file_path))
                try:
                    mytools_image._imgColorConvert(img_path= file_path, save_path=save_file, convert_id= img_tool_id)
                    self.QMessageBox_info(' 处理完成。 ')

                except Exception as error:
                    self.QMessageBox_info(' 请检查输入输入参数！ ')
                    print(error)

            if img_tool_id == 1:
                pass



    def img_leftButton0_stat(self):
        """ 控制图像缩放 /  固定宽高等比缩放 / 因子输入框显示 """
        self.QLineEdit_img_order0_0.hide()
        self.QLineEdit_img_order0_1.hide()
        self.QLineEdit_img_order0_2.hide()
        self.QLineEdit_img_order0_3.hide()

        if self.image_dropdown0.currentText() == '图像等比缩放':
            self.QLineEdit_img_order0_0.show()

        elif self.image_dropdown0.currentText() == '固定边长等比缩放':
            self.QLineEdit_img_order0_1.show()
            self.QLineEdit_img_order0_2.show()

        elif self.image_dropdown0.currentText() == '图像压缩':
            self.QLineEdit_img_order0_3.show()





    ############################ 数据绘图
    def DataVisualization_QWidget(self):
        ################# 绘图函数
        dataVisual_com_id_dict = {
            "请选择": -1,
            "柱状图": 0,
            "直方图": 1,
            "直线图": 2,
            "散点图": 3, }


        ########## 数据绘图 -- 常规绘图

        self.MainUi.right_layout.addWidget(self.show_widget(data_visualization_menus))  #### 数据绘图，按钮可见
        self.__layout_plot_0 = QHBoxLayout()  ##### 常用绘图

        self.QLabel_data_file_path0 = QLabel('打开文件：')
        self.QLineEdit_data_file_path0 = QLineEdit()
        self.QPushButton_data_file_path0 = QPushButton('浏览')
        self.QPushButton_datafile_Submit0 = QPushButton('执行')
        self.plot_dropdown0 = QtWidgets.QComboBox()
        self.plot_dropdown0.addItems(list(dataVisual_com_id_dict.keys()))
        self.__layout_plot_0.addWidget(self.plot_dropdown0)


        self.__layout_plot_0.addWidget(self.QLabel_data_file_path0, 2)
        self.__layout_plot_0.addWidget(self.QLineEdit_data_file_path0, 5)
        self.__layout_plot_0.addWidget(self.QPushButton_data_file_path0, 1)
        self.__layout_plot_0.addWidget(self.QPushButton_datafile_Submit0, 1)
        self.QWidget_for_QTabWidget_layout[data_visualization_menus[0]].addLayout(self.__layout_plot_0)  #### 第一个按钮
        self.QWidget_for_QTabWidget_layout[data_visualization_menus[0]].addStretch()


        self.QPushButton_data_file_path0.clicked.connect(
            lambda: self.getFileDialogValue(self.QLineEdit_data_file_path0, "请选择要添加的文件", "Text Files (*.txt)"))
        self.QPushButton_datafile_Submit0.clicked.connect(
            lambda: self.exec_DataVisual(dataVisual_com_id_dict.get(self.plot_dropdown0.currentText()),
                                         self.QLineEdit_data_file_path0.text()))




    def update_canvas(self, menu_name = '常规绘图'):
        """ 画布更新 """
        try:
            for item_index in range(1,self.QWidget_for_QTabWidget_layout[menu_name].count()):
                try:
                    self.QWidget_for_QTabWidget_layout[menu_name].itemAt(item_index).widget().deleteLater()
                except:
                    pass
        except Exception as error:
            print("画布更新出错: ", error)

    def exec_DataVisual(self, plot_id, file_path):  ####### 常用图绘制

        """常规绘图函数 """
        self.update_canvas(data_visualization_menus[0])

        ################# 常用绘图,
        self.QWidget_for_QTabWidget_layout[data_visualization_menus[0]].addWidget(mytools_plot.commonlyUsedPlot(file_path, plot_id= plot_id))



    def openQFileDialog(self, text, type_str):
        QFileDialog_expFile = QFileDialog()
        file_path = QFileDialog_expFile.getOpenFileName(self.MainUi, text, "//",
                                                        f"{type_str[type_str.find('.') + 1:].upper()} 格式文件({type_str})")
        return file_path[0]

    def loading_stop(self):
        self.MainUi.loading_view.hide()
        self.QMessageBox_info('文件转换成功。')

    def show_widget(self, item_list):
        __QTabWidget_item = QTabWidget()
        self.QWidget_for_QTabWidget = {}
        self.QWidget_for_QTabWidget_layout = {}
        for item in item_list:
            self.QWidget_for_QTabWidget[item] = QWidget()
            self.QWidget_for_QTabWidget_layout[item] = QVBoxLayout()
            self.QWidget_for_QTabWidget[item].setLayout(self.QWidget_for_QTabWidget_layout[item])
            __QTabWidget_item.addTab(self.QWidget_for_QTabWidget[item], item)
        return __QTabWidget_item

    def btn_clicked(self):  # 利用sender方法获得信号的发射源。
        sender = self.MainUi.sender()
        self.update_right_widget(sender)

    def signal_connect(self):  # 信号和槽
        for item in self.MainUi.control_QPushButton_dict:  # 创建批量信号和槽
            self.MainUi.control_QPushButton_dict[item].clicked.connect(self.btn_clicked)

    # 当右边的按钮被按下时
    def right_buttonclicked(self, str):
        '''
		:param str:传来的子按钮的名字
		:return:
		'''

        self.MainUi.buttonwidget.setVisible(False)
        name = str  # 获取按钮名字

    # 试例 根据按钮名字响应窗口

    def main(self):
        self.app = QApplication(sys.argv)
        self.MainUi = Main_Ui()
        # self.MainUi.buttonwidget.present_button.connect(self.right_buttonclicked)
        self.MainUi.setWindowTitle("paperBox")
        self.MainUi.show()
        self.signal_connect()
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    AppExec = App_Exec()
    AppExec.main()
