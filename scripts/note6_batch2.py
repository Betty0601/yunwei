#!/usr/bin/env python3
"""NOTE6 — Batch 2: 偏心轮 + 轴承 + 连杆 + 活塞杆 + 滑套 (在已有文档上添加)"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

c = FusionMCPClient(timeout=300)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}...")

SCRIPT = r'''
import adsk.core, adsk.fusion
app = adsk.core.Application.get()
log = []

def vi(v): return adsk.core.ValueInput.createByReal(v)
def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)

des_doc = app.activeDocument
design = des_doc.design
root = design.rootComponent
log.append(f"DOC:{des_doc.name}")
log.append(f"EXISTING_COMPS:{root.occurrences.count}")

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
    """带中心孔的圆柱 (环形轮廓)"""
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

# ── C4: 偏心轮 200_EccentricWheel_draft_v1 ──
try:
    c4 = nc(root, "200_EccentricWheel_draft_v1")
    # 圆盘主体 φ30×10
    cyl(c4, 30, 10, c4.xYConstructionPlane)
    # 中心电机轴孔 φ6
    cut_cyl_hole(c4, 6, 12, c4.xYConstructionPlane)
    # 偏心臂矩形 (中心 x=10, 宽 12, 厚 6)
    arm_plane = offset_plane(c4, c4.xYConstructionPlane, 5)
    sk = c4.sketches.add(arm_plane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(
        pt3(4, -6, 0), pt3(16, 6, 0))
    c4.features.extrudeFeatures.addSimple(
        sk.profiles.item(0), vi(6),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    log.append("C4_ECCENTRIC:OK")
except Exception as e:
    log.append(f"C4_ECCENTRIC:ERR:{str(e)[:60]}")

# ── C5: 第一轴承 210_Bearing_608_v1 ──
try:
    c5 = nc(root, "210_Bearing_608_v1")
    ring(c5, 22, 8, 7, c5.xYConstructionPlane)
    log.append("C5_BRING1:OK")
except Exception as e:
    log.append(f"C5_BRING1:ERR:{str(e)[:60]}")

# ── C6: 第二轴承 211_Bearing2_608_v1 ──
try:
    c6 = nc(root, "211_Bearing2_608_v1")
    ring(c6, 22, 8, 7, c6.xYConstructionPlane)
    log.append("C6_BRING2:OK")
except Exception as e:
    log.append(f"C6_BRING2:ERR:{str(e)[:60]}")

# ── C7: 连杆 300_ConnectingRod_draft_v1 ──
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
    # 两端铰接孔 φ5
    sk2 = c7.sketches.add(c7.xYConstructionPlane)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(-25, 0, 0), 2.5)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(25, 0, 0), 2.5)
    c7.features.extrudeFeatures.addSimple(
        sk2.profiles.item(0), vi(8),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
    log.append("C7_CONROD:OK")
except Exception as e:
    log.append(f"C7_CONROD:ERR:{str(e)[:60]}")

# ── C8: 连杆压盖 340_RodCap_draft_v1 ──
try:
    c8 = nc(root, "340_RodCap_draft_v1")
    ring(c8, 18, 8, 3, c8.xYConstructionPlane)
    log.append("C8_RODCAP:OK")
except Exception as e:
    log.append(f"C8_RODCAP:ERR:{str(e)[:60]}")

# ── C9: 活塞杆 310_PistonRod_draft_v1 ──
try:
    c9 = nc(root, "310_PistonRod_draft_v1")
    # 主体 φ10×80
    cyl(c9, 10, 80, c9.xZConstructionPlane)
    # 底端铰接孔 φ5
    bot = offset_plane(c9, c9.xYConstructionPlane, -38)
    cut_cyl_hole(c9, 5, 12, bot)
    # 顶端按摩头接口柱 φ8×10
    top = offset_plane(c9, c9.xYConstructionPlane, 40)
    cyl(c9, 8, 10, top)
    log.append("C9_PISTON:OK")
except Exception as e:
    log.append(f"C9_PISTON:ERR:{str(e)[:60]}")

# ── C10: 滑套 320_PistonBushing_draft_v1 ──
try:
    c10 = nc(root, "320_PistonBushing_draft_v1")
    ring(c10, 18, 10.1, 25, c10.xYConstructionPlane)
    log.append("C10_BUSHING:OK")
except Exception as e:
    log.append(f"C10_BUSHING:ERR:{str(e)[:60]}")

# ── C11: 软胶套 330_SoftRubberSleeve_draft_v1 ──
try:
    c11 = nc(root, "330_SoftRubberSleeve_draft_v1")
    ring(c11, 22, 19, 20, c11.xYConstructionPlane)
    log.append("C11_RUBBER:OK")
except Exception as e:
    log.append(f"C11_RUBBER:ERR:{str(e)[:60]}")

log.append(f"STATS:COMPS={design.allComponents.count}")
print("|".join(log))
'''

print("\n⚙️ Batch 2: eccentric + bearings + rod + piston + bushing...")
r = c.execute_script(SCRIPT, read_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(f"\n   {msg[:1200]}")

import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2)
r2 = sock.connect_ex(('127.0.0.1', 27182))
print(f"\n   MCP_AFTER_BATCH2: {'ALIVE ✅' if r2 == 0 else 'DEAD ❌'}")
sock.close()

c.disconnect()
