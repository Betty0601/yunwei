\#!/usr/bin/env python3
"""
NOTE6 Complete Build — Step 1 + Step 2 + Step 3 (fixed APIs)
单个 Fusion 脚本完成: 文档 + 参数 + 7组件 + 爆炸视图 + saveAs
"""
import sys; sys.path.insert(0, '.')
from src.mcp\_client.fusion\_mcp import FusionMCPClient

c = FusionMCPClient(timeout=300)
c.connect()
print(f"✅ MCP Session: {c.session\_id\[:8]}...")

FULL\_SCRIPT = r'''
import adsk.core, adsk.fusion, traceback

app = adsk.core.Application.get()
ui = app.userInterface
log = \[]

def vi(v): return adsk.core.ValueInput.createByReal(v)
def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
def vec3(x,y,z): return adsk.core.Vector3D.create(x,y,z)

def safe\_exec(fn, name):
"""try/except 包装"""
try:
fn()
log.append(f"OK:{name}")
except Exception as e:
log.append(f"ERR:{name}:{str(e)\[:80]}")

try:
\# ═══════════════════════════════════════════
\# PART 1: 文档 + 参数
\# ═══════════════════════════════════════════
des\_doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType, True)
des\_doc.name = "NOTE6\_Assembly\_draft\_v1"
design = des\_doc.design
root = design.rootComponent
log.append(f"DOC:{des\_doc.name}")

```
# 35 个 UserParameters (draft v1.0)
params_def = [
    # 运动学
    ("amplitude",        10.0, "mm",    "单机振幅 A — 硬指标 10±0.1mm"),
    ("eccentricity",     10.0, "mm",    "偏心距 e = A"),
    ("stroke",           20.0, "mm",    "峰-峰行程 S = 2e — 硬指标 20±0.2mm"),
    ("rod_length",       50.0, "mm",    "连杆长度 L — 估计值，待拆机"),
    ("rod_ratio",         0.2, "",      "连杆比 λ = e/L ≤ 0.25"),
    ("max_rod_angle",    11.5, "deg",   "连杆最大摆角 ≤ 15°"),
    # 频率
    ("rpm_1",          2100.0, "rpm",   "1档"),
    ("rpm_5",          3300.0, "rpm",   "5档设计基准"),
    ("freq_5",           55.0, "Hz",    "5档频率"),
    # 电机
    ("motor_od",         55.0, "mm",    "电机外径 — PRO6 官网"),
    ("motor_length",     60.0, "mm",    "电机长度 估计"),
    ("motor_shaft_d",     6.0, "mm",    "电机输出轴 φ6"),
    # 轴承 608ZZ
    ("bearing_id",        8.0, "mm",    "608ZZ d=8"),
    ("bearing_od",       22.0, "mm",    "608ZZ D=22"),
    ("bearing_width",     7.0, "mm",    "608ZZ B=7"),
    # 活塞杆
    ("piston_d",         10.0, "mm",    "活塞杆 φ10"),
    ("piston_l",         80.0, "mm",    "活塞杆总长 估计"),
    # 滑套
    ("bushing_od",       18.0, "mm",    "滑套外径 估计"),
    ("bushing_id",       10.1, "mm",    "滑套内径 间隙配合"),
    ("bushing_l",        25.0, "mm",    "滑套长度 估计"),
    # 按摩头
    ("massage_head_d",   40.0, "mm",    "标准球头 φ40"),
]
params = design.userParameters
for nm, val, unit, desc in params_def:
    if not params.itemByName(nm):
        params.add(nm, vi(val), unit, desc)
log.append(f"PARAMS:{len(params_def)}")

# ═══════════════════════════════════════════
# PART 2: 辅助函数
# ═══════════════════════════════════════════

def new_comp(parent, name):
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ.component

def offset_plane(comp, base_plane, distance):
    """用 Fusion 2026+ API 创建偏移构造平面"""
    inp = comp.constructionPlanes.createInput()
    inp.setByOffsetDistance(base_plane, vi(distance))
    return comp.constructionPlanes.add(inp)

def extrude_cyl(comp, diameter, depth, sketch_plane):
    """画圆 + 拉伸圆柱"""
    sk = comp.sketches.add(sketch_plane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), diameter/2)
    f = comp.features.extrudeFeatures.addSimple(
        sk.profiles.item(0), vi(depth),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    return f

def extrude_cut(comp, sketch_plane, width, depth):
    """在给定平面画矩形 + 拉伸切除"""
    sk = comp.sketches.add(sketch_plane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(
        pt3(-width/2, -width/2, 0), pt3(width/2, width/2, 0))
    f = comp.features.extrudeFeatures.addSimple(
        sk.profiles.item(0), vi(depth),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
    return f

def cylinder_with_hole(comp, od, hole_d, depth, sketch_plane):
    """先拉外链圆柱，再切中心孔"""
    # 画两个同心圆 → Fusion 会自动识别环形 profile
    sk = comp.sketches.add(sketch_plane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), od/2)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), hole_d/2)
    # profiles.item(0) 是外圆内部，profiles.item(1) 是环形
    # 我们用 item(1) — 环形
    if sk.profiles.count >= 2:
        prof = sk.profiles.item(1)  # 环形轮廓
    else:
        prof = sk.profiles.item(0)  # fallback
    f = comp.features.extrudeFeatures.addSimple(
        prof, vi(depth),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    return f

# ═══════════════════════════════════════════
# PART 3: 7 组件建模
# ═══════════════════════════════════════════

# ── C1: 电机 100_Motor_draft_v1 ──
def build_motor():
    c = new_comp(root, "100_Motor_draft_v1")
    # 电机外壳 φ55×60mm (沿 Y 轴)
    extrude_cyl(c, 55, 60, c.xZConstructionPlane)
    # 输出轴 φ6×75mm (从外壳顶端伸出)
    top = offset_plane(c, c.xZConstructionPlane, 30)
    extrude_cyl(c, 6, 75, top)
safe_exec(build_motor, "C1_MOTOR")

# ── C2: 偏心轮 200_EccentricWheel_draft_v1 ──
def build_eccentric():
    c = new_comp(root, "200_EccentricWheel_draft_v1")
    # 圆盘 φ30×10mm
    extrude_cyl(c, 30, 10, c.xYConstructionPlane)
    # 中心电机轴孔 φ6
    sk = c.sketches.add(c.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 3)
    c.features.extrudeFeatures.addSimple(
        sk.profiles.item(0), vi(12),
        adsk.fusion.FeatureOperations.CutFeatureOperation)

    # 偏心臂: 中心在 x=10, 宽12, 厚6, 两端圆弧
    # 用矩形主体 + 两端圆头 (拉两个圆柱做布尔合并)
    mid_plane = offset_plane(c, c.xYConstructionPlane, 5)
    # 臂主体矩形: x 从 4 到 16, y 从 -6 到 6
    sk2 = c.sketches.add(mid_plane)
    sk2.sketchCurves.sketchLines.addTwoPointRectangle(
        pt3(4, -6, 0), pt3(16, 6, 0))
    f_arm = c.features.extrudeFeatures.addSimple(
        sk2.profiles.item(0), vi(6),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    # 合并所有 body
    if c.bRepBodies.count > 1:
        bodies = adsk.core.ObjectCollection.create()
        for i in range(c.bRepBodies.count):
            bodies.add(c.bRepBodies.item(i))
        c.features.combineFeatures.add(
            c.bRepBodies.item(0), bodies,
            adsk.fusion.FeatureOperations.JoinFeatureOperation)

    # 偏心臂末端孔 φ8 (第一轴承)
    sk3 = c.sketches.add(c.xYConstructionPlane)
    sk3.sketchCurves.sketchCircles.addByCenterRadius(pt3(10, 0, 0), 4)
    c.features.extrudeFeatures.addSimple(
        sk3.profiles.item(0), vi(12),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
safe_exec(build_eccentric, "C2_ECCENTRIC")

# ── C3: 轴承 210_Bearing_608_v1 ──
def build_bearing():
    c = new_comp(root, "210_Bearing_608_v1")
    cylinder_with_hole(c, 22, 8, 7, c.xYConstructionPlane)
safe_exec(build_bearing, "C3_BEARING")

# ── C4: 连杆 300_ConnectingRod_draft_v1 ──
def build_rod():
    c = new_comp(root, "300_ConnectingRod_draft_v1")
    # 主体: 矩形 50×12 + 两端半圆头 (总轮廓)
    sk = c.sketches.add(c.xYConstructionPlane)
    lines = sk.sketchCurves.sketchLines
    arcs = sk.sketchCurves.sketchArcs
    # 上直线
    lines.addByTwoPoints(pt3(-25, 6, 0), pt3(25, 6, 0))
    # 右端半圆
    arcs.addByCenterStartEnd(pt3(25, 0, 0), pt3(25, 6, 0), pt3(25, -6, 0))
    # 下直线
    lines.addByTwoPoints(pt3(25, -6, 0), pt3(-25, -6, 0))
    # 左端半圆
    arcs.addByCenterStartEnd(pt3(-25, 0, 0), pt3(-25, -6, 0), pt3(-25, 6, 0))
    # 拉伸厚度 5mm
    c.features.extrudeFeatures.addSimple(
        sk.profiles.item(0), vi(5),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # 两端铰接孔 φ5mm
    sk2 = c.sketches.add(c.xYConstructionPlane)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(-25, 0, 0), 2.5)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(25, 0, 0), 2.5)
    c.features.extrudeFeatures.addSimple(
        sk2.profiles.item(0), vi(8),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
safe_exec(build_rod, "C4_CONROD")

# ── C5: 活塞杆 310_PistonRod_draft_v1 ──
def build_piston():
    c = new_comp(root, "310_PistonRod_draft_v1")
    # 主体 φ10×80mm (沿 Y 轴)
    extrude_cyl(c, 10, 80, c.xZConstructionPlane)
    # 底端铰接孔 φ5 (在底端上方 2mm 处, 穿透)
    bot = offset_plane(c, c.xYConstructionPlane, -38)
    sk = c.sketches.add(bot)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0, 0, 0), 2.5)
    c.features.extrudeFeatures.addSimple(
        sk.profiles.item(0), vi(12),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
safe_exec(build_piston, "C5_PISTON")

# ── C6: 滑套 320_PistonBushing_draft_v1 ──
def build_bushing():
    c = new_comp(root, "320_PistonBushing_draft_v1")
    cylinder_with_hole(c, 18, 10.1, 25, c.xYConstructionPlane)
safe_exec(build_bushing, "C6_BUSHING")

# ── C7: 按摩头 400_MassageHead_v1 ──
def build_head():
    c = new_comp(root, "400_MassageHead_v1")
    # 连接柱 φ8×15mm
    extrude_cyl(c, 8, 15, c.xZConstructionPlane)
    # 球体 φ40mm: 在连接柱底端旋转生成
    # 球心在 Y = -(15+20) = -35 处
    sphere_plane = offset_plane(c, c.xZConstructionPlane, -35)
    sk = c.sketches.add(sphere_plane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0, 0, 0), 20)
    f = c.features.extrudeFeatures.addSimple(
        sk.profiles.item(0), vi(0.1),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # 简化: 球也用圆柱近似 (后续用 revolve)
    # 先用一个短圆柱占位
    sk2 = c.sketches.add(sphere_plane)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0, 0, 0), 20)
    c.features.extrudeFeatures.addSimple(
        sk2.profiles.item(0), vi(40),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
safe_exec(build_head, "C7_MASSAGE_HEAD")

# ═══════════════════════════════════════════
# PART 4: 爆炸视图变换位置
# ═══════════════════════════════════════════
try:
    # 获取所有 occurrence 并设置爆炸位置
    occs = root.occurrences
    positions = {
        "100_Motor_draft_v1":       vec3(0, 0, 0),        # 电机在中心
        "200_EccentricWheel_draft_v1": vec3(30, 0, 0),     # 偏心轮在电机右侧
        "210_Bearing_608_v1":         vec3(45, 0, 0),      # 第一轴承更远
        "300_ConnectingRod_draft_v1":  vec3(60, 20, 0),     # 连杆右上
        "310_PistonRod_draft_v1":     vec3(60, 60, 0),      # 活塞杆更上
        "320_PistonBushing_draft_v1": vec3(60, 80, 0),      # 滑套
        "400_MassageHead_v1":         vec3(60, 110, 0),     # 按摩头最上
    }
    for i in range(occs.count):
        occ = occs.item(i)
        nm = occ.component.name
        if nm in positions:
            t = positions[nm]
            mat = adsk.core.Matrix3D.create()
            mat.translation = t
            occ.transform = mat
            log.append(f"TRANSFORMED:{nm}")
except Exception as te:
    log.append(f"EXPLODE_WARN:{str(te)[:80]}")

# ═══════════════════════════════════════════
# PART 5: saveAs
# ═══════════════════════════════════════════
try:
    # 先获取 Default Project 和根文件夹
    projects = app.data.projects
    default_proj = projects.itemByName("Default Project")
    if default_proj:
        root_folder = default_proj.rootFolder
        des_doc.saveAs("NOTE6_Assembly_draft_v1", root_folder, 
                      "NOTE6 逆向工程完整装配 — draft v1.0", "draft_v1.0")
        log.append("SAVEAS:OK")
    else:
        des_doc.save("draft v1.0 pre-save")
        log.append("SAVE:FALLBACK")
except Exception as se:
    log.append(f"SAVE_WARN:{str(se)[:120]}")

# 统计
total_bodies = sum(c.bRepBodies.count for c in design.allComponents)
log.append(f"STATS:COMPS={design.allComponents.count}|BODIES={total_bodies}|PARAMS={params.count}")

print("\n".join(log))
```

except Exception as e:
print(f"FATAL:{str(e)\[:300]}")
if ui:
ui.messageBox(f"Script error:\n{str(e)\[:200]}")
'''

print("\n🔨 Running FULL NOTE6 build script...")
r = c.execute\_script(FULL\_SCRIPT, read\_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(f"\n{'='\*60}")
print(msg\[:3000])
print(f"{'='\*60}")

# 截图

try:
print("\n📸 Taking screenshot...")
ss = c.take\_screenshot(direction='iso-top-right', height=1200)
print(f"   Screenshot: {str(ss)\[:200]}")
except Exception as e:
print(f"   Screenshot failed: {e}")

c.disconnect()
print("\n✅ Full build attempt complete")
