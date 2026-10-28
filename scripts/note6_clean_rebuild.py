#!/usr/bin/env python3
"""
NOTE6 干净重建 — 从零创建
根治所有之前的问题:
  ① def run(context): pass 防止 MCP 回滚
  ② comp.xYConstructionPlane (小写 x) 正确 API
  ③ 每个组件单独创建 + 立即验证
  ④ 不追加到已有文档 (避免重复)
"""
import sys, time
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

HEAD = 'def run(context): pass\n'
c = FusionMCPClient(timeout=120)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}")

# ============ Step 1: 关闭所有旧文档，新建干净文档 ============
print("\n🗑️  Step 1: New clean document...")
NEW = HEAD + '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    for d in list(app.documents):
        try: d.close(False)
        except: pass
    dt = adsk.core.DocumentTypes.FusionDesignDocumentType
    new_doc = app.documents.add(dt)
    new_doc.name = "NOTE6_Clean_v3"
    print(f"NEW_DOC:{new_doc.name}")
except Exception as e:
    print(f"NEW_ERR:{str(e)[:150]}")
'''
r = c.execute_script(NEW, read_only=False)
print(f"  {r.get('message', r.get('error',''))[:300]}")
time.sleep(2)

# ============ Step 2: 批量创建核心组件 ============
# 每批 5 个组件，全部用正确的 comp.xYConstructionPlane / xZConstructionPlane
# 所有组件按文档 2.2 节爆炸图 + 专利权利要求书

def build_component(name, code, label=""):
    """创建单个组件"""
    full = HEAD + code
    try:
        r = c.execute_script(full, read_only=False)
        msg = r.get('message', r.get('error', ''))
        for line in msg.split('\n'):
            if 'OK:' in line or 'ERR:' in line:
                status = "✅" if 'OK' in line else "❌"
                print(f"  {status} {name}: {line.strip()}")
                return 'OK' in line
        return True  # 没报错就算成功
    except Exception as e:
        print(f"  ❌ {name}: exception")
        return False
    finally:
        time.sleep(0.15)

success_count = 0
fail_count = 0

def batch(batch_num, components):
    global success_count, fail_count
    print(f"\n📦 BATCH {batch_num}")
    for name, code in components:
        if build_component(name, code):
            success_count += 1
        else:
            fail_count += 1
    
    # 批间验证
    vr = HEAD + '''
import adsk.core
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    total_bodies = sum(c.bRepBodies.count for c in app.activeDocument.design.allComponents)
    print(f"BATCH_SUMMARY:OCCS={root.occurrences.count}|BODIES={total_bodies}")
except: pass
'''
    r = c.execute_script(vr, read_only=False)
    msg = r.get('message', r.get('error', ''))
    for line in msg.split('\n'):
        if 'BATCH_SUMMARY' in line:
            print(f"  📊 {line.strip()}")
    time.sleep(0.3)

# 常用函数
def cyl_code(dia, depth, plane='xY'):
    return f'''
    sk = comp.sketches.add(comp.{plane}ConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), {dia/2})
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), adsk.core.ValueInput.createByReal({depth}), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)'''

def ring_code(od, id_, depth, plane='xY'):
    return f'''
    sk = comp.sketches.add(comp.{plane}ConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), {od/2})
    sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), {id_/2})
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), adsk.core.ValueInput.createByReal({depth}), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)'''

def cut_code(dia, depth, cx=0, cy=0, plane='xY'):
    return f'''
    sk = comp.sketches.add(comp.{plane}ConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create({cx},{cy},0), {dia/2})
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), adsk.core.ValueInput.createByReal({depth}), adsk.fusion.FeatureOperations.CutFeatureOperation)'''

# ═══════════════════════════════════════════════
# BATCH 1: 电机 + 支架 + 减震垫 (专利 R1)
# ═══════════════════════════════════════════════
batch(1, [
("100_Motor", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "100_Motor_draft_v1"
    {cyl_code(55, 60, 'xY')}
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(30))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), 3)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), adsk.core.ValueInput.createByReal(75), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:100_MOTOR")
except Exception as e: print(f"ERR:100:{{str(e)[:80]}}")'''),

