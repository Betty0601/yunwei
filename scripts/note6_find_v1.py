#!/usr/bin/env python3
"""找回 NOTE6_Assembly_draft_v1 + 在上面补全所有缺失组件"""
import sys, time
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

HEAD = 'def run(context): pass\n'
c = FusionMCPClient(timeout=120)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}")

# 关闭当前文档，尝试打开 v1
CLOSE_OPEN = HEAD + '''
import adsk.core
try:
    app = adsk.core.Application.get()
    # 关闭所有文档
    for d in list(app.documents):
        try: d.close(False)
        except: pass
    
    # 搜索最近文档找 NOTE6_Assembly
    recent = app.data.recentFiles
    print(f"RECENT_COUNT:{recent.count}")
    for i in range(recent.count):
        f = recent.item(i)
        nm = f.name
        if 'NOTE6' in nm or 'Assembly' in nm:
            print(f"FOUND_RECENT:{nm}")
            # 打开它
            try:
                app.data.open(f)
                print(f"OPENED:{nm}")
                break
            except Exception as e:
                print(f"OPEN_ERR:{str(e)[:80]}")
except Exception as e:
    print(f"CLOSE_ERR:{str(e)[:100]}")
'''
r = c.execute_script(CLOSE_OPEN, read_only=False)
print(f"Close/Open: {r.get('message', r.get('error',''))[:800]}")
time.sleep(5)

# 验证当前文档状态
VERIFY_NOW = HEAD + '''
import adsk.core
try:
    app = adsk.core.Application.get()
    print(f"DOCS_OPEN:{app.documents.count}")
    for i in range(app.documents.count):
        d = app.documents.item(i)
        print(f"  DOC:{d.name}")
    if app.activeDocument:
        root = app.activeDocument.design.rootComponent
        print(f"ACTIVE_OCCS:{root.occurrences.count}")
except Exception as e:
    print(f"V_ERR:{str(e)[:100]}")
'''
r = c.execute_script(VERIFY_NOW, read_only=False)
print(f"\nVerify: {r.get('message', r.get('error',''))[:500]}")

c.disconnect()
