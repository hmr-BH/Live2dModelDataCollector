import asyncio
import json
import os
import aiofiles
from PySide6.QtCore import QThread, Signal
import websockets

WS_URL = ""

class WebsocketTask(QThread):
    prepare_done = Signal(str)

    def __init__(self, port, plugin_name, plugin_developer, plugin_icon, token_path, /):
        super().__init__()
        self.port = port
        self.plugin_name = plugin_name
        self.plugin_developer = plugin_developer
        self.plugin_icon = plugin_icon
        self.token_path = token_path
        self.ws = None
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.authentication_token = None

    def prepare(self):
        self.loop.run_until_complete(self.request_authentication_token())

    async def initialize_websocket(self):
        global WS_URL
        WS_URL = f"ws://localhost:{self.port}"
        print(f"WebSocket URL 已设置为：{WS_URL}")
        try:
            print(f"WebSocket 连接初始化到：{WS_URL}")
            self.ws = await websockets.connect(WS_URL)
        except Exception as e:
            print(f"初始化 WebSocket 连接时出错: {e}")
            self.prepare_done.emit(f"初始化 WebSocket 连接时出错: {e}")

    async def request_authentication_token(self):
        try:
            await self.initialize_websocket()
            if not self.ws:
                raise Exception("WebSocket 连接未成功初始化")

            # 如果已经获取过token，直接使用
            if os.path.exists(self.token_path):
                async with aiofiles.open(self.token_path, mode="r") as f_token:
                    self.authentication_token = await f_token.read()
                    print(f"从文件中读取到 authenticationToken: {self.authentication_token}")
                    self.prepare_done.emit(self.authentication_token)
                    return

            # AuthenticationTokenRequest 请求
            request = {
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "AuthenticationTokenRequest",
                "messageType": "AuthenticationTokenRequest",
                "data": {
                    "pluginName": self.plugin_name,
                    "pluginDeveloper": self.plugin_developer,
                    "pluginIcon": self.plugin_icon
                }
            }

            await self.ws.send(json.dumps(request))
            print(f"请求已发送: {request}")

            response = await self.ws.recv()
            response_data = json.loads(response)
            print(f"收到响应: {response_data}")

            if response_data["messageType"] == "AuthenticationTokenResponse":
                self.authentication_token = response_data["data"]["authenticationToken"]
                print(f"获取到 authenticationToken: {self.authentication_token}")
                self.prepare_done.emit(self.authentication_token)

                # 保存token到文件
                async with aiofiles.open(self.token_path, mode="w") as f_token:
                    await f_token.write(self.authentication_token)
                    print(f"authenticationToken 已保存到文件: {self.token_path}")
            else:
                error_message = response_data.get("data", {}).get("message", "未知错误")
                self.prepare_done.emit(f"获取 authenticationToken 时出错: {error_message}")

        except Exception as e:
            print(f"请求 authenticationToken 时出错: {e}")
            self.prepare_done.emit(f"请求 authenticationToken 时出错: {e}")
        finally:
            if self.ws:
                await self.ws.close()
                print("WebSocket 连接已关闭")

    def run(self):
        self.loop.run_until_complete(self.request_authentication_token())
        self.loop.close()