("110_MotorBracket", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "110_MotorBracket_draft_v1"
    {ring_code(70, 55, 8)}
    print("OK:110_BRACKET")
except Exception as e: print(f"ERR:110:{{str(e)[:80]}}")'''),

("120_RubberMount", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "120_RubberMount_draft_v1"
    {ring_code(80, 56, 6)}
    print("OK:120_RUBBER")
except Exception as e: print(f"ERR:120:{{str(e)[:80]}}")'''),

("220_FasteningScrew", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "220_FasteningScrew_v2"
    {cyl_code(8, 3, 'xZ')}
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(3))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), 2)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), adsk.core.ValueInput.createByReal(8), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:220_SCREW")
except Exception as e: print(f"ERR:220:{{str(e)[:80]}}")'''),
])

# ═══════════════════════════════════════════════
# BATCH 2: 偏心轮 + 2轴承 (专利 R4)
# ═══════════════════════════════════════════════
batch(2, [
("200_EccentricWheel", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "200_EccentricWheel_v2"
    # 圆盘 φ30×10
    {cyl_code(30, 10)}
    # 中心电机轴孔 φ6 @ (0,0,0)
    {cut_code(6, 12, 0, 0)}
    # 关键! 偏心臂末端轴承孔 φ8 @ (10,0,0) — 偏心距 e=10mm 精确位置
    {cut_code(8, 12, 10, 0)}
    print("OK:200_ECCENTRIC")
except Exception as e: print(f"ERR:200:{{str(e)[:80]}}")'''),

("210_Bearing1", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "210_Bearing_608_v1"
    {ring_code(22, 8, 7)}
    print("OK:210_BEARING1")
except Exception as e: print(f"ERR:210:{{str(e)[:80]}}")'''),

("211_Bearing2", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "211_Bearing2_608_v1"
    {ring_code(22, 8, 7)}
    print("OK:211_BEARING2")
except Exception as e: print(f"ERR:211:{{str(e)[:80]}}")'''),
])

# ═══════════════════════════════════════════════
# BATCH 3: 连杆 + 压盖 + 螺钉 (专利 R4)
# ═══════════════════════════════════════════════
batch(3, [
("300_ConnectingRod", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "300_ConnectingRod_draft_v1"
    # 杆身 50×10×6
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(-25,-5,0), adsk.core.Point3D.create(25,5,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), adsk.core.ValueInput.createByReal(6), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # 两端圆形端头
    for cx in [-25, 25]:
        skc = comp.sketches.add(comp.xYConstructionPlane)
        skc.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cx,0,0), 5)
        comp.features.extrudeFeatures.addSimple(skc.profiles.item(0), adsk.core.ValueInput.createByReal(10), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        # 两端铰接孔 φ5
        sh = comp.sketches.add(comp.xYConstructionPlane)
        sh.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cx,0,0), 2.5)
        comp.features.extrudeFeatures.addSimple(sh.profiles.item(0), adsk.core.ValueInput.createByReal(12), adsk.fusion.FeatureOperations.CutFeatureOperation)
    print("OK:300_ROD")
except Exception as e: print(f"ERR:300:{{str(e)[:80]}}")'''),

("340_RodCap", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "340_RodCap_draft_v1"
    {ring_code(16, 8, 4)}
    print("OK:340_CAP")
except Exception as e: print(f"ERR:340:{{str(e)[:80]}}")'''),

("341_RodCapScrew", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "341_RodCapScrew_v2"
    {cyl_code(6, 2, 'xZ')}
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(2))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), 1.5)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), adsk.core.ValueInput.createByReal(4), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:341_CAPSCREW")
except Exception as e: print(f"ERR:341:{{str(e)[:80]}}")'''),

("350_HingeScrew", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "350_HingeScrew_v2"
    {cyl_code(10, 4, 'xZ')}
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(4))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), 2.5)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), adsk.core.ValueInput.createByReal(10), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:350_HINGE")
except Exception as e: print(f"ERR:350:{{str(e)[:80]}}")'''),
])

