#!/usr/bin/env python3
"""NOTE6 — Batch 3: 按摩头6款 + 电池组 + 外壳 + 控制板"""
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
log.append(f"COMPS_BEFORE:{root.occurrences.count}")

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

# ═══ 按摩头 6 款 ═══
# 410_标准球形头
try:
    c410 = nc(root, "410_StandardBallHead_draft_v1")
    cyl(c410, 8, 15, c410.xZConstructionPlane)  # 连接柱
    sp = offset_plane(c410, c410.xZConstructionPlane, -25)
    cyl(c410, 40, 40, sp)  # 球头 (圆柱近似)
    log.append("C410_HEAD_STD:OK")
except Exception as e:
    log.append(f"C410:{str(e)[:50]}")

# 420_小圆头 (扳机点)
try:
    c420 = nc(root, "420_TriggerPointHead_draft_v1")
    cyl(c420, 8, 15, c420.xZConstructionPlane)
    sp = offset_plane(c420, c420.xZConstructionPlane, -15)
    cyl(c420, 16, 16, sp)
    log.append("C420_HEAD_TRIG:OK")
except Exception as e:
    log.append(f"C420:{str(e)[:50]}")

# 430_小平头
try:
    c430 = nc(root, "430_FlatHead_draft_v1")
    cyl(c430, 8, 15, c430.xZConstructionPlane)
    sp = offset_plane(c430, c430.xZConstructionPlane, -15)
    cyl(c430, 40, 5, sp)
    log.append("C430_HEAD_FLAT:OK")
except Exception as e:
    log.append(f"C430:{str(e)[:50]}")

# 440_大号球形头
try:
    c440 = nc(root, "440_LargeBallHead_draft_v1")
    cyl(c440, 10, 15, c440.xZConstructionPlane)
    sp = offset_plane(c440, c440.xZConstructionPlane, -30)
    cyl(c440, 60, 60, sp)
    log.append("C440_HEAD_LARGE:OK")
except Exception as e:
    log.append(f"C440:{str(e)[:50]}")

# 450_减震头
try:
    c450 = nc(root, "450_CushionHead_draft_v1")
    cyl(c450, 8, 15, c450.xZConstructionPlane)
    sp = offset_plane(c450, c450.xZConstructionPlane, -22)
    cyl(c450, 36, 36, sp)
    log.append("C450_HEAD_CUSH:OK")
except Exception as e:
    log.append(f"C450:{str(e)[:50]}")

# 460_U型头 (简化为双头 + 基座)
try:
    c460 = nc(root, "460_UShapedHead_draft_v1")
    cyl(c460, 8, 15, c460.xZConstructionPlane)
    base = offset_plane(c460, c460.xZConstructionPlane, -15)
    box(c460, 30, 30, 5, base)
    log.append("C460_HEAD_U:OK")
except Exception as e:
    log.append(f"C460:{str(e)[:50]}")

# ═══ 电池组组件 ═══
# 510_Battery_Cell 18650 × 6
try:
    c510 = nc(root, "510_BatteryCell_18650_draft_v1")
    cyl(c510, 18, 65, c510.xZConstructionPlane)  # 单节电芯
    log.append("C510_CELL:OK")
except Exception as e:
    log.append(f"C510:{str(e)[:50]}")

# 520_BatteryHolder 隔离式支架
try:
    c520 = nc(root, "520_BatteryHolder_draft_v1")
    box(c520, 80, 20, 70)  # 底座
    log.append("C520_HOLDER:OK")
except Exception as e:
    log.append(f"C520:{str(e)[:50]}")

# ═══ 控制板 ═══
try:
    c610 = nc(root, "610_MainPCB_draft_v1")
    box(c610, 50, 30, 2)  # PCB 板
    log.append("C610_PCB:OK")
except Exception as e:
    log.append(f"C610:{str(e)[:50]}")

# ═══ 外壳组件 ═══
# 710_上壳体
try:
    c710 = nc(root, "710_UpperHousing_draft_v1")
    box(c710, 70, 60, 80)  # 简化外壳
    log.append("C710_UPPER:OK")
except Exception as e:
    log.append(f"C710:{str(e)[:50]}")

# 720_手柄壳体
try:
    c720 = nc(root, "720_HandleHousing_draft_v1")
    box(c720, 45, 45, 100)
    log.append("C720_HANDLE:OK")
except Exception as e:
    log.append(f"C720:{str(e)[:50]}")

# 730_硅胶保护套
try:
    c730 = nc(root, "730_SiliconeCover_draft_v1")
    ring(c730, 50, 46, 90, c730.xZConstructionPlane)
    log.append("C730_SILICONE:OK")
except Exception as e:
    log.append(f"C730:{str(e)[:50]}")

# 740_底部曲面屏
try:
    c740 = nc(root, "740_BottomDisplay_draft_v1")
    box(c740, 40, 30, 3)
    log.append("C740_DISPLAY:OK")
except Exception as e:
    log.append(f"C740:{str(e)[:50]}")

# 750_按键面板
try:
    c750 = nc(root, "750_ButtonPanel_draft_v1")
    box(c750, 20, 10, 2)
    log.append("C750_BUTTON:OK")
except Exception as e:
    log.append(f"C750:{str(e)[:50]}")

# 760_蜂窝散热孔 (简化为孔板)
try:
    c760 = nc(root, "760_HoneycombVent_draft_v1")
    box(c760, 70, 10, 50)
    log.append("C760_VENT:OK")
except Exception as e:
    log.append(f"C760:{str(e)[:50]}")

# ═══ 统计 ═══
total_bodies = sum(c.bRepBodies.count for c in design.allComponents)
log.append(f"STATS:TOTAL_COMPS={design.allComponents.count}|TOTAL_BODIES={total_bodies}")
print("|".join(log))
'''

print("\n🎁 Batch 3: 6 massage heads + battery + housing + PCB...")
r = c.execute_script(SCRIPT, read_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(f"\n   {msg[:2000]}")

import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2)
r2 = sock.connect_ex(('127.0.0.1', 27182))
print(f"\n   MCP: {'ALIVE ✅' if r2 == 0 else 'DEAD ❌'}")
sock.close()

c.disconnect()
