#!/usr/bin/env python3
"""NOTE6 Final saveAs — 修复 API"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

c = FusionMCPClient(timeout=120)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}...")

SAVE_SCRIPT = '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    des_doc = app.activeDocument
    print(f"DOC:{des_doc.name}")
    print(f"IS_SAVED:{des_doc.isSaved}")
    
    # 方法 1: 通过 data API
    try:
        data = app.data
        print(f"DATA_TYPE:{type(data).__name__}")
        print(f"DATA_DIR:{[a for a in dir(data) if not a.startswith('_')]}")
    except Exception as e:
        print(f"DATA_API_ERR:{str(e)[:80]}")
    
    # 尝试获取 DataFolder (搜索 Fusion API)
    # app.data.activeProject.rootFolder 或者直接 app.rootFolder
    try:
        # 方案 A
        proj = app.data.activeProject
        if proj:
            folder = proj.rootFolder
            print(f"PROJ_FOLDER:{folder.name}")
            ok = des_doc.saveAs("NOTE6_Assembly_draft_v1", folder,
                               "NOTE6 完整爆炸图 — draft v1.0 — 26组件", "draft_v1.0")
            print(f"SAVEAS_A:{ok}")
        else:
            print("NO_ACTIVE_PROJECT")
    except Exception as ea:
        print(f"TRY_A_ERR:{str(ea)[:100]}")
    
except Exception as e:
    print(f"FATAL:{str(e)[:150]}")
'''

r = c.execute_script(SAVE_SCRIPT, read_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(msg[:2000])
c.disconnect()