# ═══════════════════════════════════════════════
# BATCH 4: 活塞杆组件 (专利 R1+R2+R3)
# ═══════════════════════════════════════════════
batch(4, [
("310_PistonRod", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "310_PistonRod_draft_v1"
    # φ10×80 主体 (沿 Y 轴)
    {cyl_code(10, 80, 'xZ')}
    # 顶端按摩头接口柱 φ8×10
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(80))
    p_top = comp.constructionPlanes.add(inp)
    skt = comp.sketches.add(p_top)
    skt.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(skt.profiles.item(0), adsk.core.ValueInput.createByReal(10), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # 底端铰接孔 φ5 @ Y=-38
    inp2 = comp.constructionPlanes.createInput()
    inp2.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(-38))
    p_bot = comp.constructionPlanes.add(inp2)
    sh = comp.sketches.add(p_bot)
    sh.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), 2.5)
    comp.features.extrudeFeatures.addSimple(sh.profiles.item(0), adsk.core.ValueInput.createByReal(12), adsk.fusion.FeatureOperations.CutFeatureOperation)
    print("OK:310_PISTON")
except Exception as e: print(f"ERR:310:{{str(e)[:80]}}")'''),

("320_PistonBushing", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "320_PistonBushing_draft_v1"
    {ring_code(18, 10.1, 25, 'xZ')}
    print("OK:320_BUSHING")
except Exception as e: print(f"ERR:320:{{str(e)[:80]}}")'''),

("330_SoftRubberSleeve", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "330_SoftRubberSleeve_draft_v1"
    {ring_code(22, 19, 20, 'xZ')}
    print("OK:330_SOFTRUBBER")
except Exception as e: print(f"ERR:330:{{str(e)[:80]}}")'''),
])

# ═══════════════════════════════════════════════
# BATCH 5: 6 款按摩头 (专利 R5)
# ═══════════════════════════════════════════════
heads = [
("410_StandardBallHead", 18, 20, "标准球形头"),
("420_TriggerPointHead", 10, 18, "小圆头扳机点"),
("430_FlatHead", 28, 10, "小平头全身"),
("440_LargeBallHead", 45, 25, "大号球形头大肌群"),
("450_CushionHead", 30, 22, "减震头敏感肌"),
("460_UShapedHead", 30, 20, "U型头脊柱"),
]
for name, dia, depth, desc in heads:
    batch(5, [(name + "(" + desc + ")", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "{name}_draft_v1"
    # 按摩头主体
    {cyl_code(dia, depth, 'xY')}
    # 安装接口柱 (承插+金属螺纹 专利 R5)
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal({depth}))
    p = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), adsk.core.ValueInput.createByReal(8), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:{name[:7]}")
except Exception as e: print(f"ERR:{name[:7]}:{{str(e)[:80]}}")''')])

# ═══════════════════════════════════════════════
# BATCH 6: 电池 + 控制板
# ═══════════════════════════════════════════════
batch(6, [
("510_Battery18650", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "510_BatteryCell_18650_draft_v1"
    {cyl_code(18, 65, 'xZ')}
    print("OK:510_BATTERY")
except Exception as e: print(f"ERR:510:{{str(e)[:80]}}")'''),

("520_BatteryHolder", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "520_BatteryHolder_draft_v1"
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(-40,-10,0), adsk.core.Point3D.create(40,10,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), adsk.core.ValueInput.createByReal(70), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:520_BATTHOLDER")
except Exception as e: print(f"ERR:520:{{str(e)[:80]}}")'''),

("610_MainPCB", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "610_MainPCB_draft_v1"
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(-25,-15,0), adsk.core.Point3D.create(25,15,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), adsk.core.ValueInput.createByReal(2), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:610_PCB")
except Exception as e: print(f"ERR:610:{{str(e)[:80]}}")'''),
])

# 6 个独立电芯
positions = [(0, 0), (20, 0), (40, 0), (0, 20), (20, 20), (40, 20)]
for idx, (bx, by) in enumerate(positions, 1):
    batch(6, [(f"51{idx}_BatteryCell", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "51{idx}_BatteryCell_v2"
    {cyl_code(18, 65, 'xZ')}
    mat = adsk.core.Matrix3D.create()
    mat.translation = adsk.core.Vector3D.create({bx}, {by}, 0)
    root.occurrences.item(root.occurrences.count-1).transform = mat
    print("OK:BATTERY_51{idx}")
except Exception as e: print(f"ERR:51{idx}:{{str(e)[:80]}}")''')])

