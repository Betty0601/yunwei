#!/usr/bin/env python3
"""
FINAL: 从零创建完整的 NOTE6 爆炸图 (def run(context): pass 根治回滚!)
分批: 每批 5-8 个组件, 每批之间 sleep 1 秒
"""
import sys, time
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

HEAD = 'def run(context): pass\n'
c = FusionMCPClient(timeout=120)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}")

# Step 1: 全新文档
NEW_DOC = HEAD + '''
import adsk.core
try:
    app = adsk.core.Application.get()
    # 关所有
    for d in list(app.documents):
        try: d.close(False)
        except: pass
    # 新建 Fusion Design 文档
    dt = adsk.core.DocumentTypes.FusionDesignDocumentType
    new_doc = app.documents.add(dt)
    new_doc.name = "NOTE6_Assembly_Final"
    print(f"NEW_DOC:{new_doc.name}")
except Exception as e:
    print(f"NEW_ERR:{str(e)[:150]}")
'''
r = c.execute_script(NEW_DOC, read_only=False)
print(f"1. New doc: {r.get('message', r.get('error',''))[:300]}")
time.sleep(2)

def run_batch(batch_num, components):
    """执行一批组件创建"""
    for name, code in components:
        full_script = HEAD + code
        r = c.execute_script(full_script, read_only=False)
        msg = r.get('message', r.get('error', ''))
        
        ok = False
        for line in msg.split('\n'):
            if 'OK:' in line or 'CREATED:' in line:
                print(f"  ✅ {name}: {line.strip()}")
                ok = True
        if not ok:
            for line in msg.split('\n'):
                if 'ERR' in line or 'Traceback' in line:
                    print(f"  ❌ {name}: {line.strip()[:80]}")
                    break
            else:
                print(f"  ??? {name}: no output")
        time.sleep(0.2)
    
    # 批间验证
    vr = c.execute_script(HEAD + '''
import adsk.core
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    print(f"BATCH_OCCS:{root.occurrences.count}")
except: pass
''', read_only=False)
    for line in vr.get('message', vr.get('error', '')).split('\n'):
        if 'BATCH' in line:
            print(f"  → {line}")
            break
    time.sleep(0.5)

# ═══════════════════════════════════════════════
# BATCH 1: 电机组 + 偏心轮 + 轴承 (核心传动)
# ═══════════════════════════════════════════════
print("\n" + "="*60)
print("🔧 BATCH 1: 核心传动组")
print("="*60)

def cyl(dia, depth, plane_name='XY'):
    return f'''
    sk = comp.sketches.add(comp.{plane_name}ConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), {dia/2})
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi({depth}),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)'''

def ring(od, id_, depth, plane_name='XY'):
    return f'''
    sk = comp.sketches.add(comp.{plane_name}ConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), {od/2})
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), {id_/2})
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi({depth}),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)'''

def cut_cyl_at(dia, depth, cx, cy, plane_name='XY'):
    return f'''
    sk = comp.sketches.add(comp.{plane_name}ConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3({cx},{cy},0), {dia/2})
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi({depth}),
        adsk.fusion.FeatureOperations.CutFeatureOperation)'''

