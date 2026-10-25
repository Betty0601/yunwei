"""
Autodesk Fusion 360 MCP Client (Streamable HTTP)

官方 Fusion MCP Server 客户端，通过 HTTP 与本地运行的 Fusion 360 通信。
协议版本: 2024-11-05
默认端点: http://127.0.0.1:27182/mcp

使用示例:
    client = FusionMCPClient()
    client.connect()
    result = client.read(queryType="licensing")
    script_result = client.execute_script("...python code...")
    client.disconnect()
"""

import json
import uuid
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List


class FusionMCPError(Exception):
    """Fusion MCP 操作错误"""
    pass


class FusionMCPClient:
    """Fusion 360 MCP Streamable HTTP 客户端"""

    DEFAULT_URL = "http://127.0.0.1:27182/mcp"
    PROTOCOL_VERSION = "2024-11-05"
    CLIENT_INFO = {"name": "yunwei-fusion-client", "version": "1.0.0"}

    def __init__(self, url: str = DEFAULT_URL, timeout: int = 60):
        self.url = url
        self.timeout = timeout
        self.session_id: Optional[str] = None
        self._tools_cache: Optional[List[Dict]] = None
        self._id_counter = 0

    # ── 连接管理 ──────────────────────────────────────

    def connect(self) -> Dict[str, Any]:
        """初始化 MCP 会话，返回 server info"""
        # 先执行 initialize 请求获取 session id
        self._id_counter += 1
        init_payload = {
            "jsonrpc": "2.0",
            "id": self._id_counter,
            "method": "initialize",
            "params": {
                "protocolVersion": self.PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": self.CLIENT_INFO,
            },
        }
        headers = {"Content-Type": "application/json"}  # 注意：initialize 不带 session id
        data = json.dumps(init_payload).encode("utf-8")
        req = urllib.request.Request(self.url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                # 从 initialize 响应中获取 session id
                self.session_id = resp.headers.get("MCP-Session-Id")
                if not self.session_id:
                    raise FusionMCPError("MCP server did not return session id on initialize")
                body = resp.read().decode("utf-8")
                response = json.loads(body)
                result = response.get("result", {})
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8") if e.fp else ""
            raise FusionMCPError(f"HTTP {e.code}: {body}") from e

        # 发送 initialized notification
        self._notify("notifications/initialized", {})
        return result

    def disconnect(self):
        """断开连接"""
        self.session_id = None
        self._tools_cache = None

    def is_connected(self) -> bool:
        return self.session_id is not None

    def ping(self) -> bool:
        """健康检查：尝试连接 Fusion MCP"""
        try:
            client = FusionMCPClient(self.url, timeout=5)
            client.connect()
            client.disconnect()
            return True
        except Exception:
            return False

    # ── 工具查询 ──────────────────────────────────────

    def list_tools(self, refresh: bool = False) -> List[Dict]:
        """获取 MCP 可用工具列表"""
        if self._tools_cache and not refresh:
            return self._tools_cache
        response = self._request("tools/list", {})
        self._tools_cache = response["result"]["tools"]
        return self._tools_cache

    # ── CRUD 操作封装 ─────────────────────────────────

    def _tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """通用工具调用"""
        response = self._request("tools/call", {
            "name": tool_name,
            "arguments": arguments,
        })
        result = response.get("result", {})
        # 从 content 数组中提取文本
        content = result.get("content", [])
        text_parts = []
        for item in content:
            if item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        raw_text = "\n".join(text_parts)

        # 尝试 JSON 解析
        parsed_text = raw_text
        try:
            parsed_text = json.loads(raw_text)
        except (json.JSONDecodeError, TypeError):
            pass

        if result.get("isError"):
            raise FusionMCPError(
                f"Tool '{tool_name}' error: {result.get('error', raw_text)}"
            )
        return {"raw": raw_text, "parsed": parsed_text, "full": result}

    # ── fusion_mcp_read ────────────────────────────────

    def read(self, queryType: str, **kwargs) -> Dict[str, Any]:
        """
        读取 Fusion 模型数据

        queryType 可选值:
            - "licensing": 许可证信息
            - "projects": 项目列表
            - "document": 文档操作 (需配合 operation)
            - "screenshot": 截图
            - "apiDocumentation": API 文档搜索
            - "activeCommand": 当前命令
        """
        args = {"queryType": queryType, **kwargs}
        return self._tool_call("fusion_mcp_read", args)["parsed"]

    # ── fusion_mcp_execute ─────────────────────────────

    def execute_script(self, script: str, read_only: bool = False) -> Dict[str, Any]:
        """
        在 Fusion 中执行 Python 脚本

        Args:
            script: Fusion API Python 代码
            read_only: 如果脚本只读不写，设为 True 可在命令对话框打开时运行
        """
        args = {
            "featureType": "script",
            "object": {
                "script": script,
                "readOnly": read_only,
            },
        }
        return self._tool_call("fusion_mcp_execute", args)["parsed"]

    def document_open(self, fileId: str) -> Dict[str, Any]:
        """打开文档"""
        return self._tool_call("fusion_mcp_execute", {
            "featureType": "document",
            "object": {"operation": "open", "fileId": fileId},
        })["parsed"]

    def document_save(self) -> Dict[str, Any]:
        """保存当前文档"""
        return self._tool_call("fusion_mcp_execute", {
            "featureType": "document",
            "object": {"operation": "save"},
        })["parsed"]

    def document_close(self) -> Dict[str, Any]:
        """关闭当前文档"""
        return self._tool_call("fusion_mcp_execute", {
            "featureType": "document",
            "object": {"operation": "close"},
        })["parsed"]

    # ── fusion_mcp_update ──────────────────────────────

    def undo(self) -> Dict[str, Any]:
        """撤销上一步操作"""
        return self._tool_call("fusion_mcp_update", {
            "featureType": "undo",
        })["parsed"]

    def redo(self) -> Dict[str, Any]:
        """重做撤销的操作"""
        return self._tool_call("fusion_mcp_update", {
            "featureType": "redo",
        })["parsed"]

    # ── 便捷方法 ───────────────────────────────────────

    def get_license(self) -> Dict[str, Any]:
        """获取许可证信息"""
        return self.read("licensing")

    def get_open_documents(self) -> Dict[str, Any]:
        """获取当前打开的文档"""
        return self.read("document", operation="open")

    def get_recent_documents(self) -> Dict[str, Any]:
        """获取最近文档"""
        return self.read("document", operation="recent")

    def search_document(self, name: str, project: Optional[str] = None) -> Dict[str, Any]:
        """搜索文档"""
        args = {"queryType": "document", "operation": "search", "name": name}
        if project:
            args["project"] = project
        return self._tool_call("fusion_mcp_read", args)["parsed"]

    def get_projects(self) -> Dict[str, Any]:
        """获取所有项目"""
        return self.read("projects")

    def take_screenshot(self, direction: str = "iso-top-right", height: int = 800) -> Dict[str, Any]:
        """
        获取 Fusion 视口截图

        direction: current | front | back | top | bottom | left | right | iso-*
        """
        return self.read("screenshot", direction=direction, height=height)

    def search_api(self, pattern: str, category: str = "all", filter: Optional[str] = None) -> Dict[str, Any]:
        """
        搜索 Fusion API 文档

        Args:
            pattern: 正则搜索模式
            category: class | member | description | all
            filter: 可选，限定命名空间，如 "adsk.fusion"
        """
        args = {"queryType": "apiDocumentation", "searchPattern": pattern, "apiCategory": category}
        if filter:
            args["filter"] = filter
        return self.read(**args)

    # ── 底层 HTTP ─────────────────────────────────────

    def _request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送 JSON-RPC 请求到 MCP server"""
        self._id_counter += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._id_counter,
            "method": method,
            "params": params,
        }

        headers = {"Content-Type": "application/json"}
        if self.session_id:
            headers["MCP-Session-Id"] = self.session_id

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                # 如果服务器返回了新的 session id 且当前为空，则设置
                if not self.session_id:
                    new_session = resp.headers.get("MCP-Session-Id")
                    if new_session:
                        self.session_id = new_session

                body = resp.read().decode("utf-8")
                response = json.loads(body)
                return response

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8") if e.fp else ""
            raise FusionMCPError(f"HTTP {e.code}: {body}") from e
        except urllib.error.URLError as e:
            raise FusionMCPError(f"Connection failed: {e.reason}. Is Fusion 360 running with MCP enabled?") from e

    def _notify(self, method: str, params: Dict[str, Any]):
        """发送 notification（无 id，无响应）"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }
        headers = {"Content-Type": "application/json"}
        if self.session_id:
            headers["MCP-Session-Id"] = self.session_id
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.url, data=data, headers=headers, method="POST")
        try:
            urllib.request.urlopen(req, timeout=self.timeout).read()
        except Exception:
            pass  # notification 不需要响应


def connect(url: str = FusionMCPClient.DEFAULT_URL) -> FusionMCPClient:
    """便捷函数：一键连接 Fusion MCP"""
    client = FusionMCPClient(url)
    client.connect()
    return client


if __name__ == "__main__":
    # 快速自测
    print("🔍 检查 Fusion MCP 连接...")
    c = FusionMCPClient()
    if c.ping():
        print("✅ Fusion MCP Server 可达!")
        c.connect()
        lic = c.get_license()
        summary = lic.get("summary", {})
        print(f"   许可证: {lic.get('licenseTypeSummary', '?')}")
        print(f"   学生版: {summary.get('isStudent', False)}")
        c.disconnect()
    else:
        print("❌ 无法连接 Fusion MCP Server")
        print("   请确认 Fusion 360 正在运行，且已在 Preferences > General > API 中启用 Fusion MCP Server")
