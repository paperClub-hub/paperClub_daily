from PyQt5.Qt import *
import sys

class Main_Ui(QWidget):
    def __init__(self):
        super(Main_Ui, self).__init__()
        self.QRadioButton_list = []# 创建一个用于存放单选控件的列表
        self.setupUi()
    def setupUi(self):
        self.setWindowTitle('快速定位QRadioButton已选')
        self.resize(400,600)
        self.QRadioButton_Group = QButtonGroup()# 创建一个单选控件组
        self.QRadioButton_layout_list = QVBoxLayout()
        self.QRadioButton_layout_list.setAlignment(Qt.AlignCenter)
        self.setLayout(self.QRadioButton_layout_list)
        for num in range(0,10):# 测试10个控件
            self.QRadioButton_list.append(QRadioButton())#将控件写入列表
            self.QRadioButton_list[num].setText(str(num))#设置单选文本
            self.QRadioButton_layout_list.addWidget(self.QRadioButton_list[num])#将控件写入部局
            self.QRadioButton_Group.addButton(self.QRadioButton_list[num],num)#将控件写入单选控件组

class App_Exec():
    def print_clicked(self,obj):
        print('选中的id为： ',self.MainUi.QRadioButton_Group.id(obj))
    def begin(self):
        self.app = QApplication(sys.argv)
        self.MainUi= Main_Ui()
        self.MainUi.show()
        self.MainUi.QRadioButton_Group.buttonClicked.connect(self.print_clicked)#将单选组内按钮被点击，执行槽函数。
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    AppExec = App_Exec()
    AppExec.begin()