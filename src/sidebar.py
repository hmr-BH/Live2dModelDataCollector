import time
from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QFileDialog
from src.cache_manager import CacheManager
from src.websocket_task import WebsocketTask


class Sidebar(QFrame):
    def __init__(self):
        super().__init__()
        self.wt = None
        self.port = 8001
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setMinimumWidth(200)
        self.setMaximumWidth(200)

        # 创建UI元素
        self.port_label = QLabel("输入服务端端口号：")
        self.port_input = QLineEdit("8001")
        self.port_input.setFixedWidth(120)
        self.port_input.setFixedHeight(30)
        self.port_input.textChanged.connect(self.on_port_input_text_changed)

        self.prepare_button = QPushButton("准备")
        self.prepare_button.setFixedWidth(110)
        self.prepare_button.setFixedHeight(35)
        self.prepare_button.clicked.connect(self.on_prepare_button_click)

        self.start_button = QPushButton("开始监听")
        self.start_button.setFixedWidth(110)
        self.start_button.setFixedHeight(35)
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.on_start_button_click)

        self.stop_button = QPushButton("停止监听")
        self.stop_button.setFixedWidth(110)
        self.stop_button.setFixedHeight(35)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.on_stop_button_click)

        # 布局
        self.sidebar_layout = QVBoxLayout(self)
        self.sidebar_layout.setContentsMargins(20, 20, 20, 20)
        self.sidebar_layout.setSpacing(10)
        self.sidebar_layout.addWidget(self.port_label)
        self.sidebar_layout.addWidget(self.port_input)
        self.sidebar_layout.addStretch(1)
        self.sidebar_layout.addWidget(self.prepare_button)
        self.sidebar_layout.addWidget(self.start_button)
        self.sidebar_layout.addWidget(self.stop_button)

        self.plugin_name = "Live2d Model Data Collector"
        self.plugin_developer = "SwarmClone Org. (https://github.com/SwarmClone/SwarmClone)"
        # 注意，这里的图标必须是128*128，且按照Base64编码
        self.plugin_icon = "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"
        self.authentication_token = None

        self.send_param_request = False
        self.cache_manager = None
        self.save_path = None

    def on_port_input_text_changed(self, text):
        try:
            self.port = int(text)
            if self.port > 65535 or self.port < 0:
                raise ValueError
            print(f"端口号已更新为：{self.port}")
        except ValueError:
            self.port = None
            print("出现错误：必须输入一个有效的整数端口号")

    def on_prepare_button_click(self):
        if self.port is None or not (0 <= self.port <= 65535):
            self.show_error("端口错误",
                            "必须输入一个有效的整数端口号\n请确保输入框内没有非数字字符\n设置的端口号需要在0~65535的范围内")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "选择保存位置",
            f"live2d_data_{int(time.time())}.csv",
            "CSV Files (*.csv)"
        )
        if not file_path:
            return  # 用户取消，直接返回

        self.save_path = file_path
        print("准备按钮被点击，保存路径已选择：", self.save_path)

        self.wt = WebsocketTask(self.port, self.plugin_name, self.plugin_developer, self.plugin_icon)
        self.wt.prepare_done.connect(self.on_websocket_prepare_done)
        self.wt.error_occurred.connect(self.handle_websocket_error)
        self.wt.start()

    def on_start_button_click(self):
        if not (self.authentication_token and self.wt and self.save_path):
            return

        print("开始监听按钮被点击")
        self.send_param_request = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.prepare_button.setEnabled(False)

        self.cache_manager = CacheManager(self.save_path)

        self.wt.parameter_data.connect(self.handle_parameter_data)
        self.wt.error_occurred.connect(self.handle_websocket_error)

        self.wt.running = True
        self.wt.loop.run_until_complete(self.wt.start_listening())

    def on_stop_button_click(self):
        print("停止监听按钮被点击")
        if self.wt:
            self.wt.stop_listening()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.prepare_button.setEnabled(True)
            self.send_param_request = False
            self.cache_manager.close()
            self.show_success("监听已停止", f"数据已保存至：\n{self.save_path}")

    def on_websocket_prepare_done(self, result):
        if "出错" in result:
            self.show_error("认证错误", result)
        else:
            print(f"获取到 authenticationToken: {result}")
            self.authentication_token = result
            self.start_button.setEnabled(True)
            self.show_success("准备完成", "准备完成！可以开始监听。")

    def handle_parameter_data(self, data):
        if self.send_param_request:
            parameters = [
                {"name": p["name"], "value": p["value"]}
                for p in data.get("parameters", [])
            ]
            self.cache_manager.append(parameters)

            print("\n===== 收到模型参数数据 =====")
            print(f"帧号: {self.cache_manager._frame}")
            print(f"模型加载状态: {'已加载' if data.get('modelLoaded') else '未加载'}")
            if data.get("modelLoaded"):
                print(f"模型名称: {data.get('modelName', '未知')}")
                print(f"参数数量: {len(parameters)}")
                for i, param in enumerate(parameters, 1):
                    print(f"{i}. {param['name']}: {param['value']}")
            else:
                print("当前没有加载模型！")
            print("=" * 30)

    def handle_websocket_error(self, error_message):
        self.show_error("WebSocket错误", error_message)
        self.on_stop_button_click()

    def show_error(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.button(QMessageBox.Ok).setText("确认")
        msg_box.exec()

    def show_success(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.button(QMessageBox.Ok).setText("确认")
        msg_box.exec()