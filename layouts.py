import sys

from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.__init_UI()
        self.show()

    def __init_UI(self):
        self.resize(400, 300)
        self.setWindowTitle('布局器练习')

        # 创建外层的大布局器， 是垂直的
        container = QHBoxLayout()

        # 创建第一个组 上面的爱好栏目 垂直布局
        hobby_layout = QVBoxLayout()
        # 创建 爱好组 把单选框添加进去
        hobby_box = QGroupBox('爱好')
        btn1 = QRadioButton('抽烟')
        btn2 = QRadioButton('喝酒')
        btn3 = QRadioButton('烫头')
        # 把三个按钮交给 布局器 管理
        hobby_layout.addWidget(btn1)
        hobby_layout.addWidget(btn2)
        hobby_layout.addWidget(btn3)
        hobby_box.setLayout(hobby_layout)

        # 创建第二个组 下面的性别栏目 水平布局
        gender_layout = QHBoxLayout()
        # 创建 性别组 把单选框添加进去
        gender_box = QGroupBox('性别')
        btn4 = QRadioButton('男')
        btn5 = QRadioButton('女')
        # 把两个按钮交给水平布局期管理
        gender_layout.addWidget(btn4)
        gender_layout.addWidget(btn5)
        gender_box.setLayout(gender_layout)

        # 把两个栏目添加到外面的大布局器
        container.addWidget(hobby_box)
        container.addWidget(gender_box)
        self.setLayout(container)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = MyWindow()

    sys.exit(app.exec_())
