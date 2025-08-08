import asyncio
import json
import websockets
from PySide6.QtCore import QThread, Signal


class WebsocketTask(QThread):
    prepare_done = Signal(str)
    parameter_data = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, port, plugin_name, plugin_developer, plugin_icon, parent=None):
        super().__init__(parent)
        self.port = port
        self.plugin_name = plugin_name
        self.plugin_developer = plugin_developer
        self.plugin_icon = plugin_icon
        self.ws = None
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.authentication_token = None
        self.running = False
        self.request_counter = 1

    def run(self):
        """线程入口点"""
        try:
            self.loop.run_until_complete(self.start_listening())
        except Exception as e:
            print(f"监听循环出错: {e}")
            self.error_occurred.emit(f"监听循环出错: {e}")
        finally:
            self.loop.close()

    async def initialize_websocket(self):
        ws_url = f"ws://localhost:{self.port}"
        print(f"尝试连接 WebSocket: {ws_url}")
        try:
            self.ws = await websockets.connect(ws_url, ping_interval=30)
            print(f"WebSocket 连接成功: {ws_url}")
            return True
        except Exception as e:
            print(f"连接 WebSocket 失败: {e}")
            self.error_occurred.emit(f"连接 WebSocket 失败: {e}")
            return False

    async def request_authentication_token(self):
        """请求认证令牌"""
        try:
            if not await self.initialize_websocket():
                return

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
            print("已发送认证令牌请求")

            response = await self.ws.recv()
            response_data = json.loads(response)

            if response_data["messageType"] == "AuthenticationTokenResponse":
                self.authentication_token = response_data["data"]["authenticationToken"]
                print(f"获取到认证令牌: {self.authentication_token}")
                self.prepare_done.emit(self.authentication_token)
            else:
                error_message = response_data.get("data", {}).get("message", "未知错误")
                self.error_occurred.emit(f"获取认证令牌失败: {error_message}")

            # 关闭连接，因为后续的监听会使用新的连接
            await self.ws.close()
            self.ws = None

        except Exception as e:
            print(f"请求认证令牌时出错: {e}")
            self.error_occurred.emit(f"请求认证令牌时出错: {e}")
            await self.ws.close()
            self.ws = None

    async def authenticate(self):
        """认证会话"""
        # 确保有有效的 WebSocket 连接
        if self.ws is None:
            if not await self.initialize_websocket():
                return None

        # 检查连接是否已关闭
        try:
            # 发送一个简单的 ping 测试连接
            await self.ws.ping()
        except websockets.exceptions.ConnectionClosed:
            # 连接已关闭，尝试重新连接
            if not await self.initialize_websocket():
                return None

        auth_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": f"AuthRequest_{self.request_counter}",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": self.plugin_name,
                "pluginDeveloper": self.plugin_developer,
                "authenticationToken": self.authentication_token
            }
        }
        self.request_counter += 1

        try:
            await self.ws.send(json.dumps(auth_request))
            print("已发送认证请求")

            response = await self.ws.recv()
            return json.loads(response)
        except websockets.exceptions.ConnectionClosed:
            print("认证过程中连接已关闭")
            return None

    async def get_parameters(self):
        param_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": f"ParamRequest_{self.request_counter}",
            "messageType": "Live2DParameterListRequest"
        }
        self.request_counter += 1

        try:
            await self.ws.send(json.dumps(param_request))

            response = await self.ws.recv()
            return json.loads(response)
        except websockets.exceptions.ConnectionClosed:
            print("获取参数过程中连接已关闭")
            return {"messageType": "ConnectionClosed"}

    async def start_listening(self):
        self.running = True

        await self.request_authentication_token()

        if self.ws is None:
            if not await self.initialize_websocket():
                self.error_occurred.emit("无法建立 WebSocket 连接")
                return

        # 认证会话
        auth_response = await self.authenticate()
        if auth_response is None:
            self.error_occurred.emit("认证失败: 连接问题")
            return

        if auth_response.get("messageType") != "AuthenticationResponse":
            error_msg = auth_response.get("data", {}).get("message", "认证失败")
            self.error_occurred.emit(f"认证失败: {error_msg}")
            return

        print("认证成功，开始监听模型参数...")

        try:
            while True:
                if self.running:
                    try:
                        # 获取参数
                        response = await self.get_parameters()

                        if response is None:
                            # 重新连接
                            if not await self.initialize_websocket():
                                self.error_occurred.emit("连接已关闭且无法重新连接")
                                break

                            # 重新认证
                            auth_response = await self.authenticate()
                            if not auth_response or auth_response.get("messageType") != "AuthenticationResponse":
                                self.error_occurred.emit("重新认证失败")
                                break
                            continue

                        # 处理响应
                        if response["messageType"] == "Live2DParameterListResponse":
                            self.parameter_data.emit(response["data"])
                        elif response["messageType"] == "APIError":
                            error_id = response["data"]["errorID"]
                            if error_id == 11:  # ModelNotLoaded错误
                                self.error_occurred.emit("当前没有加载模型！请加载模型后再试。")
                            else:
                                error_msg = response["data"]["message"]
                                self.error_occurred.emit(f"API错误: {error_msg}")
                        elif response["messageType"] == "ConnectionClosed":
                            # 重新连接
                            if not await self.initialize_websocket():
                                self.error_occurred.emit("连接已关闭且无法重新连接")
                                break

                            # 重新认证
                            auth_response = await self.authenticate()
                            if not auth_response or auth_response.get("messageType") != "AuthenticationResponse":
                                self.error_occurred.emit("重新认证失败")
                                break

                        # 每秒20次请求（理论上是这样的，实际我也不清楚能不能刚好20次）
                        await asyncio.sleep(0.05)

                    except Exception as e:
                        print(f"获取参数时出错: {e}")
                        self.error_occurred.emit(f"获取参数时出错: {str(e)}")
                        await asyncio.sleep(1)  # 出错后等待1秒再重试
        finally:
            if self.ws:
                await self.ws.close()
                self.ws = None
            print("监听已停止")

    def stop_listening(self):
        # 只是暂停发送请求，因为如果直接关闭循环再次开启就会很麻烦
        self.running = False