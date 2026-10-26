"""
统一错误分类 — 所有 Fusion/Git/GitHub 相关异常的结构化层级

错误分类（对应长提示词要求）:
  CONFIG_ERROR         配置缺失或错误
  CREDENTIAL_ERROR     认证/密钥问题
  GIT_ERROR            Git 本地操作异常
  GITHUB_ERROR         GitHub API/推送异常
  MCP_CONNECTION_ERROR Fusion MCP 不可达或握手失败
  MCP_PROTOCOL_ERROR   MCP 协议不兼容
  FUSION_DOC_ERROR     Fusion 文档状态异常
  FUSION_API_ERROR     Fusion API 调用失败
  FUSION_GEOMETRY_ERROR 几何无效
  FUSION_EXPORT_ERROR  导出失败
  NETWORK_ERROR        网络层问题
  TIMEOUT_ERROR        操作超时
  UNKNOWN_ERROR        兜底
"""


class YunweiError(Exception):
    """项目统一异常基类"""
    code: str = "UNKNOWN_ERROR"
    recoverable: bool = True

    def __init__(self, message: str, details: str = "", hint: str = "",
                 cause: Exception = None):
        super().__init__(message)
        self.message = message
        self.details = details
        self.hint = hint
        self.cause = cause
        self.recoverable = type(self).recoverable

    def to_dict(self) -> dict:
        return {
            "error_code": self.code,
            "message": self.message,
            "details": self.details,
            "hint": self.hint,
            "recoverable": self.recoverable,
        }

    def __str__(self) -> str:
        base = f"[{self.code}] {self.message}"
        if self.details:
            base += f"\n  details: {self.details}"
        if self.hint:
            base += f"\n  hint: {self.hint}"
        return base


class ConfigError(YunweiError):
    code = "CONFIG_ERROR"
    recoverable = True


class CredentialError(YunweiError):
    code = "CREDENTIAL_ERROR"
    recoverable = True


class GitError(YunweiError):
    code = "GIT_ERROR"
    recoverable = True


class GitHubError(YunweiError):
    code = "GITHUB_ERROR"
    recoverable = True


class MCPConnectionError(YunweiError):
    code = "MCP_CONNECTION_ERROR"
    recoverable = True

    def __init__(self, **kw):
        kw.setdefault("hint", "确认 Fusion 360 正在运行，Preferences > General > API 已启用 Fusion MCP Server")
        super().__init__(**kw)


class MCPProtocolError(YunweiError):
    code = "MCP_PROTOCOL_ERROR"
    recoverable = False


class FusionDocError(YunweiError):
    code = "FUSION_DOC_ERROR"
    recoverable = True


class FusionAPIError(YunweiError):
    code = "FUSION_API_ERROR"
    recoverable = True


class FusionGeometryError(YunweiError):
    code = "FUSION_GEOMETRY_ERROR"
    recoverable = False


class FusionExportError(YunweiError):
    code = "FUSION_EXPORT_ERROR"
    recoverable = True


class NetworkError(YunweiError):
    code = "NETWORK_ERROR"
    recoverable = True


class TimeoutError(YunweiError):
    code = "TIMEOUT_ERROR"
    recoverable = True


def classify_exception(e: Exception) -> YunweiError:
    """将任意异常归类为对应的 YunweiError"""
    if isinstance(e, YunweiError):
        return e
    msg = str(e)

    if "Connection failed" in msg or "ConnectionRefusedError" in type(e).__name__:
        return MCPConnectionError(message=msg, cause=e)
    if "HTTPError" in type(e).__name__ or "HTTP" in msg:
        if "MCP-Session-Id" in msg:
            return MCPProtocolError(message=msg, hint="Session 过期了，重新 connect()", cause=e)
        return NetworkError(message=msg, cause=e)
    if "No such file" in msg or "FileNotFoundError" in type(e).__name__:
        return ConfigError(message=msg, hint="检查文件路径和 .gitignore", cause=e)
    if "Permission" in msg or "credential" in msg.lower():
        return CredentialError(message=msg, cause=e)
    if "timeout" in msg.lower():
        return TimeoutError(message=msg, cause=e)
    if "Fusion" in msg or "adsk" in msg or "AttributeError" in msg:
        return FusionAPIError(message=msg, cause=e)

    return YunweiError(message=msg, cause=e)


if __name__ == "__main__":
    # 演示
    try:
        raise MCPConnectionError(message="无法连接 localhost:27182")
    except YunweiError as e:
        print(e)
        print()
        print("dict:", e.to_dict())
        print()
        print("recoverable:", e.recoverable)
