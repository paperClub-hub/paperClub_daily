import sys,sqlite3,random,time
from PyQt5.Qt import *


conn = sqlite3.connect('test.db')
cursor = conn.cursor()



class Main_Ui(QWidget):
    def __init__(self):
        super(Main_Ui, self).__init__()
        self.QTimer_insert = QTimer()
        self.QTimer_insert.start(0)
        self.QTimer_show = QTimer()
        self.setupUi()
    def insert_Data(self):
        name = "".join(random.sample([chr(i) for i in range(97, 123)], random.randint(5, 10)))
        # 26个英文字母，随机取5-10个，组成一个字符串
        age = random.randint(15, 30)
        # 年龄范围，15-30
        tel = "1{}".format(random.randint(1000000000, 9999999999))
        # 随机生成11位电话号码
        sql = "insert into test_table values(Null,'{name}',{age},'{tel}')".format(name=name, age=age, tel=tel)
        cursor.execute(sql)
        conn.commit()
    def closeEvent(self,event):
        # 当窗口程序关闭时，执行以下操作。
        self.QTimer_insert.stop()
        sql = "delete from test_table"
        # 清表SQL
        sql1 = "update sqlite_sequence set seq=0 where name='test_table';"
        # 重设自增ID，归零
        cursor.execute(sql)
        cursor.execute(sql1)
        conn.commit()
    def setupUi(self):
        self.resize(400,600)# 窗口尺寸
        self.__layout_main = QVBoxLayout()# 创建主布局为垂直布局
        self.setLayout(self.__layout_main)# 让窗口应用主布局
        self.QTableWidget_show= QTableWidget()# 创建一个表格控件对象

        self.__layout1 = QHBoxLayout()# 创建子布局1，此布局为水平布局
        self.__layout2 = QHBoxLayout()# 创建子布局2，此布局为水平布局
        self.QLabel_s = QLabel('刷新频率：')# 创建文本标签控件。
        self.QSpinBox_s = QSpinBox()#创建数值调节控件。
        self.QSpinBox_s.setValue(1)#设置初始值为1
        self.QSpinBox_s.setSingleStep(1)#设置调整步长为1
        self.QSpinBox_s.setRange(1,60)#设置调整范围为1至60秒
        self.QSpinBox_s.setToolTip('值范围（{}-{}）秒'.format(self.QSpinBox_s.minimum(),self.QSpinBox_s.maximum()))
        #设置控件说明提示。
        self.QTimer_show.start(int(self.QSpinBox_s.value())*1000)
        #让表格显示计时器启动。单位为毫秒
        self.__layout1.addWidget(self.QTableWidget_show)#向布局1添加表格控件。
        self.__layout2.addWidget(self.QLabel_s)#向布局2添加文本控件。
        self.__layout2.addWidget(self.QSpinBox_s)#向布局2添加数据调节控件。
        self.__layout2.addStretch()#布局弹簧

        self.__layout_main.addLayout(self.__layout1)#向主布局添加子布局1
        self.__layout_main.addLayout(self.__layout2)#向主布局添加子布局2
class App_Exec():
    def valueChange_exec(self,value):#数据调节控件数据发生改变后，执行此操作
        try:
            self.MainUi.QTimer_show.stop()#让已经启动的计时器停止，未启动则忽略
        except:
            pass
        self.MainUi.QTimer_show.start(int(value)*1000)#启动计时器，按新的值执行。
    def show_data(self):
        #显示QTableWidget数据
        QTableWidget_sql = "select stu_age,count(stu_age) as num from test_table group by stu_age having num>=1 order by num desc;"
        cursor.execute(QTableWidget_sql)
        QTableWidget_sql_rs = cursor.fetchall()
        self.MainUi.QTableWidget_show.setRowCount(len(QTableWidget_sql_rs))#设置表格行数
        self.MainUi.QTableWidget_show.setColumnCount(2)#设置表格列数
        self.MainUi.QTableWidget_show.setHorizontalHeaderLabels(['年龄','人数'])#设置横向表头
        for row_num,row_item in enumerate(QTableWidget_sql_rs):
            for col_num,col_item in enumerate(row_item):
                self.MainUi.QTableWidget_show.setItem(row_num,col_num,QTableWidgetItem(str(col_item)))
                #向表格单元格插入数据。





    def signal_connect(self):#信号和槽连接
        self.MainUi.QSpinBox_s.valueChanged.connect(self.valueChange_exec)
        #数值调节发生改变事件，连接到槽

        self.MainUi.QTimer_insert.timeout.connect(self.MainUi.insert_Data)
        #计时器超时，连接到槽

        self.MainUi.QTimer_show.timeout.connect(self.show_data)
        #计时器超时，连接到槽
    def begin(self):#界面程序入口
        self.app = QApplication(sys.argv)
        self.MainUi = Main_Ui()#实例化窗口界面类
        self.MainUi.show()#持续显示窗口
        self.signal_connect()#信号与槽连接。
        sys.exit(self.app.exec_())#退出程序


if __name__ == '__main__':
    AppExec = App_Exec()
    AppExec.begin()
