import os
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QScreen
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout

from sidebar import Sidebar


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(700, 400)
        self.setWindowTitle('Live2d模型运动参数获取工具')
        self.window_center()
        path = Path(__file__).resolve().parent
        self.setWindowIcon(QIcon(os.path.join(path, '../img/icon.png')))

        # 设置全局按钮样式
        self.setStyleSheet("""
                QPushButton {
                    background-color: #0870C1;
                    border: none;
                    color: white;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 14px;
                    font-weight: bold;
                    cursor: pointer;
                    border-radius: 8px;
                    padding: 8px 16px;
                }

                QPushButton:hover {
                    background-color: #0978D1;
                }

                QPushButton:disabled {
                    background-color: #2D2D2D;
                    border: 1px solid red; /* 禁用时的红色边框 */
                    color: #808080;
                    cursor: not-allowed;
                }
            """)

        self.sidebar = Sidebar()
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.main_layout)
        
        
    def window_center(self):
        screen_size = QScreen.availableGeometry(QApplication.primaryScreen())
        x = (screen_size.width() - self.width()) / 2
        y = (screen_size.height() - self.height()) / 2 - 40
        self.move(int(x), int(y))
        
    
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()