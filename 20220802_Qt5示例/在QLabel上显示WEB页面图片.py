from PyQt5.Qt import *
import sys,requests

class Main_UI(QWidget):
    def __init__(self,url):
        super().__init__()
        self.url = url
        self.setupUI()
    def setupUI(self):
        self.layout_main = QHBoxLayout()
        self.QLabel_image = QLabel()
        self.layout_main.addWidget(self.QLabel_image)
        self.setLayout(self.layout_main)
        self.get_url_image()
    def get_url_image(self):
        url_image = requests.get(self.url).content
        self.QBy_data = QByteArray(url_image)
        self.QBuffer_obj = QBuffer(self.QBy_data)#此处注意，如果将self.QBy_data设置成局部变量，就会报错，具体为什么，还不清楚。
        self.movie = QMovie()
        self.movie.setDevice(self.QBuffer_obj)
        self.QLabel_image.setMovie(self.movie)
        # self.movie.set()
        self.movie.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    url_gif = 'https://n.sinaimg.cn/finance/blackcat/pc/blackcat-hover.gif'
    url_png ='https://huaban.com/img/error_page/img_404.png'
    url_jpg = 'http://n.sinaimg.cn/default/1_img/upload/3933d981/749/w930h619/20210331/6362-knaqvqn8332153.jpg'
    ui = Main_UI(url_gif)
    ui.show()
    sys.exit(app.exec_())