import os
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QScreen
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit, QFrame


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(700, 400)
        self.setWindowTitle('Live2d模型运动参数获取工具')
        self.window_center()
        path = Path(__file__).resolve().parent
        self.setWindowIcon(QIcon(os.path.join(path, '../img/icon.png')))
        
        self.sidebar = QFrame(self)
        self.sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        self.sidebar.setFrameShadow(QFrame.Shadow.Raised)
        self.sidebar.setMinimumWidth(200)
        self.sidebar.setMaximumWidth(200)
        
        self.port_label = QLabel("输入服务端端口号：")
        self.port_input = QLineEdit("8001")
        self.port_input.setFixedWidth(120)
        self.port_input.setFixedHeight(30)
        self.prepare_button = QPushButton("准备")
        self.prepare_button.setFixedWidth(110)
        self.prepare_button.setFixedHeight(35)
        self.prepare_button.clicked.connect(self.on_prepare_button_click)
        
        self.sidebar_layout = QVBoxLayout(self)
        self.sidebar_layout.setContentsMargins(20, 20, 20, 20)
        self.sidebar_layout.setSpacing(10)
        self.sidebar_layout.addWidget(self.port_label)
        self.sidebar_layout.addWidget(self.port_input)
        self.sidebar_layout.addStretch(1)
        self.sidebar_layout.addWidget(self.prepare_button)
        self.sidebar.setLayout(self.sidebar_layout)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.main_layout)
        
        
    def window_center(self):
        screen_size = QScreen.availableGeometry(QApplication.primaryScreen())
        x = (screen_size.width() - self.width()) / 2
        y = (screen_size.height() - self.height()) / 2 - 40
        self.move(x, y)

    def on_prepare_button_click(self):
        print("准备按钮被点击")
        
    
def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()