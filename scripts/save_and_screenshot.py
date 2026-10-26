#!/usr/bin/env python3
"""保存 DMS Concept + 截图"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import connect
c = connect()

SCRIPT = '''
import adsk.core, adsk.fusion

app = adsk.core.Application.get()
doc = app.activeDocument
design = doc.design
out = []

# 先试简单 save (带描述)
try:
    doc.save("DMS Phase 2 Concept Assembly")
    out.append(f"SAVE_OK:{doc.name}")
except Exception as e1:
    out.append(f"SAVE_FAIL:{str(e1)[:60]}")
    # 试 saveAs 到本地
    try:
        import os
        local = os.path.expanduser("~/Documents/DMS_Concept_Assembly.f3d")
        doc.saveAs(local, "", True)
        out.append(f"SAVEAS_OK:{local}")
    except Exception as e2:
        out.append(f"SAVEAS_FAIL:{str(e2)[:60]}")

# 最终状态
out.append(f"FINAL:{doc.name}|saved={doc.isSaved}|comps={design.allComponents.count-1}|bodies={sum(cc.bRepBodies.count for cc in design.allComponents)}|params={design.userParameters.count}")

print("|".join(out))
'''

print("💾 保存 DMS Concept...")
r = c.execute_script(SCRIPT, read_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(f"\n📋 {msg}")
print("\n📸 截图...")
shot = c.take_screenshot()
print(f"   {shot}")
c.disconnect()
