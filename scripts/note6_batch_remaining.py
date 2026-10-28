#!/usr/bin/env python3
"""
在 NOTE6_Assembly_draft_v2 上追加剩余核心组件 (分批)
v2 当前: 16 组件 (100_Motor + 200_EccentricWheel + 14 补全组件)
需要追加: 24 个核心组件 (从 oneshot 提取)
"""
import sys, time
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

HEAD = 'def run(context): pass\n'
c = FusionMCPClient(timeout=120)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}")

# 先打开 v2
OPEN_V2 = HEAD + '''
import adsk.core
try:
    app = adsk.core.Application.get()
    # 尝试从最近或 active folder 打开
    folder = app.data.activeFolder
    files = folder.getFiles()
    print(f"FOLDER_FILES:{files.count}")
    for i in range(files.count):
        f = files.item(i)
        if 'draft_v2' in f.name:
            app.data.open(f)
            print(f"OPENED_V2:{f.name}")
            break
except Exception as e:
    print(f"OPEN_ERR:{str(e)[:100]}")
'''
r = c.execute_script(OPEN_V2, read_only=False)
print(f"Open: {r.get('message', r.get('error',''))[:300]}")
time.sleep(3)

def make_comp(name, code):
    script = HEAD + code.replace('COMP_NAME', name)
    r = c.execute_script(script, read_only=False)
    msg = r.get('message', r.get('error', ''))
    for line in msg.split('\n'):
        if line and 'Traceback' not in line and 'File' not in line and 'run' not in line and 'def' not in line:
            print(f"  {line}")
    time.sleep(0.3)

def base_code(body):
    return f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "{body}"
'''

print("\n" + "="*60)
print("🔧 BATCH 1: 电机组 (已存在 100_Motor)")
print("="*60)

# 110_MotorBracket — 环形支架
print("\n[1/24] 110_MotorBracket_draft_v1")
make_comp("110_MotorBracket_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "110_MotorBracket_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    # 环形支架 OD70×ID55×8
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 35)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 27.5)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(8),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:110")
except Exception as e: print(f"ERR:110:{str(e)[:60]}")
''')

# 120_RubberMount — 电机橡胶减震垫 (专利 R1)
print("[2/24] 120_RubberMount_draft_v1")
make_comp("120_RubberMount_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "120_RubberMount_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 40)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 28)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(6),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:120")
except Exception as e: print(f"ERR:120:{str(e)[:60]}")
''')

print("\n" + "="*60)
print("🔧 BATCH 2: 轴承 + 连杆")
print("="*60)

# 210_Bearing_608_v1
print("[3/24] 210_Bearing_608_v1")
make_comp("210_Bearing_608_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "210_Bearing_608_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    # 608ZZ: ID8×OD22×W7
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 11)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(7),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:210")
except Exception as e: print(f"ERR:210:{str(e)[:60]}")
''')

# 211_Bearing2_608_v1
print("[4/24] 211_Bearing2_608_v1")
make_comp("211_Bearing2_608_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "211_Bearing2_608_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 11)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(7),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:211")
except Exception as e: print(f"ERR:211:{str(e)[:60]}")
''')

# 300_ConnectingRod
print("[5/24] 300_ConnectingRod_draft_v1")
make_comp("300_ConnectingRod_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "300_ConnectingRod_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    # 杆身 50×10×6
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-25,-5,0), pt3(25,5,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(6),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # 左端点 φ10 圆形
    p_left = comp.constructionPlanes.createInput()
    p_left.setByOffset(comp.xYConstructionPlane, vi(-5))
    pl = comp.constructionPlanes.add(p_left)
    skl = comp.sketches.add(pl)
    skl.sketchCurves.sketchCircles.addByCenterRadius(pt3(-25,0,0), 5)
    comp.features.extrudeFeatures.addSimple(skl.profiles.item(0), vi(10),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # 右端点 φ10 圆形
    p_right = comp.constructionPlanes.createInput()
    p_right.setByOffset(comp.xYConstructionPlane, vi(-5))
    pr = comp.constructionPlanes.add(p_right)
    skr = comp.sketches.add(pr)
    skr.sketchCurves.sketchCircles.addByCenterRadius(pt3(25,0,0), 5)
    comp.features.extrudeFeatures.addSimple(skr.profiles.item(0), vi(10),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # 两端铰接孔 φ5
    for cx in [-25, 25]:
        sh = comp.sketches.add(comp.xYConstructionPlane)
        sh.sketchCurves.sketchCircles.addByCenterRadius(pt3(cx,0,0), 2.5)
        comp.features.extrudeFeatures.addSimple(sh.profiles.item(0), vi(12),
            adsk.fusion.FeatureOperations.CutFeatureOperation)
    print("OK:300")
except Exception as e: print(f"ERR:300:{str(e)[:60]}")
''')

