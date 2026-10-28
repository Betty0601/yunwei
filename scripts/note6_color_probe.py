#!/usr/bin/env python3
"""NOTE6 上色 v3 — 用最简单的 Fusion API"""
import sys, time
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

HEAD = 'def run(context): pass\n'
c = FusionMCPClient(timeout=120)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}")

COLOR_SCRIPT = HEAD + '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    design = app.activeDocument.design
    root = design.rootComponent
    
    # 先看 Fusion 有哪些顶层 API 可用
    print(f"DIR_APP:material={hasattr(app, 'materialLibs')}")
    print(f"DIR_DESIGN:appearances={hasattr(design, 'appearances')}")
    
    # 看看 body 有什么属性
    first_body = None
    for i in range(root.occurrences.count):
        comp = root.occurrences.item(i).component
        if comp.bRepBodies.count > 0:
            first_body = comp.bRepBodies.item(0)
            break
    if first_body:
        attrs = [a for a in dir(first_body) if 'color' in a.lower() or 'appear' in a.lower()]
        print(f"BODY_COLOR_ATTRS:{attrs}")
    
    # 方法 1: 直接 setAppearance (如果有)
    # 方法 2: design.appearances.create
    # 让我试 design.appearances.addByCopy 用 NULL parent
    try:
        print(f"APPEARANCES_COUNT:{design.appearances.count}")
        for i in range(min(3, design.appearances.count)):
            app_obj = design.appearances.item(i)
            print(f"  [{i}]{app_obj.name}")
    except Exception as e:
        print(f"APPEARANCES_ERR:{str(e)[:60]}")
    
    # 方法3: 用 ProductLibraryService 或其他
    try:
        product_service = app.getProductLibraryService()
        print(f"HAS_PRODUCT_SERVICE:True")
    except:
        print(f"HAS_PRODUCT_SERVICE:False")
    
    # 列出 app 所有包含 'lib' 或 'appear' 的属性
    lib_attrs = [a for a in dir(app) if 'lib' in a.lower() or 'appear' in a.lower() or 'material' in a.lower()]
    print(f"APP_LIB_ATTRS:{lib_attrs}")
    
    # design 里的
    d_attrs = [a for a in dir(design) if 'lib' in a.lower() or 'appear' in a.lower() or 'material' in a.lower() or 'color' in a.lower()]
    print(f"DESIGN_ATTRS:{d_attrs}")
    
except Exception as fatal:
    print(f"FATAL:{str(fatal)[:200]}")
'''

print("🔍 Probing Fusion API for coloring...")
r = c.execute_script(COLOR_SCRIPT, read_only=False)
msg = r.get('message', r.get('error', '')) if isinstance(r, dict) else str(r)
for line in msg.split('\n'):
    if line and 'Traceback' not in line and 'File' not in line and 'run' not in line and 'def' not in line:
        print(f"  {line}")

c.disconnect()
