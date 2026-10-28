#!/usr/bin/env python3
"""
NOTE6 完整重建 — 在现有 batch1 文档上补全 batch2 + batch3
修复: Fusion 内部脚本加 try/except 避免事务回滚
"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

c = FusionMCPClient(timeout=300)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}...")

# ── Batch 2 重建 (偏心轮+轴承+连杆+活塞杆+滑套+软胶套+连杆压盖) ──
BATCH2_SCRIPT = '''
import adsk.core, adsk.fusion
import traceback

try:
    app = adsk.core.Application.get()
    des_doc = app.activeDocument
    design = des_doc.design
    root = design.rootComponent
    log = [f"DOC:{des_doc.name}", f"EXISTING:{root.occurrences.count}"]
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    def nc(parent, name):
        occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = name
        return occ.component
    def offset_plane(comp, base, dist):
        inp = comp.constructionPlanes.createInput()
        inp.setByOffset(base, vi(dist))
        return comp.constructionPlanes.add(inp)
    def cyl(comp, dia, depth, plane):
        sk = comp.sketches.add(plane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), dia/2)
        comp.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(depth),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    def ring(comp, od, id_, depth, plane):
        sk = comp.sketches.add(plane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), od/2)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), id_/2)
        prof = sk.profiles.item(1) if sk.profiles.count >= 2 else sk.profiles.item(0)
        comp.features.extrudeFeatures.addSimple(
            prof, vi(depth), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    def cut_cyl_hole(comp, dia, depth, plane):
        sk = comp.sketches.add(plane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), dia/2)
        comp.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(depth),
            adsk.fusion.FeatureOperations.CutFeatureOperation)

    # C4: 偏心轮
    try:
        c4 = nc(root, "200_EccentricWheel_draft_v1")
        cyl(c4, 30, 10, c4.xYConstructionPlane)
        cut_cyl_hole(c4, 6, 12, c4.xYConstructionPlane)
        arm_plane = offset_plane(c4, c4.xYConstructionPlane, 5)
        sk = c4.sketches.add(arm_plane)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(
            pt3(4, -6, 0), pt3(16, 6, 0))
        c4.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(6),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        log.append("C4:OK")
    except Exception as e: log.append(f"C4:ERR:{str(e)[:40]}")

    # C5: 第一轴承
    try:
        c5 = nc(root, "210_Bearing_608_v1")
        ring(c5, 22, 8, 7, c5.xYConstructionPlane)
        log.append("C5:OK")
    except Exception as e: log.append(f"C5:ERR:{str(e)[:40]}")

    # C6: 第二轴承
    try:
        c6 = nc(root, "211_Bearing2_608_v1")
        ring(c6, 22, 8, 7, c6.xYConstructionPlane)
        log.append("C6:OK")
    except Exception as e: log.append(f"C6:ERR:{str(e)[:40]}")

    # C7: 连杆
    try:
        c7 = nc(root, "300_ConnectingRod_draft_v1")
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
        sk2 = c7.sketches.add(c7.xYConstructionPlane)
        sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(-25, 0, 0), 2.5)
        sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(25, 0, 0), 2.5)
        c7.features.extrudeFeatures.addSimple(
            sk2.profiles.item(0), vi(8),
            adsk.fusion.FeatureOperations.CutFeatureOperation)
        log.append("C7:OK")
    except Exception as e: log.append(f"C7:ERR:{str(e)[:40]}")

    # C8: 连杆压盖
    try:
        c8 = nc(root, "340_RodCap_draft_v1")
        ring(c8, 18, 8, 3, c8.xYConstructionPlane)
        log.append("C8:OK")
    except Exception as e: log.append(f"C8:ERR:{str(e)[:40]}")

    # C9: 活塞杆
    try:
        c9 = nc(root, "310_PistonRod_draft_v1")
        cyl(c9, 10, 80, c9.xZConstructionPlane)
        bot = offset_plane(c9, c9.xYConstructionPlane, -38)
        cut_cyl_hole(c9, 5, 12, bot)
        top = offset_plane(c9, c9.xYConstructionPlane, 40)
        cyl(c9, 8, 10, top)
        log.append("C9:OK")
    except Exception as e: log.append(f"C9:ERR:{str(e)[:40]}")

    # C10: 滑套
    try:
        c10 = nc(root, "320_PistonBushing_draft_v1")
        ring(c10, 18, 10.1, 25, c10.xYConstructionPlane)
        log.append("C10:OK")
    except Exception as e: log.append(f"C10:ERR:{str(e)[:40]}")

    # C11: 软胶套
    try:
        c11 = nc(root, "330_SoftRubberSleeve_draft_v1")
        ring(c11, 22, 19, 20, c11.xYConstructionPlane)
        log.append("C11:OK")
    except Exception as e: log.append(f"C11:ERR:{str(e)[:40]}")

    log.append(f"STATS:{design.allComponents.count}")
except Exception as fatal:
    log = [f"FATAL:{str(fatal)[:100]}"]

print("|".join(log))
'''

print("\n⚙️ Rebuild Batch 2...")
r2 = c.execute_script(BATCH2_SCRIPT, read_only=False)
msg2 = r2.get('message', str(r2)) if isinstance(r2, dict) else str(r2)
print(f"   {msg2[:800]}")

import socket
def mcp_alive():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    r = s.connect_ex(('127.0.0.1', 27182))
    s.close()
    return r == 0

print(f"   MCP: {'ALIVE ✅' if mcp_alive() else 'DEAD ❌'}")

# ── Batch 3 重建 (按摩头6+电池+外壳+控制板) ──
if mcp_alive():
    BATCH3_SCRIPT = '''
import adsk.core, adsk.fusion
import traceback

try:
    app = adsk.core.Application.get()
    des_doc = app.activeDocument
    design = des_doc.design
    root = design.rootComponent
    log = [f"DOC:{des_doc.name}", f"BEFORE:{root.occurrences.count}"]
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    def nc(parent, name):
        occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = name
        return occ.component
    def offset_plane(comp, base, dist):
        inp = comp.constructionPlanes.createInput()
        inp.setByOffset(base, vi(dist))
        return comp.constructionPlanes.add(inp)
    def cyl(comp, dia, depth, plane):
        sk = comp.sketches.add(plane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), dia/2)
        comp.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(depth),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    def box(comp, w, h, d, plane=None):
        pl = plane or comp.xYConstructionPlane
        sk = comp.sketches.add(pl)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(
            pt3(-w/2, -h/2, 0), pt3(w/2, h/2, 0))
        comp.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(d),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    def ring(comp, od, id_, depth, plane):
        sk = comp.sketches.add(plane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), od/2)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), id_/2)
        prof = sk.profiles.item(1) if sk.profiles.count >= 2 else sk.profiles.item(0)
        comp.features.extrudeFeatures.addSimple(
            prof, vi(depth), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    def make_massage_head(comp, ball_d):
        cyl(comp, 8, 15, comp.xZConstructionPlane)
        sp = offset_plane(comp, comp.xZConstructionPlane, -(15+ball_d/2))
        cyl(comp, ball_d, ball_d, sp)

    # 按摩头 6 款
    heads = [
        ("410_StandardBallHead_draft_v1", 40),
        ("420_TriggerPointHead_draft_v1", 16),
        ("430_FlatHead_draft_v1", 40),  # 特殊: 平头
        ("440_LargeBallHead_draft_v1", 60),
        ("450_CushionHead_draft_v1", 36),
    ]
    for nm, bd in heads:
        try:
            make_massage_head(nc(root, nm), bd)
            log.append(f"{nm.split('_')[0]}:OK")
        except Exception as e: log.append(f"{nm[:8]}:ERR:{str(e)[:30]}")

    # 小平头特殊处理 (薄圆柱)
    try:
        c430 = nc(root, "430_FlatHead_draft_v1")
        cyl(c430, 8, 15, c430.xZConstructionPlane)
        sp = offset_plane(c430, c430.xZConstructionPlane, -15)
        cyl(c430, 40, 5, sp)
        log.append("C430:OK")
    except Exception as e: log.append(f"C430:ERR:{str(e)[:30]}")

    # U型头
    try:
        c460 = nc(root, "460_UShapedHead_draft_v1")
        cyl(c460, 8, 15, c460.xZConstructionPlane)
        base = offset_plane(c460, c460.xZConstructionPlane, -15)
        box(c460, 30, 30, 5, base)
        log.append("C460:OK")
    except Exception as e: log.append(f"C460:ERR:{str(e)[:30]}")

    # 电池 + 支架
    try:
        cyl(nc(root, "510_BatteryCell_18650_draft_v1"), 18, 65, 
            nc(root, "510_BatteryCell_18650_draft_v1").xZConstructionPlane)
        log.append("C510:OK")
    except Exception as e: log.append(f"C510:ERR:{str(e)[:30]}")
    try:
        box(nc(root, "520_BatteryHolder_draft_v1"), 80, 20, 70)
        log.append("C520:OK")
    except Exception as e: log.append(f"C520:ERR:{str(e)[:30]}")

    # 控制板
    try:
        box(nc(root, "610_MainPCB_draft_v1"), 50, 30, 2)
        log.append("C610:OK")
    except Exception as e: log.append(f"C610:ERR:{str(e)[:30]}")

    # 外壳组
    try: box(nc(root, "710_UpperHousing_draft_v1"), 70, 60, 80); log.append("C710:OK")
    except Exception as e: log.append(f"C710:ERR:{str(e)[:30]}")
    try: box(nc(root, "720_HandleHousing_draft_v1"), 45, 45, 100); log.append("C720:OK")
    except Exception as e: log.append(f"C720:ERR:{str(e)[:30]}")
    try: ring(nc(root, "730_SiliconeCover_draft_v1"), 50, 46, 90, nc(root, "730_SiliconeCover_draft_v1").xZConstructionPlane); log.append("C730:OK")
    except Exception as e: log.append(f"C730:ERR:{str(e)[:30]}")
    try: box(nc(root, "740_BottomDisplay_draft_v1"), 40, 30, 3); log.append("C740:OK")
    except Exception as e: log.append(f"C740:ERR:{str(e)[:30]}")
    try: box(nc(root, "750_ButtonPanel_draft_v1"), 20, 10, 2); log.append("C750:OK")
    except Exception as e: log.append(f"C750:ERR:{str(e)[:30]}")
    try: box(nc(root, "760_HoneycombVent_draft_v1"), 70, 10, 50); log.append("C760:OK")
    except Exception as e: log.append(f"C760:ERR:{str(e)[:30]}")

    log.append(f"STATS:{design.allComponents.count}|{sum(c.bRepBodies.count for c in design.allComponents)}")
except Exception as fatal:
    log = [f"FATAL:{str(fatal)[:100]}"]

print("|".join(log))
'''
    print("\n🎁 Rebuild Batch 3...")
    r3 = c.execute_script(BATCH3_SCRIPT, read_only=False)
    msg3 = r3.get('message', str(r3)) if isinstance(r3, dict) else str(r3)
    print(f"   {msg3[:1200]}")
    print(f"   MCP: {'ALIVE ✅' if mcp_alive() else 'DEAD ❌'}")

c.disconnect()
print("\n✅ Rebuild complete")