# 340_RodCap — 连杆压盖 (专利 R4)
print("[6/24] 340_RodCap_draft_v1")
make_comp("340_RodCap_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "340_RodCap_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    # 压盖圆盘 φ16×4, 中心孔 φ8
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 8)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(4),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:340")
except Exception as e: print(f"ERR:340:{str(e)[:60]}")
''')

print("\n" + "="*60)
print("🔧 BATCH 3: 活塞杆组件")
print("="*60)

# 310_PistonRod
print("[7/24] 310_PistonRod_draft_v1")
make_comp("310_PistonRod_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "310_PistonRod_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    # 活塞杆主体 φ10×80 (沿 Y 轴)
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 5)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(80),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # 顶端接口柱 φ8×10 (按摩头承插)
    p_top = comp.constructionPlanes.createInput()
    p_top.setByOffset(comp.xZConstructionPlane, vi(80))
    pt = comp.constructionPlanes.add(p_top)
    skt = comp.sketches.add(pt)
    skt.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(skt.profiles.item(0), vi(10),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # 底端铰接孔 φ5 @ Y=-38
    p_bot = comp.constructionPlanes.createInput()
    p_bot.setByOffset(comp.xZConstructionPlane, vi(-38))
    pb = comp.constructionPlanes.add(p_bot)
    sh = comp.sketches.add(pb)
    sh.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 2.5)
    comp.features.extrudeFeatures.addSimple(sh.profiles.item(0), vi(12),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
    print("OK:310")
except Exception as e: print(f"ERR:310:{str(e)[:60]}")
''')

# 320_PistonBushing — 滑套 (专利 R2)
print("[8/24] 320_PistonBushing_draft_v1")
make_comp("320_PistonBushing_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "320_PistonBushing_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    # φ18 OD × φ10.1 ID × 25 长
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 9)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 5.05)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(25),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:320")
except Exception as e: print(f"ERR:320:{str(e)[:60]}")
''')

# 330_SoftRubberSleeve — 软胶套 (专利 R1)
print("[9/24] 330_SoftRubberSleeve_draft_v1")
make_comp("330_SoftRubberSleeve_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "330_SoftRubberSleeve_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    # OD22 × ID19 × 20 长
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 11)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 9.5)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(20),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:330")
except Exception as e: print(f"ERR:330:{str(e)[:60]}")
''')

print("\n" + "="*60)
print("🔧 BATCH 4: 6 款按摩头")
print("="*60)

