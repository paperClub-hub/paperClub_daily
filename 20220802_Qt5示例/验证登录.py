from PyQt5.Qt import *
import sys
# 此程序登录框验证
class Login_UI(QWidget):#登录窗口
    def __init__(self):
        super(Login_UI, self).__init__()
        self.setupUi()
    def setupUi(self):
        self.setWindowTitle('登录【用户名：123，密码123】')
        self.resize(500,300)
        self.layout_V = QVBoxLayout()
        self.layout_node = {}
        self.setLayout(self.layout_V)

        self.form_dict= {}
        # 采用字典当作表单的变量集合
        self.form_dict['username'] = {'标签':QLabel('用户名：'),'文本框':QLineEdit()}
        self.form_dict['password'] = {'标签':QLabel('密  码：'),'文本框':QLineEdit()}
        self.form_dict['function_event'] = {'清空':QPushButton('清 空'),'登录':QPushButton('登 录')}
        # 设置单行文本框为密码框
        self.form_dict ['password']['文本框'].setEchoMode(QLineEdit.Password)
        # 遍历表单集合
        for row,value in enumerate(self.form_dict.values()):
            self.layout_node[row] = QHBoxLayout()
            self.layout_V.addLayout(self.layout_node[row])
            for col,value in enumerate(value.values()):
                self.layout_node [row].addWidget(value)
    def close_winodw(self):
        self.hide()

class Main_Window(QWidget):#主窗口
    islogin_signal = pyqtSignal()
    def __init__(self):
        super(Main_Window, self).__init__()
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle('登录成功')
        self.resize(800,600)
        self.Label = QLabel('登录成功，已进入到主窗口，关闭窗口，再次弹出登录框。',self)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.Label)
        self.setLayout(self.layout)
    def closeEvent(self,event):
        self.islogin_signal.emit()




class execute_app():# 逻辑类
    def isVerification(self):
        username = self.LoginUI.form_dict ['username']['文本框'].text()
        password = self.LoginUI.form_dict ['password'] ['文本框'].text()
        if username == '123' and password == '123':
            return True
        else:
            return False
    def relogin(self):
        self.LoginUI.form_dict ['username'] ['文本框'].setText("")
        self.LoginUI.form_dict ['password'] ['文本框'].setText("")
        self.LoginUI.show()
        self.MainWindow.hide()
    def login(self):
        if self.isVerification():
            self.LoginUI.close_winodw()
            self.MainWindow.show()
        else:
            QMessageBox.warning(self.LoginUI,'错误','用户名或密码错误')
    def clear_lineedit(self):
        self.LoginUI.form_dict ['username'] ['文本框'].setText('')
        self.LoginUI.form_dict ['password'] ['文本框'].setText('')
    def doing(self):
        self.app = QApplication(sys.argv)
        self.LoginUI = Login_UI()
        self.MainWindow = Main_Window()
        self.LoginUI.show()
        self.LoginUI.form_dict ['function_event'] ['清空'].clicked.connect(self.clear_lineedit)
        self.LoginUI.form_dict ['function_event'] ['登录'].clicked.connect(self.login)
        self.MainWindow.islogin_signal.connect(self.relogin)
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    execute = execute_app()
    execute.doing()