"""
配置加载模块 — 从 .env 和环境变量加载非敏感配置

用法:
    from src.config import Config
    c = Config.load()
    print(c.FUSION_MCP_URL)  # http://127.0.0.1:27182
    print(c.FUSION_MCP_TIMEOUT)  # 60
    print(c.get("unknown_key", "default"))
"""

import os
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Config:
    """项目运行时配置"""
    # ── Fusion MCP ──
    FUSION_MCP_URL: str = "http://127.0.0.1:27182"
    FUSION_MCP_TIMEOUT: int = 60
    FUSION_DOC_ID: Optional[str] = None

    # ── GitHub (脚本自动推送时用) ──
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_OWNER: str = "Betty0601"
    GITHUB_REPO: str = "yunwei"

    # ── 导出路径 ──
    MODEL_DIR: str = "models"
    ASSET_DIR: str = "assets"
    LOG_DIR: str = "logs"

    # ── 行为开关 ──
    REUSE_DOCUMENT: bool = True  # Fusion 中复用已有文档
    AUTO_CREATE_DOC: bool = True  # 没有文档时自动创建
    CREDENTIAL_HELPER: str = "osxkeychain"

    @classmethod
    def load(cls, env_path: Optional[str] = None) -> "Config":
        """加载配置：环境变量 > .env 文件 > 默认值"""
        # 1. 先设置默认值
        cfg = cls()

        # 2. 加载 .env 文件（如果存在）
        paths = [env_path] if env_path else [".env", ".env.local"]
        for p in paths:
            if os.path.isfile(p):
                print(f"📄 加载 {p}...", file=sys.stderr)
                with open(p) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, _, val = line.partition("=")
                        cfg._set(key.strip(), val.strip())
                break

        # 3. 环境变量覆盖最高优先级
        for key in cfg._field_names():
            env_val = os.environ.get(key)
            if env_val is not None:
                cfg._set(key, env_val)

        # 4. 类型转换
        cfg._coerce_types()
        return cfg

    def _set(self, key: str, val: str):
        """设置字段值（支持模糊匹配）"""
        key_upper = key.upper()
        if hasattr(self, key_upper):
            setattr(self, key_upper, val)

    def _coerce_types(self):
        """将字符串值转换为正确的 Python 类型"""
        for name in self._field_names():
            cur = getattr(self, name)
            if isinstance(cur, str):
                # int
                try:
                    if name.endswith("_TIMEOUT") or name.endswith("_DIR") or name.endswith("_PORT"):
                        pass  # timeout 可以是 int
                    if name.endswith("_TIMEOUT"):
                        setattr(self, name, int(cur))
                except ValueError:
                    pass
                # bool
                low = cur.lower()
                if low in ("true", "1", "yes"):
                    setattr(self, name, True)
                elif low in ("false", "0", "no", ""):
                    setattr(self, name, False)
        # timeout 最后处理
        if isinstance(self.FUSION_MCP_TIMEOUT, str) and self.FUSION_MCP_TIMEOUT.isdigit():
            self.FUSION_MCP_TIMEOUT = int(self.FUSION_MCP_TIMEOUT)

    @classmethod
    def _field_names(cls):
        return [f for f in cls.__dataclass_fields__]

    def get(self, key: str, default=None):
        """字典风格访问"""
        return getattr(self, key.upper(), default)

    def summary(self, redact: bool = True) -> dict:
        """返回配置摘要（敏感值脱敏）"""
        result = {}
        for name in self._field_names():
            val = getattr(self, name)
            if redact and ("TOKEN" in name or "SECRET" in name or "PASSWORD" in name):
                result[name] = "*** (redacted)" if val else None
            else:
                result[name] = val
        return result


def load_config() -> Config:
    """便捷函数"""
    return Config.load()


if __name__ == "__main__":
    cfg = Config.load()
    print("=== yunwei 配置摘要 ===")
    for k, v in cfg.summary().items():
        print(f"  {k} = {v}")
