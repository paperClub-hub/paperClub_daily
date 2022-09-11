from PyQt5.Qt import * # 此处为了实例方便使用*,实际项目推荐具体到某个类名。
import sys


class Main_WindowUI(QWidget):#主窗UI类
    def __init__(self):
        super(Main_WindowUI, self).__init__()
        self.setupUi()
    def setupUi(self):
        self.setWindowTitle('主窗点击按钮打开子窗')
        self.resize(800,400)
        self.layout_main = QVBoxLayout() # 创建窗体底层垂直总局
        self.layout_main.setAlignment(Qt.AlignCenter) # 使总局中的控件居中
        self.setLayout(self.layout_main)
        self.QPushButton_openchildwindowUI = QPushButton('点击按钮打开子窗')
        self.QPushButton_openchildwindowUI.setFixedWidth(100)

        self.layout_main.addWidget(self.QPushButton_openchildwindowUI)
class Child_WindowUI(QWidget):#子窗UI类
    def __init__(self,width = 400,height = 200):#这里写了两个接收的，赋值了默认值，即使实例化不传递参数进来，也不会报错
        super(Child_WindowUI, self).__init__()
        self.width = width
        self.height = height
        self.setupUi()
    def setupUi(self):
        self.resize(self.width,self.height)
        self.layout_main = QVBoxLayout()
        self.layout_main.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout_main)

        self.QLabel_Tip = QLabel('子窗已经打开')
        self.layout_main.addWidget(self.QLabel_Tip)
class App_Exec():
    def begin(self):
        self.app = QApplication(sys.argv)
        self.MainWindowUI = Main_WindowUI()
        self.ChildWindowUI = Child_WindowUI(self.MainWindowUI.width()//2,self.MainWindowUI.height()//2) # 参数是大窗口宽和高的一半大小。
        # 此处已经实例化了子窗，但没有show()出来，待满足条件后，再进行show()方法操作。
        self.MainWindowUI.show()
        self.MainWindowUI.QPushButton_openchildwindowUI.clicked.connect(self.ChildWindowUI.show)
        # 等效于上句 self.MainWindowUI.QPushButton_openchildwindowUI.clicked.connect( lambda: self.ChildWindowUI.show() )
        # lambda（匿名函数），一般用于函数体只有一条语句，或需要赋值参数时使用。
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    AppExec = App_Exec()
    AppExec.begin()
        