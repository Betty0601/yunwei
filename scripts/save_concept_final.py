#!/usr/bin/env python3
"""DMS Concept 保存到 Team Hub"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import connect
c = connect()

SCRIPT = '''
import adsk.core, adsk.fusion
app = adsk.core.Application.get()
doc = app.activeDocument
out = []

# 获取 defaultProject
project = app.data.dataProjects[0]
out.append(f"PROJ:{project.name}")

# saveAs 4 参数: name, folder, desc, version
ok = doc.saveAs("DMS_Concept_Assembly_Phase2", project.rootFolder, 
               "DMS Phase 2 Concept Assembly - 7 comps / 11 bodies / 15 params", 
               "P2-001")
out.append(f"SAVEAS:{ok}")
out.append(f"DOC:{doc.name}")
out.append(f"SAVED:{doc.isSaved}")
print("|".join(out))
'''

print("💾 saveAs DMS Concept...")
r = c.execute_script(SCRIPT, read_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(f"📋 {msg}")
print("\n📸 截图...")
print(c.take_screenshot())
c.disconnect()
