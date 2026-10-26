#!/usr/bin/env python3
"""导出 DMS Concept + 最终验证"""
import sys, os; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import connect
c = connect()

SCRIPT = '''
import adsk.core, adsk.fusion
app = adsk.core.Application.get()
doc = app.activeDocument
design = doc.design
root = design.rootComponent
out = []

# 最终验证
bc = sum(cc.bRepBodies.count for cc in design.allComponents)
pc = design.userParameters.count
cc = design.allComponents.count - 1
out.append(f"DOC:{doc.name}")
out.append(f"SAVED:{doc.isSaved}")
out.append(f"COMP:{cc}")
out.append(f"BODY:{bc}")
out.append(f"PARAM:{pc}")
out.append(f"JOINT:{root.joints.count}")

# 组件列表
for occ in root.occurrences:
    bcc = occ.component.bRepBodies.count
    out.append(f"COMPONENT:{occ.component.name}|bodies={bcc}")

# 参数列表
for i in range(min(pc, 15)):
    p = design.userParameters.item(i)
    out.append(f"PARAM:{p.name}={p.value}{p.unit}")

print("|".join(out))
'''

print("📊 最终验证...")
r = c.execute_script(SCRIPT, read_only=True)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(f"\n{msg}")

print("\n📸 尝试截图...")
shot = c.take_screenshot()
print(f"shot result: {shot}")

c.disconnect()
print("\n✅ DMS Concept Phase 2 完成!")
