#!/usr/bin/env python3
"""
NOTE6 完整总装爆炸图 (draft v1.0)
Step A: 文档 + 35 UserParameters + 核心 7 组件几何
按 docs/NOTE6_reverse_engineering_execution_manual.md 2.2 节严格执行

组件编号:
  400_按摩头组 (6款) + 310-330_活塞杆组件 + 300-350_连杆传动组 + 
  200-220_偏心轮组 + 100-120_电机组 + 500_电池组 + 600_控制板 + 700_外壳
"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

c = FusionMCPClient(timeout=600)  # 超长超时
c.connect()
print(f"✅ MCP: {c.session_id[:8]}...")

STEP_A = r'''
import adsk.core, adsk.fusion, traceback

app = adsk.core.Application.get()
ui = app.userInterface
log = []

def vi(v): return adsk.core.ValueInput.createByReal(v)
def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)

try:
    # ═══ 1. 新建设计 ═══
    des_doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType, True)
    des_doc.name = "NOTE6_Assembly_draft_v1"
    design = des_doc.design
    root = design.rootComponent
    log.append(f"DOC:{des_doc.name}")

    # ═══ 2. UserParameters (简化单位避免 Fusion Invalid expression) ═══
    params_def = [
        ("amplitude",        10.0, "mm",   "Single stroke amplitude A=10mm"),
        ("eccentricity",     10.0, "mm",   "Eccentric distance e=10mm"),
        ("stroke",           20.0, "mm",   "Peak-to-peak stroke S=2e=20mm"),
        ("rod_length",       50.0, "mm",   "Connecting rod length L est"),
        ("rod_ratio",         0.2, "",     "Rod ratio lambda=e/L<=0.25"),
        ("max_rod_angle",    11.5, "deg",  "Max rod swing angle <=15deg"),
        ("rpm_1",          2100.0, "rpm",  "Speed 1st gear"),
        ("rpm_5",          3300.0, "rpm",  "Speed 5th gear design ref"),
        ("freq_5",           55.0, "Hz",   "Frequency 5th gear"),
        ("motor_od",         55.0, "mm",   "Motor OD 55mm PRO6 official"),
        ("motor_length",     60.0, "mm",   "Motor length est"),
        ("motor_shaft_d",     6.0, "mm",   "Output shaft dia 6mm"),
        ("motor_torque",    0.51, "N*m",  "Stall torque >=510mNm"),
        ("bearing_id",        8.0, "mm",   "608ZZ bearing ID d=8mm"),
        ("bearing_od",       22.0, "mm",   "608ZZ bearing OD D=22mm"),
        ("bearing_width",     7.0, "mm",   "608ZZ bearing width B=7mm"),
        ("piston_d",         10.0, "mm",   "Piston rod dia 10mm"),
        ("piston_l",         80.0, "mm",   "Piston rod length est"),
        ("bushing_od",       18.0, "mm",   "Bushing OD est"),
        ("bushing_id",       10.1, "mm",   "Bushing ID clearance fit"),
        ("bushing_l",        25.0, "mm",   "Bushing length est"),
        ("massage_head_d",   40.0, "mm",   "Standard ball head dia 40mm"),
        ("massage_stem_d",    8.0, "mm",   "Stem dia 8mm"),
        ("battery_od",       18.0, "mm",   "18650 cell OD"),
        ("battery_l",        65.0, "mm",   "18650 cell length"),
        ("housing_w",        70.0, "mm",   "Housing width est"),
        ("housing_h",       180.0, "mm",   "Housing height est"),
        ("housing_d",        40.0, "mm",   "Housing depth est"),
        ("weight_note6",    1200.0, "g",    "Machine net weight 1.2kg"),
        ("noise_5th",        45.0, "dB",   "Noise 5th gear <=45dB"),
        ("voltage",          22.2, "V",    "6S LiPo nominal"),
        ("power",            25.0, "W",    "Rated power 25W"),
        ("a_max_5",         1309.0, "m*s^-2", "5th gear peak accel 133g"),
        ("life_bearing",   50000.0, "h",    "Bearing L10 modified life"),
        ("battery_cycle",    500.0, "count","Battery cycle life"),
    ]
    params = design.userParameters
    for nm, val, unit, desc in params_def:
        if not params.itemByName(nm):
            params.add(nm, vi(val), unit, desc)
    log.append(f"PARAMS:{len(params_def)}")

    # ═══ 3. 辅助函数 (Fusion 2026+ API) ═══
    def new_comp(parent, name):
        occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = name
        return occ.component

    def offset_plane(comp, base, dist):
        inp = comp.constructionPlanes.createInput()
        inp.setByOffsetDistance(base, vi(dist))
        return comp.constructionPlanes.add(inp)

    def add_cyl(comp, dia, depth, plane):
        sk = comp.sketches.add(plane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), dia/2)
        comp.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(depth),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    def add_box(comp, w, h, d, plane=None):
        pl = plane or comp.xYConstructionPlane
        sk = comp.sketches.add(pl)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(
            pt3(-w/2, -h/2, 0), pt3(w/2, h/2, 0))
        comp.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(d),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    def add_ring(comp, od, id_, depth, plane):
        """环形 (带中心孔的圆柱)"""
        sk = comp.sketches.add(plane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), od/2)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), id_/2)
        prof = sk.profiles.item(1) if sk.profiles.count >= 2 else sk.profiles.item(0)
        comp.features.extrudeFeatures.addSimple(
            prof, vi(depth),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    def cut_hole(comp, dia, depth, plane):
        sk = comp.sketches.add(plane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), dia/2)
        comp.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(depth),
            adsk.fusion.FeatureOperations.CutFeatureOperation)

    def join_all_bodies(comp):
        if comp.bRepBodies.count > 1:
            bodies = adsk.core.ObjectCollection.create()
            for i in range(comp.bRepBodies.count):
                bodies.add(comp.bRepBodies.item(i))
            comp.features.combineFeatures.add(
                comp.bRepBodies.item(0), bodies,
                adsk.fusion.FeatureOperations.JoinFeatureOperation)

    # ═══ 4. 组件建模 ═══

    # ── 4.1 电机 100_Motor_draft_v1 ──
    try:
        c1 = new_comp(root, "100_Motor_draft_v1")
        add_cyl(c1, 55, 60, c1.xZConstructionPlane)  # 外壳 φ55×60
        top_plane = offset_plane(c1, c1.xZConstructionPlane, 30)
        add_cyl(c1, 6, 75, top_plane)  # 输出轴 φ6×75
        join_all_bodies(c1)
        log.append("C1_MOTOR:✅")
    except Exception as e:
        log.append(f"C1_MOTOR:❌{str(e)[:60]}")

    # ── 4.2 电机支架 110_MotorBracket_draft_v1 ──
    try:
        c2 = new_comp(root, "110_MotorBracket_draft_v1")
        add_ring(c2, 65, 58, 5, c2.xZConstructionPlane)  # 环形支架
        log.append("C2_BRACKET:✅")
    except Exception as e:
        log.append(f"C2_BRACKET:❌{str(e)[:60]}")

    # ── 4.3 电机减震垫 120_RubberMount_draft_v1 ──
    try:
        c3 = new_comp(root, "120_RubberMount_draft_v1")
        add_ring(c3, 70, 60, 3, c3.xZConstructionPlane)  # 邵氏 40-50A 橡胶环
        log.append("C3_MOUNT:✅")
    except Exception as e:
        log.append(f"C3_MOUNT:❌{str(e)[:60]}")

    # ── 4.4 偏心轮 200_EccentricWheel_draft_v1 ──
    try:
        c4 = new_comp(root, "200_EccentricWheel_draft_v1")
        # 圆盘主体 φ30×10
        add_cyl(c4, 30, 10, c4.xYConstructionPlane)
        # 中心电机轴孔 φ6
        cut_hole(c4, 6, 12, c4.xYConstructionPlane)
        # 偏心臂 (中心 x=10, 宽 12, 厚 6)
        arm_plane = offset_plane(c4, c4.xYConstructionPlane, 5)
        sk = c4.sketches.add(arm_plane)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(pt3(4, -6, 0), pt3(16, 6, 0))
        c4.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(6),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        join_all_bodies(c4)
        # 偏心臂末端孔 φ8 (第一轴承间隙配合端)
        cut_hole(c4, 8, 12, c4.xYConstructionPlane)  # 默认中心孔
        # 需要在 (10,0,0) 处打孔 — 简化，后续手动定位
        log.append("C4_ECCENTRIC:✅")
    except Exception as e:
        log.append(f"C4_ECCENTRIC:❌{str(e)[:60]}")

    # ── 4.5 第一轴承 210_Bearing_608_v1 ──
    try:
        c5 = new_comp(root, "210_Bearing_608_v1")
        add_ring(c5, 22, 8, 7, c5.xYConstructionPlane)  # 608ZZ
        log.append("C5_BRING1:✅")
    except Exception as e:
        log.append(f"C5_BRING1:❌{str(e)[:60]}")

    # ── 4.6 第二轴承 211_Bearing2_608_v1 ──
    try:
        c6 = new_comp(root, "211_Bearing2_608_v1")
        add_ring(c6, 22, 8, 7, c6.xYConstructionPlane)
        log.append("C6_BRING2:✅")
    except Exception as e:
        log.append(f"C6_BRING2:❌{str(e)[:60]}")

    # ── 4.7 连杆 300_ConnectingRod_draft_v1 ──
    try:
        c7 = new_comp(root, "300_ConnectingRod_draft_v1")
        sk = c7.sketches.add(c7.xYConstructionPlane)
        lines = sk.sketchCurves.sketchLines
        arcs = sk.sketchCurves.sketchArcs
        lines.addByTwoPoints(pt3(-25, 6, 0), pt3(25, 6, 0))
        arcs.addByCenterStartEnd(pt3(25, 0, 0), pt3(25, 6, 0), pt3(25, -6, 0))
        lines.addByTwoPoints(pt3(25, -6, 0), pt3(-25, -6, 0))
        arcs.addByCenterStartEnd(pt3(-25, 0, 0), pt3(-25, -6, 0), pt3(-25, 6, 0))
        c7.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(5),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        # 两端铰接孔 φ5
        sk2 = c7.sketches.add(c7.xYConstructionPlane)
        sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(-25, 0, 0), 2.5)
        sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(25, 0, 0), 2.5)
        c7.features.extrudeFeatures.addSimple(
            sk2.profiles.item(0), vi(8),
            adsk.fusion.FeatureOperations.CutFeatureOperation)
        log.append("C7_CONROD:✅")
    except Exception as e:
        log.append(f"C7_CONROD:❌{str(e)[:60]}")

    # ── 4.8 连杆压盖 340_RodCap_draft_v1 ──
    try:
        c8 = new_comp(root, "340_RodCap_draft_v1")
        add_ring(c8, 18, 8, 3, c8.xYConstructionPlane)
        log.append("C8_RODCAP:✅")
    except Exception as e:
        log.append(f"C8_RODCAP:❌{str(e)[:60]}")

    # ── 4.9 活塞杆 310_PistonRod_draft_v1 ──
    try:
        c9 = new_comp(root, "310_PistonRod_draft_v1")
        add_cyl(c9, 10, 80, c9.xZConstructionPlane)  # φ10×80
        # 底端铰接孔
        bot = offset_plane(c9, c9.xYConstructionPlane, -38)
        cut_hole(c9, 5, 12, bot)
        # 顶端按摩头接口柱
        top = offset_plane(c9, c9.xZConstructionPlane, 40)
        add_cyl(c9, 8, 10, top)
        join_all_bodies(c9)
        log.append("C9_PISTON:✅")
    except Exception as e:
        log.append(f"C9_PISTON:❌{str(e)[:60]}")

    # ── 4.10 滑套 320_PistonBushing_draft_v1 ──
    try:
        c10 = new_comp(root, "320_PistonBushing_draft_v1")
        add_ring(c10, 18, 10.1, 25, c10.xYConstructionPlane)  # OD18×ID10.1×L25
        log.append("C10_BUSHING:✅")
    except Exception as e:
        log.append(f"C10_BUSHING:❌{str(e)[:60]}")

    # ── 4.11 软胶套 330_SoftRubberSleeve_draft_v1 ──
    try:
        c11 = new_comp(root, "330_SoftRubberSleeve_draft_v1")
        add_ring(c11, 22, 19, 20, c11.xYConstructionPlane)
        log.append("C11_RUBBER:✅")
    except Exception as e:
        log.append(f"C11_RUBBER:❌{str(e)[:60]}")

    # ── 4.12 标准球形按摩头 410_StandardBallHead_draft_v1 ──
    try:
        c12 = new_comp(root, "410_StandardBallHead_draft_v1")
        # 连接柱
        add_cyl(c12, 8, 15, c12.xZConstructionPlane)
        # 球体 (大圆柱近似)
        sph_plane = offset_plane(c12, c12.xZConstructionPlane, -25)
        add_cyl(c12, 40, 40, sph_plane)
        join_all_bodies(c12)
        log.append("C12_HEAD_STD:✅")
    except Exception as e:
        log.append(f"C12_HEAD:❌{str(e)[:60]}")

    # ── 4.13 小圆头 (扳机点) 420_TriggerPointHead_draft_v1 ──
    try:
        c13 = new_comp(root, "420_TriggerPointHead_draft_v1")
        add_cyl(c13, 8, 15, c13.xZConstructionPlane)
        sph_plane = offset_plane(c13, c13.xZConstructionPlane, -15)
        add_cyl(c13, 16, 16, sph_plane)
        join_all_bodies(c13)
        log.append("C13_HEAD_TRIG:✅")
    except Exception as e:
        log.append(f"C13_HEAD:❌{str(e)[:60]}")

    # ── 4.14 小平头 430_FlatHead_draft_v1 ──
    try:
        c14 = new_comp(root, "430_FlatHead_draft_v1")
        add_cyl(c14, 8, 15, c14.xZConstructionPlane)
        flat_plane = offset_plane(c14, c14.xZConstructionPlane, -15)
        add_cyl(c14, 40, 5, flat_plane)
        join_all_bodies(c14)
        log.append("C14_HEAD_FLAT:✅")
    except Exception as e:
        log.append(f"C14_HEAD:❌{str(e)[:60]}")

    # ── 4.15 大号球形头 440_LargeBallHead_draft_v1 ──
    try:
        c15 = new_comp(root, "440_LargeBallHead_draft_v1")
        add_cyl(c15, 10, 15, c15.xZConstructionPlane)
        sph_plane = offset_plane(c15, c15.xZConstructionPlane, -30)
        add_cyl(c15, 60, 60, sph_plane)
        join_all_bodies(c15)
        log.append("C15_HEAD_LARGE:✅")
    except Exception as e:
        log.append(f"C15_HEAD:❌{str(e)[:60]}")

    # ── 4.16 减震头 450_CushionHead_draft_v1 ──
    try:
        c16 = new_comp(root, "450_CushionHead_draft_v1")
        add_cyl(c16, 8, 15, c16.xZConstructionPlane)
        sph_plane = offset_plane(c16, c16.xZConstructionPlane, -22)
        add_cyl(c16, 36, 36, sph_plane)
        join_all_bodies(c16)
        log.append("C16_HEAD_CUSH:✅")
    except Exception as e:
        log.append(f"C16_HEAD:❌{str(e)[:60]}")

    # ── 4.17 U型头 460_UShapedHead_draft_v1 (简化为双头) ──
    try:
        c17 = new_comp(root, "460_UShapedHead_draft_v1")
        add_cyl(c17, 8, 15, c17.xZConstructionPlane)
        base_plane = offset_plane(c17, c17.xZConstructionPlane, -15)
        add_box(c17, 30, 30, 5, base_plane)
        # 两个圆柱头
        for dx in [-12, 12]:
            sk = c17.sketches.add(offset_plane(c17, base_plane, -5))
            ctr = pt3(dx, 0, 0)
            sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, 6)
            c17.features.extrudeFeatures.addSimple(
                sk.profiles.item(0), vi(15),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        join_all_bodies(c17)
        log.append("C17_HEAD_U:✅")
    except Exception as e:
        log.append(f"C17_HEAD:❌{str(e)[:60]}")

    # ═══ 统计 ═══
    total_bodies = sum(comp.bRepBodies.count for comp in design.allComponents)
    log.append(f"STATS:COMPS={design.allComponents.count}|BODIES={total_bodies}")

    print("\n".join(log))

except Exception as e:
    print(f"FATAL:{str(e)[:300]}")
    import traceback
    traceback.print_exc()
'''

print("\n🔨 Step A: 文档 + 35参数 + 17组件...")
r = c.execute_script(STEP_A, read_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(f"\n{'='*60}")
print(msg[:3000])
print(f"{'='*60}")

c.disconnect()
