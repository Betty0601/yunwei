#!/usr/bin/env python3
"""
多原语测试：创建多个几何体并验证

运行前确保 Fusion 360 已打开或通过 API 创建新文档。
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.mcp_client.fusion_mcp import connect
from src.fusion_tools.primitives import create_cube, create_cylinder, create_bracket

def main():
    client = connect()
    print(f"✅ Connected (session: {client.session_id[:8]}...)")

    tests = [
        ("Cube 15×15×15", create_cube(15, 15, 15, "TestCube")),
        ("Cylinder r=10 h=30", create_cylinder(10, 30, "TestCylinder")),
        ("Bracket 40×30×5", create_bracket(40, 30, 5, 8, "TestBracket")),
    ]

    for name, script in tests:
        print(f"\n🔨 Creating {name}...")
        result = client.execute_script(script)
        msg = result.get("message", "") if isinstance(result, dict) else str(result)
        if "CREATED" in msg:
            print(f"   ✅ {msg.splitlines()[0]}")
        elif "ERROR" in msg:
            print(f"   ❌ {msg}")
        else:
            print(f"   ℹ️ {msg[:100]}")

    # 获取当前打开的文档
    docs = client.get_open_documents()
    print(f"\n📄 Open documents: {docs.get('message', '?')}")

    client.disconnect()
    print("\n🎉 All tests done!")


if __name__ == "__main__":
    main()
