import sys
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi


class Main_Window(QMainWindow):
    def __init__(self, parent=None):
        super(Main_Window, self).__init__(parent)
        loadUi('main.ui', self)
    def menubar_slot(self,action):
        QMessageBox.information(self,'目录事件',action.text())

    def pushbutton_slot1(self):
        QMessageBox.information(self,'提示','信号已经触发，执行以下操作。')
        QMessageBox.information(self,'执行','文本框1={}，文本框2={}，文本框3={}，文本框4={}，'
                                .format(self.lineEdit_2.text(),
                                        self.lineEdit_3.text(),
                                        self.lineEdit_4.text(),
                                        self.lineEdit_5.text())
                                )
        QMessageBox.information(self,'操作','操作执行完毕。')

app = QApplication(sys.argv)
w = Main_Window()
w.show()

sys.exit(app.exec())