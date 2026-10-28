#!/usr/bin/env python3
"""极端测试: 全新文档 + 最小创建"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient
c = FusionMCPClient(timeout=120)
c.connect()

# 1. 全新文档
NEW_DOC = '''
def run(): pass
import adsk.core
try:
    app = adsk.core.Application.get()
    # 关闭当前活动文档 (如果有)
    try:
        if app.activeDocument:
            app.activeDocument.close(False)
    except: pass
    
    # 新建文档
    new_doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    new_doc.name = "NOTE6_Test_v3"
    print(f"NEW_DOC:{new_doc.name}")
except Exception as e:
    print(f"NEW_DOC_ERR:{str(e)[:100]}")
'''
print("1. New document...")
r = c.execute_script(NEW_DOC, read_only=False)
print(f"   {r.get('message', r.get('error',''))[:500]}")

# 2. 只创建 1 个组件 — 最简单的圆柱
MAKE1 = '''
def run(): pass
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    print(f"BEFORE:{root.occurrences.count}")
    
    # 最简单的组件创建
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = "TestCyl"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    sk = occ.component.sketches.add(occ.component.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), 10)
    occ.component.features.extrudeFeatures.addSimple(
        sk.profiles.item(0), vi(20),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    print(f"AFTER_CREATE:{root.occurrences.count}")
except Exception as e:
    print(f"ERR:{str(e)[:100]}")
'''
print("\n2. Make 1 cylinder...")
r = c.execute_script(MAKE1, read_only=False)
print(f"   {r.get('message', r.get('error',''))[:500]}")

# 3. 立即验证
VERIFY = '''
def run(): pass
import adsk.core
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    print(f"VERIFY:{root.occurrences.count}")
    for i in range(root.occurrences.count):
        print(f"  [{i}] {root.occurrences.item(i).component.name}")
except Exception as e:
    print(f"V_ERR:{str(e)[:100]}")
'''
import time; time.sleep(1)
print("\n3. Verify after 1s...")
r = c.execute_script(VERIFY, read_only=False)
print(f"   {r.get('message', r.get('error',''))[:500]}")

# 4. 再创建第 2 个组件
MAKE2 = '''
def run(): pass
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = "TestBlock"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    sk = occ.component.sketches.add(occ.component.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-5,-5,0), adsk.core.Point3D.create(5,5,0))
    occ.component.features.extrudeFeatures.addSimple(
        sk.profiles.item(0), vi(10),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    print(f"AFTER_MAKE2:{root.occurrences.count}")
except Exception as e:
    print(f"ERR2:{str(e)[:100]}")
'''
print("\n4. Make 2nd block...")
r = c.execute_script(MAKE2, read_only=False)
print(f"   {r.get('message', r.get('error',''))[:500]}")

time.sleep(1)
print("\n5. Final verify...")
r = c.execute_script(VERIFY, read_only=False)
print(f"   {r.get('message', r.get('error',''))[:500]}")

c.disconnect()