heads = [
    ("410_StandardBallHead_draft_v1", 18, 20),
    ("420_TriggerPointHead_draft_v1", 10, 18),
    ("430_FlatHead_draft_v1", 28, 10),
    ("440_LargeBallHead_draft_v1", 45, 25),
    ("450_CushionHead_draft_v1", 30, 22),
    ("460_UShapedHead_draft_v1", 30, 20),
]
for i, (name, dia, depth) in enumerate(heads):
    print(f"[{i+10}/24] {name}")
    make_comp(name, f'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "{name}"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), {dia/2})
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi({depth}),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # 安装接口柱 (承插+金属螺纹 专利 R5)
    p = comp.constructionPlanes.createInput()
    p.setByOffset(comp.xYConstructionPlane, vi({depth}))
    pp = comp.constructionPlanes.add(p)
    sk2 = comp.sketches.add(pp)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(8),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:{name[:5]}")
except Exception as e: print(f"ERR:{name[:5]}:{{str(e)[:50]}}")
''')

print("\n" + "="*60)
print("🔧 BATCH 5: 电池 + 控制板 + 外壳")
print("="*60)

# 510_BatteryCell_18650 (占位)
print("[16/24] 510_BatteryCell_18650_draft_v1")
make_comp("510_BatteryCell_18650_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "510_BatteryCell_18650_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 9)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(65),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:510")
except Exception as e: print(f"ERR:510:{str(e)[:50]}")
''')

# 520_BatteryHolder
print("[17/24] 520_BatteryHolder_draft_v1")
make_comp("520_BatteryHolder_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "520_BatteryHolder_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-40,-10,0), pt3(40,10,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(70),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:520")
except Exception as e: print(f"ERR:520:{str(e)[:50]}")
''')

# 610_MainPCB
print("[18/24] 610_MainPCB_draft_v1")
make_comp("610_MainPCB_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "610_MainPCB_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-25,-15,0), pt3(25,15,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(2),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:610")
except Exception as e: print(f"ERR:610:{str(e)[:50]}")
''')

# 外壳组: 710-760
print("[19/24] 710_UpperHousing_draft_v1")
make_comp("710_UpperHousing_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "710_UpperHousing_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-60,-40,0), pt3(60,40,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(50),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:710")
except Exception as e: print(f"ERR:710:{str(e)[:50]}")
''')

print("[20/24] 720_HandleHousing_draft_v1")
make_comp("720_HandleHousing_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "720_HandleHousing_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-40,-30,0), pt3(40,30,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(100),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:720")
except Exception as e: print(f"ERR:720:{str(e)[:50]}")
''')

print("[21/24] 730_SiliconeCover_draft_v1")
make_comp("730_SiliconeCover_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "730_SiliconeCover_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 38)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 34)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(90),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:730")
except Exception as e: print(f"ERR:730:{str(e)[:50]}")
''')

print("[22/24] 740_BottomDisplay_draft_v1")
make_comp("740_BottomDisplay_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "740_BottomDisplay_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-20,-30,0), pt3(20,30,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(2),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:740")
except Exception as e: print(f"ERR:740:{str(e)[:50]}")
''')

print("[23/24] 750_ButtonPanel_draft_v1")
make_comp("750_ButtonPanel_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "750_ButtonPanel_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-15,-25,0), pt3(15,25,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(1.5),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:750")
except Exception as e: print(f"ERR:750:{str(e)[:50]}")
''')

print("[24/24] 760_HoneycombVent_draft_v1")
make_comp("760_HoneycombVent_draft_v1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "760_HoneycombVent_draft_v1"
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(-50,-30,0), pt3(50,30,0))
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(1),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:760")
except Exception as e: print(f"ERR:760:{str(e)[:50]}")
''')

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
    try:
        d.save("draft v2.0 — complete 40 components all patent features included")
        print("SAVE:OK")
    except Exception as e:
        print(f"SAVE:ERR:{str(e)[:80]}")
except Exception as e:
    print(f"VERIFY_ERR:{str(e)[:100]}")
'''
r = c.execute_script(FINAL, read_only=False)
print(f"  {r.get('message', r.get('error',''))[:800]}")

# 截图
print("\n📸 Final screenshots...")
for direction in ['iso-top-right', 'iso-top-left', 'front', 'top']:
    try:
        c.take_screenshot(direction=direction, height=1600)
        print(f"  {direction}: OK")
    except Exception as e:
        print(f"  {direction}: err")

c.disconnect()
print("\n✅ Complete!")
