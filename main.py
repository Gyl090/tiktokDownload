import os.path
import re
import sys

import requests
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QHeaderView, QLabel


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.download_tasks = []  # 存储下载视频的子线程
        self.download_history_table = DownloadHistory()
        self.__init_ui()  # 加载界面

    def __init_ui(self):
        self.resize(600, 400)  # 设置主窗口的宽高
        self.setWindowTitle('抖音下载工具')  # 显示窗口的标题

        self.url_input = QLineEdit()  # url的输入框
        self.url_input.setPlaceholderText('请输入分享链接')
        download_btn = QPushButton('开始下载')  # 下载按钮

        download_btn.clicked.connect(self.handle_btn)  # 绑定点击事件

        h_layout = QHBoxLayout()  # 创建水平布局器 容纳上述两组件
        # 将两个组件添加到布局器中
        h_layout.addWidget(self.url_input, 0, Qt.AlignTop)
        h_layout.addWidget(download_btn, 0, Qt.AlignTop)

        v_layout = QVBoxLayout()  # 创建垂直布局器，容纳表格和上面的水平布局器
        # 创建下面的表格

        # 要将布局器添加到QWidget中
        v_layout.addLayout(h_layout)
        # 创建下载表盒 并填充信息， 加入到垂直 布局器中（表格和水平布局期并列）
        # 同时进行的任务数量
        self.task_num_label = QLabel(str(len(self.download_tasks)))

        v_layout.addWidget(self.download_history_table)
        v_layout.addWidget(self.task_num_label, 0, Qt.AlignBottom)  # 定位到下边
        self.setLayout(v_layout)

        self.show()  # 显示窗口

    def handle_btn(self):
        url_4_download = self.parse_url(self.url_input.text())
        print('点击了按钮', url_4_download)
        # 得到最初的url 开始爬虫分析，准备下载视频
        # 1.1 创建子线程来开启下载任务
        download_task = Download_task()
        download_task.percent_signal.connect(self.update_percent)  # 把一个线程信号和一个更新进度的函数绑定
        self.download_tasks.append(download_task)
        download_task.task_id = self.download_tasks.index(download_task)  # 每一个下载任务进程都有一个自己的id

        # 1.2 把这个系在任务需要用到的url传给子线程
        download_task.url = url_4_download
        # 1.3 开始子线程的run方法，下载视频
        self.download_tasks[-1].start()  # 每次只开启最后的下载任务
        # 开启任务之后 更新表格

    def parse_url(self, full_share_url):
        """提取分享链接中 真正的视频url"""
        if not full_share_url:
            return
        # 正则匹配search得到对象
        inner_url = re.search(r'(http.+[^ ])', full_share_url).group(0)
        return inner_url

    def update_percent(self, task_id, msg, title):  # 把丛子线程获取到的信息展示到表格中对应的行
        # print('子线程发射了信号 现在被我接收到', task_id, msg, title)
        table_row_title = QTableWidgetItem(title)
        table_row_percent = QTableWidgetItem(msg)
        if task_id <= self.download_history_table.table.rowCount():
            self.download_history_table.table.setRowCount(task_id + 1)
        self.download_history_table.table.setItem(task_id, 0, table_row_title)
        self.download_history_table.table.setItem(task_id, 1, table_row_percent)
        # 更新任务数目
        self.task_num_label.setText(str(len(self.download_tasks)))


class DownloadHistory(QWidget):
    def __init__(self):
        super().__init__()
        self.__init_ui()

    def __init_ui(self):
        self.table = QTableWidget(0, 2)  # 默认 0行2列的表格
        self.table.setHorizontalHeaderLabels(['视频名称', '下载进度'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        download_task_lists_layout = QVBoxLayout()
        download_task_lists_layout.addWidget(self.table)

        self.setLayout(download_task_lists_layout)  # 要让这个下载历史组件 使用 这个管理着表格组件的 布局器


class Download_task(QThread):
    percent_signal = pyqtSignal(int, str, str)  # 子线程用来传输 下载进度（str）给主线程ui的信号

    def __init__(self):
        super().__init__()
        self.url = ''
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
                          'like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 '
        }
        self.task_id = 0

    def download_video(self):
        print('最初的地址', self.url)
        r1 = requests.get(url=self.url, headers=self.headers, allow_redirects=False)
        url2 = r1.headers.get('location')
        print('访问最初url后 要求302到', url2)

        # 获取url2后面的关键id
        vid = re.search(r'/video/(\d+)/', url2).group(1)
        # print(vid)
        print(f'接下来访问 https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={vid} 即可获得json')
        base_url = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids='
        r_json = requests.get(url=base_url + vid, headers=self.headers).json()
        # print(type(r_json), r_json)
        title = r_json['item_list'][0].get('desc')  # 获取视频的简介
        url3 = r_json.get('item_list')[0].get('video').get('play_addr').get('url_list')[0]
        final_url = url3.replace('playwm', 'play')
        print('最终的无水印地址为', final_url)

        video_response = requests.get(url=final_url, headers=self.headers, stream=True)
        # 在请求体中获得视频的总长度（字节数）
        video_len = int(video_response.headers.get('Content-Length'))
        video_content = video_response.iter_content(100)

        with open(f'./videos/{title}.mp4', 'wb') as vf:
            cur_down = 0
            try:
                for item in video_content:
                    write_len = vf.write(item)
                    cur_down += write_len
                    percent = '%02.2f%%' % (cur_down * 100 / video_len)
                    # print('正在下载', percent)
                    self.percent_signal.emit(self.task_id, percent, title)
                    # 发射信号 在界面上 展示进度
            except requests.exceptions.StreamConsumedError:
                print('下载完毕 100%')

    def run(self):
        print('现在开始下载', self.url)
        self.download_video()


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    if not os.path.exists(BASE_DIR + 'videos'):
        os.mkdir(BASE_DIR + 'videos')

    app = QApplication(sys.argv)

    main_widget = MainWidget()

    sys.exit(app.exec_())
