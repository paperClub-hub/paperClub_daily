from PyQt5.Qt import *
import sys

class Main_Ui(QWidget):
    def __init__(self):
        super(Main_Ui, self).__init__()
        self.setupUi()
    def setupUi(self):
        self.setWindowTitle('打开文件获取路径实例')
        self.resize(800, 300)
        self.layout_main = QHBoxLayout()  # 创建水平布局
        self.setLayout(self.layout_main)  # 窗体设置底层总局

        self.QLineEdit_filepath = QLineEdit()
        self.QLineEdit_filepath.setReadOnly(True) # 控件设置为只读

        self.QPushButton_openfile = QPushButton('打开文件')
        # 向总局中增加控件，后面跟的数字，为各控件的宽度占比。
        self.layout_main.addWidget(self.QLineEdit_filepath,8)  # 向部局中增加标签控件
        self.layout_main.addWidget(self.QPushButton_openfile,2)  # 向部局中增加按钮控件
    def QFileDialog_exp_file(self):
        self.QFileDialog_expFile = QFileDialog(self)  # 打开文件控件
        file_path = self.QFileDialog_expFile.getOpenFileName(None, "请选择要添加的文件", "//", "Text Files (*.xlsx;*.xls)")
        print(file_path)
        # file_path 变量获得的是一个元组
        # 括号里可以修改扩展名。
        if file_path [0]:
            # 将得到的路径文本增加点单行文本框中
            self.QLineEdit_filepath.setText(file_path [0])
            # 弹出消息对话框
            QMessageBox.information(self, '提示', '已经获取到文件路径【{}】'.format(file_path [0]))

class app_exec():
    def begin(self):
        self.app = QApplication(sys.argv)
        self.MainUI = Main_Ui()
        self.MainUI.show()
        
        # 当按钮被点击执行机槽函数。
        self.MainUI.QPushButton_openfile.clicked.connect(self.MainUI.QFileDialog_exp_file)

        sys.exit(self.app.exec_())

if __name__ == '__main__':
    AppExec = app_exec()
    AppExec.begin()
