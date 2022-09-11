import sys
from PyQt5.Qt import *

class QPushButton(QPushButton):#重写QPushButton
    def __init__(self,text):
        super(QPushButton, self).__init__()
        self.setText(text)
        self.setFixedWidth(200)

class Main_Ui(QWidget):
    def __init__(self):
        super(Main_Ui, self).__init__()
        self.setWindowTitle('关于QMessageBox提示框的Demo')
        self.resize(800,500)
        self.setupUi()

    def setupUi(self):
        self.layout_main = QVBoxLayout()

        self.btn_tips = QPushButton('弹出一个提示框')
        self.btn_question = QPushButton('弹出一个问询框')
        self.btn_warning = QPushButton('弹出一个警告框')


        self.layout_main.addWidget(self.btn_tips,alignment=Qt.AlignCenter)
        self.layout_main.addWidget(self.btn_question,alignment=Qt.AlignCenter)
        self.layout_main.addWidget(self.btn_warning,alignment=Qt.AlignCenter)

        self.setLayout(self.layout_main)

class App_Exec():
    def QMessageBox_custom_tips(self):#正常可以对QMessageBox进行封装。此外写了个简易写法。
        QMessageBox.information(self.MainUi, '提示','这是一个提示框',QMessageBox.Ok)
    def QMessageBox_custom_question(self):
        reply = QMessageBox.question(self.MainUi,'询问','叫你一声者行孙你敢答应吗？',QMessageBox.Yes|QMessageBox.No)
        return reply
    def QMessageBox_custom_warning(self):
        QMessageBox.warning(self.MainUi,'警告','此骚操作不合法!',QMessageBox.Ok)

    def signal_connect(self):
        self.MainUi.btn_tips.clicked.connect(self.QMessageBox_custom_tips)
        self.MainUi.btn_question.clicked.connect(self.QMessageBox_custom_question)
        self.MainUi.btn_warning.clicked.connect(self.QMessageBox_custom_warning)
    def begin(self):
        self.app = QApplication(sys.argv)
        self.MainUi = Main_Ui()
        self.MainUi.show()
        self.signal_connect()
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    AppExec = App_Exec()
    AppExec.begin()
