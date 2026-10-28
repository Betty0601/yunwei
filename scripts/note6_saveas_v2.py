#!/usr/bin/env python3
"""NOTE6 Final saveAs attempt 2"""
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
    
    # 尝试 activeFolder
    try:
        folder = app.data.activeFolder
        print(f"ACTIVE_FOLDER:{folder.name if folder else 'None'}")
        if folder:
            ok = des_doc.saveAs("NOTE6_Assembly_draft_v1", folder,
                               "NOTE6 完整爆炸图 — draft v1.0 — 26组件35体", "draft_v1.0")
            print(f"SAVEAS_OK:{ok}")
            print(f"IS_SAVED_NOW:{des_doc.isSaved}")
    except Exception as e:
        print(f"ACTIVE_FOLDER_ERR:{str(e)[:120]}")
    
except Exception as fatal:
    print(f"FATAL:{str(fatal)[:150]}")
'''

r = c.execute_script(SAVE_SCRIPT, read_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(msg[:1500])
c.disconnect()