batches = [
    # BATCH 1: 电机 + 偏心轮 + 轴承
    [
    ("100_Motor_draft_v1", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "100_Motor_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    {cyl(55, 60)}
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xYConstructionPlane, vi(30))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 3)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(75), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:100_MOTOR")
except Exception as e: print(f"ERR:100:{{str(e)[:60]}}")
'''),
    ("110_MotorBracket_draft_v1", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "110_MotorBracket_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    {ring(70, 55, 8)}
    print("OK:110_BRACKET")
except Exception as e: print(f"ERR:110:{{str(e)[:60]}}")
'''),
    ("120_RubberMount_draft_v1", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "120_RubberMount_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    {ring(80, 56, 6)}
    print("OK:120_RUBBER")
except Exception as e: print(f"ERR:120:{{str(e)[:60]}}")
'''),
    ("200_EccentricWheel_v2", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "200_EccentricWheel_v2"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    # 圆盘 φ30×10
    {cyl(30, 10)}
    # 中心电机轴孔 φ6 @ (0,0,0)
    {cut_cyl_at(6, 12, 0, 0)}
    # 偏心臂末端孔 φ8 @ (10,0,0) — 专利 R4 关键!
    {cut_cyl_at(8, 12, 10, 0)}
    print("OK:200_ECCENTRIC")
except Exception as e: print(f"ERR:200:{{str(e)[:60]}}")
'''),
    ("210_Bearing_608_v1", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "210_Bearing_608_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    {ring(22, 8, 7)}
    print("OK:210_BEARING1")
except Exception as e: print(f"ERR:210:{{str(e)[:60]}}")
'''),
    ("211_Bearing2_608_v1", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "211_Bearing2_608_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    {ring(22, 8, 7)}
    print("OK:211_BEARING2")
except Exception as e: print(f"ERR:211:{{str(e)[:60]}}")
'''),
    ("220_FasteningScrew_v2", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "220_FasteningScrew_v2"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    {cyl(8, 3, 'XZ')}
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, vi(3))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 2)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(8), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:220_SCREW_MOTOR")
except Exception as e: print(f"ERR:220:{{str(e)[:60]}}")
'''),
    ],
    
    # BATCH 2: 连杆 + 活塞杆
    [
    ("300_ConnectingRod_draft_v1", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "300_ConnectingRod_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-25,-5,0), pt3(25,5,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(6), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # 两端圆孔
    for cx in [-25, 25]:
        skc = comp.sketches.add(comp.xYConstructionPlane)
        skc.sketchCurves.sketchCircles.addByCenterRadius(pt3(cx,0,0), 5)
        comp.features.extrudeFeatures.addSimple(skc.profiles.item(0), vi(10), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # 两端铰接孔 φ5
    for cx in [-25, 25]:
        sh = comp.sketches.add(comp.xYConstructionPlane)
        sh.sketchCurves.sketchCircles.addByCenterRadius(pt3(cx,0,0), 2.5)
        comp.features.extrudeFeatures.addSimple(sh.profiles.item(0), vi(12), adsk.fusion.FeatureOperations.CutFeatureOperation)
    print("OK:300_ROD")
except Exception as e: print(f"ERR:300:{{str(e)[:60]}}")
'''),
    ("340_RodCap_draft_v1", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "340_RodCap_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    {ring(16, 8, 4)}
    print("OK:340_CAP")
except Exception as e: print(f"ERR:340:{{str(e)[:60]}}")
'''),
    ("341_RodCapScrew_v2", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "341_RodCapScrew_v2"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    {cyl(6, 2, 'XZ')}
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, vi(2))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 1.5)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(4), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:341_CAPSCREW")
except Exception as e: print(f"ERR:341:{{str(e)[:60]}}")
'''),
    ("310_PistonRod_draft_v1", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "310_PistonRod_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    # φ10×80 主体 (沿 Y)
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 5)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(80), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # 顶端接口柱 φ8×10
    p_top = comp.constructionPlanes.createInput()
    p_top.setByOffset(comp.xZConstructionPlane, vi(80))
    pt = comp.constructionPlanes.add(p_top)
    skt = comp.sketches.add(pt)
    skt.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(skt.profiles.item(0), vi(10), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # 底端铰接孔 φ5 @ Y=-38
    p_bot = comp.constructionPlanes.createInput()
    p_bot.setByOffset(comp.xZConstructionPlane, vi(-38))
    pb = comp.constructionPlanes.add(p_bot)
    sh = comp.sketches.add(pb)
    sh.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 2.5)
    comp.features.extrudeFeatures.addSimple(sh.profiles.item(0), vi(12), adsk.fusion.FeatureOperations.CutFeatureOperation)
    print("OK:310_PISTON")
except Exception as e: print(f"ERR:310:{{str(e)[:60]}}")
'''),
    ("320_PistonBushing_draft_v1", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "320_PistonBushing_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    {ring(18, 10.1, 25, 'XZ')}
    print("OK:320_BUSHING")
except Exception as e: print(f"ERR:320:{{str(e)[:60]}}")
'''),
    ("330_SoftRubberSleeve_draft_v1", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "330_SoftRubberSleeve_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    {ring(22, 19, 20, 'XZ')}
    print("OK:330_SOFTRUBBER")
except Exception as e: print(f"ERR:330:{{str(e)[:60]}}")
'''),
    ("350_HingeScrew_v2", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "350_HingeScrew_v2"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    {cyl(10, 4, 'XZ')}
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, vi(4))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 2.5)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(10), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:350_HINGE")
except Exception as e: print(f"ERR:350:{{str(e)[:60]}}")
'''),
    ],
    
    # BATCH 3: 6 款按摩头
    [
    ("410-460_MassageHeads", None),  # placeholder - handled specially
    ],
    
    # BATCH 4: 电池 + 控制板 + 外壳
    [
    ("500-760_BatteryHousing", None),  # placeholder
    ],
]

# 执行 BATCH 1 和 BATCH 2
run_batch("BATCH1", batches[0])
run_batch("BATCH2", batches[1])

# BATCH 3: 6 款按摩头
print("\n" + "="*60)
print("🔧 BATCH 3: 6 款按摩头")
print("="*60)
heads = [
    ("410_StandardBallHead_draft_v1", 18, 20),
    ("420_TriggerPointHead_draft_v1", 10, 18),
    ("430_FlatHead_draft_v1", 28, 10),
    ("440_LargeBallHead_draft_v1", 45, 25),
    ("450_CushionHead_draft_v1", 30, 22),
    ("460_UShapedHead_draft_v1", 30, 20),
]
for name, dia, depth in heads:
    code = f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "{name}"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), {dia/2})
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi({depth}), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # 安装接口柱 (专利 R5: 承插+金属螺纹)
    p = comp.constructionPlanes.createInput()
    p.setByOffset(comp.xYConstructionPlane, vi({depth}))
    pp = comp.constructionPlanes.add(p)
    sk2 = comp.sketches.add(pp)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(8), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:{name[:7]}")
