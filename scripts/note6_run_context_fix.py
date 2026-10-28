#!/usr/bin/env python3
"""最终修复: def run(context): pass (接受 MCP wrapper 的参数!)"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

HEAD = '''
def run(context): pass
'''

c = FusionMCPClient(timeout=120)
c.connect()
print("✅ MCP connected")

# 1. 关闭旧文档 + 新文档
NEW = '''
def run(context): pass
import adsk.core
try:
    app = adsk.core.Application.get()
    try:
        for d in list(app.documents):
            d.close(False)
    except: pass
    new_doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    new_doc.name = "NOTE6_Test_Fix"
    print(f"NEW_DOC:{new_doc.name}")
except Exception as e:
    print(f"ERR:{str(e)[:100]}")
'''
print("1. New doc...")
r = c.execute_script(NEW, read_only=False)
print(f"   {r.get('message', r.get('error',''))[:300]}")

import time

# 2. 创建组件 1: 电机
MAKE1 = HEAD + '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "100_Motor"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    # 外壳 φ55×60
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 27.5)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(60),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # 输出轴 φ6×75
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xYConstructionPlane, vi(30))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 3)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(75),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    print(f"MOTOR_CREATED:OCCS={root.occurrences.count}")
except Exception as e:
    print(f"MOTOR_ERR:{str(e)[:100]}")
'''
print("\n2. Make Motor...")
r = c.execute_script(MAKE1, read_only=False)
print(f"   {r.get('message', r.get('error',''))[:300]}")

time.sleep(1)

# 3. 立即验证
V = HEAD + '''
import adsk.core
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    print(f"VERIFY_OCCS:{root.occurrences.count}")
    for i in range(root.occurrences.count):
        print(f"  [{i}] {root.occurrences.item(i).component.name}")
except Exception as e:
    print(f"V_ERR:{str(e)[:100]}")
'''
print("\n3. Verify...")
r = c.execute_script(V, read_only=False)
print(f"   {r.get('message', r.get('error',''))[:500]}")

# 4. 创建第 2 个组件
MAKE2 = HEAD + '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "200_EccentricWheel"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 15)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(10),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # 中心孔 + 偏心臂孔 @10mm
    sk2 = comp.sketches.add(comp.xYConstructionPlane)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 3)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(10,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(12),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
    
    print(f"ECC_CREATED:OCCS={root.occurrences.count}")
except Exception as e:
    print(f"ECC_ERR:{str(e)[:100]}")
'''
print("\n4. Make Eccentric...")
r = c.execute_script(MAKE2, read_only=False)
print(f"   {r.get('message', r.get('error',''))[:300]}")

time.sleep(1)
print("\n5. Final verify...")
r = c.execute_script(V, read_only=False)
print(f"   {r.get('message', r.get('error',''))[:500]}")

c.disconnect()
