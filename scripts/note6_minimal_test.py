#!/usr/bin/env python3
"""最小化测试：创建 1 个组件后立即验证是否保留"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient
import socket

def mcp_ok():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    r = s.connect_ex(('127.0.0.1', 27182))
    s.close()
    return r == 0

c = FusionMCPClient(timeout=120)
c.connect()
print(f"STEP1_MCP:{'OK' if mcp_ok() else 'DEAD'}")

# 只创建 1 个组件 — 补全的偏心轮
TEST1 = '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    des_doc = app.activeDocument
    design = des_doc.design
    root = design.rootComponent
    print(f"BEFORE:{root.occurrences.count}")
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "200_EccentricWheel_v2"
    
    # 圆盘
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 15)
    comp.features.extrudeFeatures.addSimple(
        sk.profiles.item(0), vi(10),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # 中心孔 φ6 @ (0,0,0)
    sk2 = comp.sketches.add(comp.xYConstructionPlane)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 3)
    comp.features.extrudeFeatures.addSimple(
        sk2.profiles.item(0), vi(12),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
    
    # 偏心臂末端孔 φ8 @ (10,0,0) — 关键!
    sk3 = comp.sketches.add(comp.xYConstructionPlane)
    sk3.sketchCurves.sketchCircles.addByCenterRadius(pt3(10,0,0), 4)
    comp.features.extrudeFeatures.addSimple(
        sk3.profiles.item(0), vi(12),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
    
    print("CREATED:200_v2")
except Exception as e:
    print(f"ERR:{str(e)[:100]}")
'''

print("STEP2_Create 1 component...")
r = c.execute_script(TEST1, read_only=False)
print(f"   {r.get('message','')[:300]}")
print(f"STEP3_MCP:{'OK' if mcp_ok() else 'DEAD'}")

# 立即验证
VERIFY = '''
import adsk.core
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    names = [root.occurrences.item(i).component.name for i in range(root.occurrences.count)]
    print(f"VERIFY:{len(names)} occs")
    has_v2 = any('v2' in n for n in names)
    print(f"HAS_V2:{has_v2}")
    for n in names:
        if '200' in n: print(f"  FOUND:{n}")
except Exception as e:
    print(f"VERIFY_ERR:{str(e)[:80]}")
'''

if mcp_ok():
    print("STEP4_Verify...")
    r2 = c.execute_script(VERIFY, read_only=False)
    print(f"   {r2.get('message','')[:500]}")
    print(f"STEP5_MCP:{'OK' if mcp_ok() else 'DEAD'}")

c.disconnect()