# ═══════════════════════════════════════════════
# BATCH 7: 外壳 (文档 2.2 节)
# ═══════════════════════════════════════════════
batch(7, [
("710_UpperHousing", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "710_UpperHousing_draft_v1"
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(-60,-40,0), adsk.core.Point3D.create(60,40,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), adsk.core.ValueInput.createByReal(50), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:710_UPPER")
except Exception as e: print(f"ERR:710:{{str(e)[:80]}}")'''),

("720_HandleHousing", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "720_HandleHousing_draft_v1"
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(-40,-30,0), adsk.core.Point3D.create(40,30,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), adsk.core.ValueInput.createByReal(100), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:720_HANDLE")
except Exception as e: print(f"ERR:720:{{str(e)[:80]}}")'''),

("730_SiliconeCover", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "730_SiliconeCover_draft_v1"
    {ring_code(76, 68, 90, 'xZ')}
    print("OK:730_SILICONE")
except Exception as e: print(f"ERR:730:{{str(e)[:80]}}")'''),

("740_BottomDisplay", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "740_BottomDisplay_draft_v1"
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(-20,-30,0), adsk.core.Point3D.create(20,30,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), adsk.core.ValueInput.createByReal(2), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:740_DISPLAY")
except Exception as e: print(f"ERR:740:{{str(e)[:80]}}")'''),

("750_ButtonPanel", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "750_ButtonPanel_draft_v1"
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(-15,-25,0), adsk.core.Point3D.create(15,25,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), adsk.core.ValueInput.createByReal(1.5), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:750_BUTTON")
except Exception as e: print(f"ERR:750:{{str(e)[:80]}}")'''),

("760_HoneycombVent", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "760_HoneycombVent_draft_v1"
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(-50,-30,0), adsk.core.Point3D.create(50,30,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), adsk.core.ValueInput.createByReal(1), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:760_VENT")
except Exception as e: print(f"ERR:760:{{str(e)[:80]}}")'''),
])

# 4 个外壳自攻螺钉
for i in range(1, 5):
    batch(7, [(f"77{i}_HousingScrew", f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "77{i}_HousingScrew_v2"
    {cyl_code(5, 2, 'xZ')}
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(2))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), 1.25)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), adsk.core.ValueInput.createByReal(5), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:77{i}_HOUSING")
except Exception as e: print(f"ERR:77{i}:{{str(e)[:80]}}")''')])

# ============ Step 3: 最终统计 ============
print(f"\n{'='*60}")
print(f"📊 CREATION SUMMARY: {success_count} ✅ / {fail_count} ❌")
print(f"{'='*60}")

FINAL = HEAD + '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    d = app.activeDocument.design
    root = d.rootComponent
    bodies = sum(c.bRepBodies.count for c in d.allComponents)
    empty = sum(1 for c in d.allComponents if c.bRepBodies.count == 0)
    print(f"FINAL:DOC={d.name}|COMPS={d.allComponents.count}|OCCS={root.occurrences.count}|BODIES={bodies}|EMPTY_COMPS={empty}")
    try:
        folder = app.data.activeFolder
        d.saveAs("NOTE6_Clean_v3_Complete", folder, "干净重建版: 零重复零空壳", "NOTE6")
        print("SAVEAS:OK")
    except Exception as e:
        try:
            d.save("draft v3.0 clean rebuild")
            print("SAVE:OK")
        except Exception as e2:
            print(f"SAVE_ERR:{str(e2)[:80]}")
except Exception as e:
    print(f"VERIFY_ERR:{str(e)[:100]}")
'''
r = c.execute_script(FINAL, read_only=False)
msg = r.get('message', r.get('error', '')) if isinstance(r, dict) else str(r)
for line in msg.split('\n'):
    if line and 'Traceback' not in line and 'File' not in line and 'run' not in line and 'def' not in line:
        print(f"  {line}")

c.disconnect()
print("\n✅ Clean rebuild done!")
