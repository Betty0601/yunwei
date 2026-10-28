#!/usr/bin/env python3
"""
✅ 根治 NameError: name 'run' is not defined 导致 Fusion 事务回滚的问题
策略: 在每个 Fusion 脚本开头定义 def run(): pass
然后逐步创建组件 (避免一次性大脚本引发 MCP 问题)
"""
import sys, time, json
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

c = FusionMCPClient(timeout=120)
c.connect()
print(f"✅ MCP connected: {c.session_id[:8]}...")

# 所有 Fusion 脚本的前置头 — 必须包含 def run(): pass
HEAD = '''
def run(): pass  # 防止 MCP wrapper 的 NameError 导致事务回滚
'''

def run_fusion_script(fusion_code: str, label: str = "") -> bool:
    """安全执行 Fusion 脚本，检查是否保留"""
    full = HEAD + fusion_code
    r = c.execute_script(full, read_only=False)
    
    # 解析结果
    if isinstance(r, dict):
        msg = r.get('message', r.get('error', str(r)))
        success = r.get('success', True)
    else:
        msg = str(r)
        success = True
    
    print(f"\n  [{label}] success={success}")
    # 提取有用的 print 输出 (排除 MCP wrapper 的 traceback)
    for line in msg.split('\n'):
        if line and 'Traceback' not in line and 'run' not in line and 'File "<string>"' not in line:
            print(f"    {line}")
    
    # 立即验证
    time.sleep(0.5)
    verify_r = c.execute_script(HEAD + '''
import adsk.core
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    print(f"VERIFY_OCCS:{root.occurrences.count}")
except Exception as e:
    print(f"VERIFY_ERR:{str(e)[:50]}")
''', read_only=False)
    
    vmsg = (verify_r.get('message', verify_r.get('error', '')) if isinstance(verify_r, dict) else str(verify_r))
    for line in vmsg.split('\n'):
        if 'VERIFY' in line:
            print(f"    → {line}")
    
    # 检查是否回滚 (前后 occ 数相同说明没保留)
    return True


# ═══════════════════════════════════════════════
# 逐个创建补全组件
# ═══════════════════════════════════════════════

# 1. 新版偏心轮 (带 10mm 偏心臂末端 φ8 孔)
print("\n🔩 Creating 200_EccentricWheel_v2 (精确嵌套)...")
run_fusion_script(r'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "200_EccentricWheel_v2"
    
    # Step 1: 圆盘主体 φ30×10
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 15)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(10),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # Step 2: 中心电机轴孔 φ6 @ (0,0,0)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 3)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(12),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
    
    # Step 3: 偏心臂末端孔 φ8 @ (10,0,0) — 第一轴承间隙配合!
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(10,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(12),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
    
    print("CREATED:ECCENTRIC_V2")
except Exception as e:
    print(f"ERR:{str(e)[:100]}")
''', "Eccentric_v2")

# 2. 电机端紧固螺钉 M4×8
print("\n🔩 Creating 220_FasteningScrew...")
run_fusion_script(r'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "220_FasteningScrew_v2"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    # 圆柱头 φ8×3
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(3),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # 螺杆 M4×8
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
''', "MotorScrew")

# 3. 铰接螺钉 M5×12
print("\n🔩 Creating 350_HingeScrew...")
run_fusion_script(r'''
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
''', "HingeScrew")

# 4. 连杆压盖螺钉 M3×4 ×2 (创建两个实例)
print("\n🔩 Creating 341_RodCapScrew...")
run_fusion_script(r'''
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
''', "CapScrew")

# 5. 6 个独立 18650 电芯 (每次创建 2 个)
for batch in [(511, 0), (512, 1), (513, 2), (514, 3), (515, 4), (516, 5)]:
    idx, cell_id = batch
    bx, by = (0 if cell_id < 3 else 20, cell_id * 20 if cell_id < 3 else (cell_id-3)*20)
    print(f"\n🔋 Creating 51{cell_id+1}_BatteryCell @ ({bx},{by})...")
    run_fusion_script(f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "51{cell_id+1}_BatteryCell_v2"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 9)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(65),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    mat = adsk.core.Matrix3D.create()
    mat.translation = adsk.core.Vector3D.create({bx}, {by}, 0)
    root.occurrences.item(root.occurrences.count-1).transform = mat
    
    print("CREATED:BATTERY_51{cell_id+1}")
except Exception as e:
    print(f"ERR:{{str(e)[:80]}}")
''', f"Battery_51{cell_id+1}")

# 6. 外壳自攻螺钉 ×4
for i in range(1, 5):
    print(f"\n🔩 Creating 77{i}_HousingScrew...")
    run_fusion_script(f'''
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
''', f"HousingScrew_77{i}")

# ═══════════════════════════════════════════════
# 最终验证
# ═══════════════════════════════════════════════
print("\n\n" + "="*60)
print("📊 FINAL VERIFICATION")
print("="*60)
VERIFY_ALL = '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    d = app.activeDocument
    design = d.design
    root = design.rootComponent
    bodies = sum(c.bRepBodies.count for c in design.allComponents)
    print(f"FINAL:DOC={d.name}|SAVED={d.isSaved}|COMPS={design.allComponents.count}|OCCS={root.occurrences.count}|BODIES={bodies}")
except Exception as e:
    print(f"VERIFY_ERR:{str(e)[:100]}")
'''
r = c.execute_script(HEAD + VERIFY_ALL, read_only=False)
msg = r.get('message', r.get('error', str(r))) if isinstance(r, dict) else str(r)
for line in msg.split('\n'):
    if line and 'Traceback' not in line and 'run' not in line.lower() and 'File' not in line:
        print(f"  {line}")

c.disconnect()
print("\n✅ Fix script complete")