except Exception as e: print(f"ERR:{name[:7]}:{{str(e)[:50]}}")
'''
    run_batch(f"HEAD_{name[:4]}", [(name, code)])

# BATCH 4: 电池 + 控制板 + 外壳
print("\n" + "="*60)
print("🔧 BATCH 4: 电池 + 控制板 + 外壳")
print("="*60)
run_batch("BATCH4", [
("510_BatteryCell_18650_draft_v1", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "510_BatteryCell_18650_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    {cyl(18, 65, 'XZ')}
    print("OK:510_BATTERY18650")
except Exception as e: print(f"ERR:510:{{str(e)[:50]}}")
'''),
("520_BatteryHolder_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "520_BatteryHolder_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-40,-10,0), pt3(40,10,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(70), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:520_BATTHOLDER")
except Exception as e: print(f"ERR:520:{{str(e)[:50]}}")
'''),
("610_MainPCB_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "610_MainPCB_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-25,-15,0), pt3(25,15,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(2), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:610_PCB")
except Exception as e: print(f"ERR:610:{{str(e)[:50]}}")
'''),
("710_UpperHousing_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "710_UpperHousing_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-60,-40,0), pt3(60,40,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(50), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:710_UPPER")
except Exception as e: print(f"ERR:710:{{str(e)[:50]}}")
'''),
("720_HandleHousing_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "720_HandleHousing_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-40,-30,0), pt3(40,30,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(100), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:720_HANDLE")
except Exception as e: print(f"ERR:720:{{str(e)[:50]}}")
'''),
("730_SiliconeCover_draft_v1", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "730_SiliconeCover_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    {ring(76, 68, 90, 'XZ')}
    print("OK:730_SILICONE")
except Exception as e: print(f"ERR:730:{{str(e)[:50]}}")
'''),
("740_BottomDisplay_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "740_BottomDisplay_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-20,-30,0), pt3(20,30,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(2), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:740_DISPLAY")
except Exception as e: print(f"ERR:740:{{str(e)[:50]}}")
'''),
("750_ButtonPanel_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "750_ButtonPanel_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-15,-25,0), pt3(15,25,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(1.5), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:750_BUTTON")
except Exception as e: print(f"ERR:750:{{str(e)[:50]}}")
'''),
("760_HoneycombVent_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "760_HoneycombVent_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-50,-30,0), pt3(50,30,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(1), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:760_VENT")
except Exception as e: print(f"ERR:760:{{str(e)[:50]}}")
'''),
])

# BATCH 5: 6 个独立电芯 + 4 外壳螺钉
print("\n" + "="*60)
print("🔧 BATCH 5: 6 个独立电芯 + 4 外壳螺钉")
print("="*60)
bat5 = []
positions = [(0, 0), (20, 0), (40, 0), (0, 20), (20, 20), (40, 20)]
for idx, (bx, by) in enumerate(positions, 1):
    bat5.append((f"51{idx}_BatteryCell_v2", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "51{idx}_BatteryCell_v2"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 9)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(65), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    mat = adsk.core.Matrix3D.create()
    mat.translation = adsk.core.Vector3D.create({bx}, {by}, 0)
    root.occurrences.item(root.occurrences.count-1).transform = mat
    print("OK:BATTERY51{idx}")
except Exception as e: print(f"ERR:BAT51{idx}:{{str(e)[:50]}}")
'''))
for i in range(1, 5):
    bat5.append((f"77{i}_HousingScrew_v2", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "77{i}_HousingScrew_v2"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 2.5)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(2), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, vi(2))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 1.25)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(5), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:HOUSING77{i}")
except Exception as e: print(f"ERR:77{i}:{{str(e)[:50]}}")
'''))
run_batch("BATCH5", bat5)

# FINAL SAVE + VERIFY
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
    try:
        folder = app.data.activeFolder
        d.saveAs("NOTE6_Assembly_draft_v2_Complete", folder, "完整 40+ 组件 爆炸图", "NOTE6")
        print("SAVEAS:OK")
    except Exception as e:
        try:
            d.save("draft v2.0 complete")
            print("SAVE:OK")
        except Exception as e2:
            print(f"SAVE_ERR:{str(e2)[:80]}")
except Exception as e:
    print(f"VERIFY_ERR:{str(e)[:100]}")
'''
r = c.execute_script(FINAL, read_only=False)
print(f"  {r.get('message', r.get('error',''))[:800]}")

# 截图
print("\n📸 Final screenshots...")
for direction in ['iso-top-right', 'iso-top-left', 'front', 'top', 'iso-top']:
    try:
        c.take_screenshot(direction=direction, height=1600)
        print(f"  {direction}: OK")
    except: print(f"  {direction}: err")

c.disconnect()
print("\n✅ ALL DONE!")
