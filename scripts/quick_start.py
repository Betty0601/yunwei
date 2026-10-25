#!/usr/bin/env python3
"""
快速开始脚本：通过 Fusion MCP 创建一个 20×20×20 的立方体

用法: python3 scripts/quick_start.py
前提: Fusion 360 正在运行，且已启用 Fusion MCP Server (端口 27182)
"""

import sys
import os

# 添加 src 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.mcp_client.fusion_mcp import connect, FusionMCPError
from src.fusion_tools.primitives import create_cube


def main():
    print("=" * 60)
    print("🚀 Fusion 360 AI Automation - Quick Start")
    print("=" * 60)
    
    # 1. 连接 Fusion MCP
    print("\n[1/4] 连接 Fusion MCP Server...")
    try:
        client = connect()
        print(f"    ✅ 已连接 (Session: {client.session_id[:8]}...)")
    except FusionMCPError as e:
        print(f"    ❌ 连接失败: {e}")
        print("    请确认 Fusion 360 正在运行，Preferences > General > API 已启用 Fusion MCP")
        return 1

    # 2. 检查许可证
    print("\n[2/4] 检查许可证...")
    try:
        lic = client.get_license()
        summary = lic.get("summary", {})
        print(f"    ✅ {lic.get('licenseTypeSummary', '?')} "
              f"(Student={summary.get('isStudent', False)})")
    except Exception as e:
        print(f"    ⚠️ 许可证查询异常: {e}")

    # 3. 创建立方体
    print("\n[3/4] 创建 20×20×20 立方体...")
    script = create_cube(20, 20, 20, name="QuickCube")
    try:
        result = client.execute_script(script)
        msg = result.get("message", str(result)) if isinstance(result, dict) else str(result)
        if "CREATED_CUBE" in msg:
            print(f"    ✅ 成功! {msg}")
        elif "ERROR" in msg:
            print(f"    ❌ {msg}")
            return 1
        else:
            print(f"    ℹ️ {msg}")
    except Exception as e:
        print(f"    ❌ 创建失败: {e}")
        return 1

    # 4. 截图
    print("\n[4/4] 获取截图...")
    try:
        shot = client.take_screenshot(direction="iso-top-right", height=800)
        if isinstance(shot, dict) and ("signed_url" in shot or "image_url" in shot):
            url = shot.get("signed_url") or shot.get("image_url")
            print(f"    ✅ 截图: {str(url)[:80]}...")
        else:
            print(f"    ℹ️ 截图结果: {str(shot)[:100]}")
    except Exception as e:
        print(f"    ⚠️ 截图异常（可能需要先保存文档）: {e}")

    # 清理
    client.disconnect()
    print("\n" + "=" * 60)
    print("🎉 快速体验完成! 去 Fusion 360 窗口看看那个立方体吧!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
