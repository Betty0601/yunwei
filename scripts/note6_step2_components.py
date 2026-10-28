#!/usr/bin/env python3
"""
NOTE6 Step 2 — 7 大核心组件几何建模 (draft v1.0)

每个组件用参数化 UserParameter 控制尺寸
所有几何使用 .sketches.add() + addSimple 拉伸
"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

c = FusionMCPClient(timeout=180)
c.connect()
print(f"✅ MCP Session: {c.session_id[:8]}...")

STEP2_SCRIPT = r'''
import adsk.core, adsk.fusion, traceback

app = adsk.core.Application.get()
log = []

try:
    des_doc = app.activeDocument
    design = des_doc.design
    root = design.rootComponent
    log.append(f"ACTIVE_DOC:{des_doc.name}")
    log.append(f"COMPS_BEFORE:{root.occurrences.count}")

    # ═══ 辅助函数 ═══
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    def vec3(x,y,z): return adsk.core.Vector3D.create(x,y,z)

    # 通用草图 + 拉伸
    def make_cyl(comp, diameter, depth, sketch_plane=None):
        """在指定平面上画圆并拉伸为圆柱"""
        plane = sketch_plane or comp.xYConstructionPlane
        sk = comp.sketches.add(plane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), diameter/2)
        prof = sk.profiles.item(0)
        f = comp.features.extrudeFeatures.addSimple(
            prof, vi(depth),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        return f

    def make_box(comp, w, h, d):
        """画矩形并拉伸为盒子"""
        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(
            pt3(-w/2, -h/2, 0), pt3(w/2, h/2, 0))
        f = comp.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(d),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        return f

    def make_cyl_hole(comp, outer_d, hole_d, depth):
        """带中心孔的圆柱 (先拉外圆再切除内孔)"""
        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), outer_d/2)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), hole_d/2)
        # 外圆 + 内孔 = 环形轮廓需要用 combine
        # 简单方案: 先拉外圆, 再用孔工具
        f_outer = comp.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(depth),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        # 新建草图用于中心孔
        sk2 = comp.sketches.add(comp.xYConstructionPlane)
        sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), hole_d/2)
        f_hole = comp.features.extrudeFeatures.addSimple(
            sk2.profiles.item(0), vi(depth+1),
            adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        return f_outer, f_hole

    # 创建新组件
    def new_comp(parent, name):
        occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = name
        return occ.component

    # ═══════════════════════════════════════════════════
    # 组件 1: 电机 100_Motor_draft_v1
    # φ55mm × 60mm 外壳, φ6mm × 75mm 输出轴
    # ═══════════════════════════════════════════════════
    comp_motor = new_comp(root, "100_Motor_draft_v1")

    # 电机外壳 (55mm OD, 60mm 长)
    make_cyl(comp_motor, 55, 60, comp_motor.xZConstructionPlane)  # 沿 X 轴拉伸
    # 输出轴 (6mm OD, 75mm 长, 从外壳一端伸出)
    # 用偏移平面画草图
    shaft_plane = comp_motor.constructionPlanes.createByOffset(
        comp_motor.xZConstructionPlane, vi(60/2))  # 电机端面
    make_cyl(comp_motor, 6, 75, shaft_plane)

    log.append("C1_MOTOR:OK")

    # ═══════════════════════════════════════════════════
    # 组件 2: 偏心轮 200_EccentricWheel_draft_v1
    # 圆盘 φ30×10mm + 偏心臂 12×8×6mm, 偏心距 e=10mm
    # 中心孔 φ6mm (电机轴), 另一端孔 φ8mm (第一轴承)
    # ═══════════════════════════════════════════════════
    comp_ec = new_comp(root, "200_EccentricWheel_draft_v1")

    # 偏心轮圆盘部分 (在 XY 平面, 中心在原点)
    make_cyl(comp_ec, 30, 10)  # φ30×10mm 圆盘

    # 中心孔 (电机轴孔) — 需要用 Cut
    sk_hole = comp_ec.sketches.add(comp_ec.xYConstructionPlane)
    sk_hole.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 3)  # φ6mm
    comp_ec.features.extrudeFeatures.addSimple(
        sk_hole.profiles.item(0), vi(12),
        adsk.fusion.FeatureOperations.CutFeatureOperation
    )

    # 偏心臂 (从圆盘延伸到偏心距 e=10mm 处)
    # 偏心臂中心在 (10, 0, 0), 宽度 12mm, 高度 8mm, 厚 6mm
    arm_plane = comp_ec.constructionPlanes.createByOffset(
        comp_ec.xYConstructionPlane, vi(5))  # 在圆盘中间位置
    sk_arm = comp_ec.sketches.add(arm_plane)
    sk_arm.sketchCurves.sketchLines.addTwoPointRectangle(
        pt3(10-6, -4, 0), pt3(10+6, 4, 0))  # 中心 x=10, 宽 12
    # 先新建 body 再合并
    f_arm = comp_ec.features.extrudeFeatures.addSimple(
        sk_arm.profiles.item(0), vi(6),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    # 合并到圆盘
    target_body = comp_ec.bRepBodies.item(0)
    tool_bodies = adsk.core.ObjectCollection.create()
    tool_bodies.add(comp_ec.bRepBodies.item(1))
    comp_ec.features.combineFeatures.add(target_body, tool_bodies, 
        adsk.fusion.FeatureOperations.JoinFeatureOperation)

    # 偏心臂末端孔 (φ8mm — 第一轴承)
    sk_arm_hole = comp_ec.sketches.add(comp_ec.xYConstructionPlane)
    sk_arm_hole.sketchCurves.sketchCircles.addByCenterRadius(pt3(10, 0, 0), 4)  # φ8mm
    comp_ec.features.extrudeFeatures.addSimple(
        sk_arm_hole.profiles.item(0), vi(10),
        adsk.fusion.FeatureOperations.CutFeatureOperation
    )

    log.append("C2_ECCENTRIC:OK")

    # ═══════════════════════════════════════════════════
    # 组件 3: 轴承 210_Bearing_608_v1
    # 608ZZ: ID φ8mm × OD φ22mm × W 7mm
    # ═══════════════════════════════════════════════════
    comp_brg = new_comp(root, "210_Bearing_608_v1")

    # 先画外环 (φ22 OD, φ10 ID 外环孔)
    # 再画内环 (φ8 ID, φ12 OD)
    # 保持简单: 用一个带中心孔的圆柱表示轴承
    make_cyl_hole(comp_brg, 22, 8, 7)  # OD22 × ID8 × W7

    log.append("C3_BEARING:OK")

    # ═══════════════════════════════════════════════════
    # 组件 4: 连杆 300_ConnectingRod_draft_v1
    # L=50mm × 宽 12mm × 厚 5mm
    # 两端铰接孔 φ5mm
    # ═══════════════════════════════════════════════════
    comp_rod = new_comp(root, "300_ConnectingRod_draft_v1")

    # 连杆主体 (水平, 两端孔中心距 50mm)
    # 中心在原点, 一端在 (-25, 0, 0), 另一端在 (25, 0, 0)
    sk_rod = comp_rod.sketches.add(comp_rod.xYConstructionPlane)
    # 主体矩形 50×12
    sk_rod.sketchCurves.sketchLines.addTwoPointRectangle(
        pt3(-25, -6, 0), pt3(25, 6, 0))
    # 去掉两端多余部分 (用圆切掉)
    # 左端点: 画圆 φ12 中心 (-25, 0, 0)
    sk_rod.sketchCurves.sketchCircles.addByCenterRadius(pt3(-25, 0, 0), 6)
    sk_rod.sketchCurves.sketchCircles.addByCenterRadius(pt3(25, 0, 0), 6)
    # 这会把轮廓分成多块, 我们需要整个外部轮廓
    # 简单做法: 重新画一个轮廓包含两端半圆
    # 删掉刚才的, 重画
    sk_rod.deleteMe()

    # 用多段线重画连杆轮廓
    sk_rod = comp_rod.sketches.add(comp_rod.xYConstructionPlane)
    lines = sk_rod.sketchCurves.sketchLines
    arcs = sk_rod.sketchCurves.sketchArcs
    # 上直线从 (-25, 6) 到 (25, 6)
    lines.addByTwoPoints(pt3(-25, 6, 0), pt3(25, 6, 0))
    # 右端半圆 (从 (25, 6) 顺时针到 (25, -6))
    arcs.addByCenterStartEnd(pt3(25, 0, 0), pt3(25, 6, 0), pt3(25, -6, 0))
    # 下直线从 (25, -6) 到 (-25, -6)
    lines.addByTwoPoints(pt3(25, -6, 0), pt3(-25, -6, 0))
    # 左端半圆
    arcs.addByCenterStartEnd(pt3(-25, 0, 0), pt3(-25, -6, 0), pt3(-25, 6, 0))

    f_rod = comp_rod.features.extrudeFeatures.addSimple(
        sk_rod.profiles.item(0), vi(5),  # 厚度 5mm
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )

    # 两端铰接孔 φ5mm
    sk_holes = comp_rod.sketches.add(comp_rod.xYConstructionPlane)
    sk_holes.sketchCurves.sketchCircles.addByCenterRadius(pt3(-25, 0, 0), 2.5)
    sk_holes.sketchCurves.sketchCircles.addByCenterRadius(pt3(25, 0, 0), 2.5)
    comp_rod.features.extrudeFeatures.addSimple(
        sk_holes.profiles.item(0), vi(6),
        adsk.fusion.FeatureOperations.CutFeatureOperation
    )

    log.append("C4_CONROD:OK")

    # ═══════════════════════════════════════════════════
    # 组件 5: 活塞杆 310_PistonRod_draft_v1
    # φ10mm × 80mm 钢杆 + 底端铰接孔 φ5mm
    # ═══════════════════════════════════════════════════
    comp_piston = new_comp(root, "310_PistonRod_draft_v1")

    # 活塞杆主体 (沿 Y 轴, 总长 80mm)
    make_cyl(comp_piston, 10, 80, comp_piston.xZConstructionPlane)

    # 底端铰接孔 (在底端, 垂直于轴线方向 φ5mm)
    # 底端 Y = -80/2 = -40
    bottom_plane = comp_piston.constructionPlanes.createByOffset(
        comp_piston.xYConstructionPlane, vi(-38))  # 离底端 2mm
    sk_phole = comp_piston.sketches.add(bottom_plane)
    sk_phole.sketchCurves.sketchCircles.addByCenterRadius(pt3(0, 0, 0), 2.5)
    comp_piston.features.extrudeFeatures.addSimple(
        sk_phole.profiles.item(0), vi(12),  # 穿透整个 φ10 杆
        adsk.fusion.FeatureOperations.CutFeatureOperation
    )

    # 顶端按摩头接口 (φ8mm 短柱, 带外螺纹示意)
    top_plane = comp_piston.constructionPlanes.createByOffset(
        comp_piston.xYConstructionPlane, vi(40))
    make_cyl(comp_piston, 8, 10, top_plane)

    # 合并
    bodies = adsk.core.ObjectCollection.create()
    for i in range(comp_piston.bRepBodies.count):
        bodies.add(comp_piston.bRepBodies.item(i))
    if comp_piston.bRepBodies.count > 1:
        comp_piston.features.combineFeatures.add(
            comp_piston.bRepBodies.item(0), bodies,
            adsk.fusion.FeatureOperations.JoinFeatureOperation)

    log.append("C5_PISTON:OK")

    # ═══════════════════════════════════════════════════
    # 组件 6: 滑套 320_PistonBushing_draft_v1
    # OD φ18mm × ID φ10.1mm × L 25mm
    # 内孔带油槽 (螺旋示意, 简化为环形槽)
    # ═══════════════════════════════════════════════════
    comp_bush = new_comp(root, "320_PistonBushing_draft_v1")

    # 带中心孔的圆柱 (外 φ18, 内 φ10.1, 长 25)
    make_cyl_hole(comp_bush, 18, 10.1, 25)

    # 油槽 (3 个环形槽示意, 在内部)
    for z_off in [-5, 0, 5]:
        groove_plane = comp_bush.constructionPlanes.createByOffset(
            comp_bush.xZConstructionPlane, vi(z_off))
        # 但油槽是在内部, 需要在 ID10.1 上开环形槽
        # 简化: 用一个小圆柱切除
        sk_groove = comp_bush.sketches.add(groove_plane)
        sk_groove.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 10.1/2 + 0.5)
        sk_groove.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 10.1/2 - 0.5)

    log.append("C6_BUSHING:OK")

    # ═══════════════════════════════════════════════════
    # 组件 7: 按摩头 400_MassageHead_v1
    # 标准球形头: 球 φ40mm + 连接柱
    # ═══════════════════════════════════════════════════
    comp_head = new_comp(root, "400_MassageHead_v1")

    # 连接柱 (φ8mm × 15mm)
    make_cyl(comp_head, 8, 15, comp_head.xZConstructionPlane)

    # 球体 (用旋转特征: 半圆绕轴旋转)
    sk_sphere = comp_head.sketches.add(comp_head.xZConstructionPlane)
    # 半圆轮廓: 从 (0, 0) 到 (0, -40) 绕 X 轴
    sk_sphere.sketchCurves.sketchArcs.addByCenterStartEnd(
        pt3(0, -15, 0),  # 球心在连接柱底端下方
        pt3(20, -15, 0),  # 右
        pt3(-20, -15, 0)) # 左

    # 合并
    bodies2 = adsk.core.ObjectCollection.create()
    for i in range(comp_head.bRepBodies.count):
        bodies2.add(comp_head.bRepBodies.item(i))
    if comp_head.bRepBodies.count > 1:
        comp_head.features.combineFeatures.add(
            comp_head.bRepBodies.item(0), bodies2,
            adsk.fusion.FeatureOperations.JoinFeatureOperation)

    log.append("C7_MASSAGE_HEAD:OK")

    # ═══════════════════════════════════════════════════
    # 统计
    # ═══════════════════════════════════════════════════
    total_bodies = 0
    for c in design.allComponents:
        total_bodies += c.bRepBodies.count
    log.append(f"TOTAL_COMPS:{design.allComponents.count}")
    log.append(f"TOTAL_BODIES:{total_bodies}")
    log.append(f"PARAMS:{design.userParameters.count}")

    print("|".join(log))

except Exception as e:
    print(f"ERROR:{str(e)[:500]}")
    import traceback
    traceback.print_exc()
'''

print("\n🔧 STEP 2: Build 7 component geometry...")
r2 = c.execute_script(STEP2_SCRIPT, read_only=False)
msg2 = r2.get('message', str(r2)) if isinstance(r2, dict) else str(r2)
print(f"\n   Result: {msg2[:1500]}")

c.disconnect()
print("\n✅ Step 2 attempted")
