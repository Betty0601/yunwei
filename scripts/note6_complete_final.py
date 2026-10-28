#!/usr/bin/env python3
"""
NOTE6 补全脚本 - 根治版
每次创建 1 个组件 + 立即验证 + 即使 MCP 调用 run(context) 也不报错
"""
import sys, time
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

# ✅ 根治: 接受 MCP wrapper 的 context 参数
HEAD = 'def run(context): pass\n'

c = FusionMCPClient(timeout=120)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}")

# 先打开原来的文档
OPEN_SCRIPT = HEAD + '''
import adsk.core
try:
    app = adsk.core.Application.get()
    docs = [d for d in app.documents if "NOTE6_Assembly" in d.name]
    if docs:
        for d in docs[:-1]:
            try: d.close(False)
            except: pass
        docs[-1].activate()
        print(f"OPENED:{docs[-1].name}")
    else:
        print("NO_DOC_FOUND")
except Exception as e:
    print(f"ERR:{str(e)[:100]}")
'''
r = c.execute_script(OPEN_SCRIPT, read_only=False)
print(f"Open doc: {r.get('message', r.get('error',''))[:300]}")
time.sleep(2)

def run_one(name, code):
    """安全创建 1 个组件"""
    script = HEAD + code
    r = c.execute_script(script, read_only=False)
    msg = r.get('message', r.get('error', ''))
    # 打印有用的行
    for line in msg.split('\n'):
        if line and 'Traceback' not in line and 'File' not in line and 'run' not in line:
            print(f"  {line}")
    
    time.sleep(0.5)
    # 快速验证
    vr = c.execute_script(HEAD + '''
import adsk.core
try:
    app = adsk.core.Application.get()
    print(f"OCCS:{app.activeDocument.design.rootComponent.occurrences.count}")
except: pass
''', read_only=False)
    vmsg = vr.get('message', vr.get('error', ''))
    for line in vmsg.split('\n'):
        if 'OCCS' in line:
            print(f"    → {line}")
            break

print("\n" + "="*60)
print("📦 补全 NOTE6 缺失组件")
print("="*60)

# ═══════ 1. 精确版偏心轮 (带 10mm 处 φ8 孔) ═══════
print("\n🔩 [1/13] 200_EccentricWheel_v2")
run_one("Eccentric_v2", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "200_EccentricWheel_v2"
    
    # 圆盘 φ30×10
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 15)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(10),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # 中心电机轴孔 φ6 @ (0,0,0)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 3)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(12),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
    
    # 偏心臂末端孔 φ8 @ (10,0,0) — 专利 R4 关键!
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(10,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(12),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
    
    print("CREATED:ECCENTRIC_V2")
except Exception as e:
    print(f"ERR:{str(e)[:100]}")
''')

# ═══════ 2. 电机端紧固螺钉 ═══════
print("\n🔩 [2/13] 220_FasteningScrew_v2 (专利 R4)")
run_one("MotorScrew", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "220_FasteningScrew_v2"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    # 圆柱头
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(3),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # 螺杆
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, vi(3))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 2)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(8),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    print("CREATED:SCREW_MOTOR")
except Exception as e:
    print(f"ERR:{str(e)[:100]}")
''')

# ═══════ 3. 铰接螺钉 ═══════
print("\n🔩 [3/13] 350_HingeScrew_v2 (专利 R4)")
run_one("HingeScrew", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "350_HingeScrew_v2"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 5)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(4),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, vi(4))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 2.5)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(10),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    print("CREATED:HINGE_SCREW")
except Exception as e:
    print(f"ERR:{str(e)[:100]}")
''')

# ═══════ 4. 连杆压盖螺钉 ═══════
print("\n🔩 [4/13] 341_RodCapScrew_v2 (专利 R4)")
run_one("CapScrew", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "341_RodCapScrew_v2"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 3)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(2),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, vi(2))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 1.5)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(4),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    print("CREATED:CAP_SCREW")
except Exception as e:
    print(f"ERR:{str(e)[:100]}")
''')

# ═══════ 5-10. 6 个独立 18650 电芯 ═══════
positions = [
    (0, 0), (20, 0), (40, 0),  # 上排
    (0, 20), (20, 20), (40, 20),  # 下排
]
for idx, (bx, by) in enumerate(positions, 1):
    print(f"\n🔋 [{idx+4}/13] 51{idx}_BatteryCell_v2 @ ({bx},{by})")
    script = f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "51{idx}_BatteryCell_v2"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 9)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(65),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    mat = adsk.core.Matrix3D.create()
    mat.translation = adsk.core.Vector3D.create({bx}, {by}, 0)
    root.occurrences.item(root.occurrences.count-1).transform = mat
    
    print("CREATED:BATTERY_51{idx}")
except Exception as e:
    print(f"ERR:{{str(e)[:80]}}")
'''
    run_one(f"Battery_51{idx}", script)

# ═══════ 11-14. 4 个外壳自攻螺钉 ═══════
for i in range(1, 5):
    print(f"\n🔩 [{i+10}/13] 77{i}_HousingScrew_v2")
    script = f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "77{i}_HousingScrew_v2"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 2.5)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(2),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, vi(2))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 1.25)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(5),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    print("CREATED:HOUSING_SCREW_77{i}")
except Exception as e:
    print(f"ERR:{{str(e)[:80]}}")
'''
    run_one(f"HousingScrew_77{i}", script)

# ═══════ FINAL VERIFY + SAVE ═══════
print("\n" + "="*60)
print("📊 FINAL VERIFICATION & SAVE")
print("="*60)
FINAL = HEAD + '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    d = app.activeDocument
    design = d.design
    root = design.rootComponent
    bodies = sum(c.bRepBodies.count for c in design.allComponents)
    print(f"FINAL:DOC={d.name}|SAVED={d.isSaved}|COMPS={design.allComponents.count}|OCCS={root.occurrences.count}|BODIES={bodies}")
    
    # Save
    try:
        d.save("draft v1.0 — 40+ components complete")
        print("SAVE:OK")
    except Exception as e:
        print(f"SAVE:ERR:{str(e)[:80]}")
        
except Exception as e:
    print(f"VERIFY_ERR:{str(e)[:100]}")
'''
r = c.execute_script(FINAL, read_only=False)
print(f"  {r.get('message', r.get('error',''))[:1000]}")

# 截图
print("\n📸 Taking screenshots...")
for direction in ['iso-top-right', 'iso-top-left', 'front', 'top', 'iso-top']:
    try:
        c.take_screenshot(direction=direction, height=1600)
        print(f"  {direction}: OK")
    except Exception as e:
        print(f"  {direction}: err")

c.disconnect()
print("\n✅ All done!")
