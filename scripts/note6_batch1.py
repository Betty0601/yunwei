#!/usr/bin/env python3
"""NOTE6 — Batch 1: 文档 + 参数 + 电机 (测试稳定性)"""
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

des_doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType, True)
des_doc.name = "NOTE6_Assembly_draft_v1"
design = des_doc.design
root = design.rootComponent
log.append(f"DOC:{des_doc.name}")

# 15 Core params (simplified units)
ps = [
    ("amplitude",10.0,"mm","Amplitude A=10mm"),
    ("eccentricity",10.0,"mm","eccentric distance e=10mm"),
    ("stroke",20.0,"mm","Peak-to-peak S=20mm"),
    ("rod_length",50.0,"mm","Rod length L"),
    ("rod_ratio",0.2,"","Rod ratio lambda=0.2"),
    ("motor_od",55.0,"mm","Motor OD 55mm"),
    ("motor_length",60.0,"mm","Motor length"),
    ("motor_shaft_d",6.0,"mm","Output shaft dia"),
    ("bearing_id",8.0,"mm","608ZZ ID"),
    ("bearing_od",22.0,"mm","608ZZ OD"),
    ("bearing_width",7.0,"mm","608ZZ width"),
    ("piston_d",10.0,"mm","Piston dia"),
    ("bushing_od",18.0,"mm","Bushing OD"),
    ("massage_head_d",40.0,"mm","Ball head dia"),
    ("rpm_5",3300.0,"rpm","5th gear speed"),
]
for nm,val,u,desc in ps:
    if not design.userParameters.itemByName(nm):
        design.userParameters.add(nm, vi(val), u, desc)
log.append(f"PARAMS:{len(ps)}")

# Helper
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

# ── 组件 1: 电机 ──
c1 = nc(root, "100_Motor_draft_v1")
cyl(c1, 55, 60, c1.xZConstructionPlane)  # 外壳
p = offset_plane(c1, c1.xZConstructionPlane, 30)
cyl(c1, 6, 75, p)  # 输出轴 (独立体)
log.append("C1_MOTOR:OK")

# ── 组件 2: 电机支架 ──
c2 = nc(root, "110_MotorBracket_draft_v1")
sk = c2.sketches.add(c2.xZConstructionPlane)
sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 65/2)
sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 58/2)
prof = sk.profiles.item(1) if sk.profiles.count >= 2 else sk.profiles.item(0)
c2.features.extrudeFeatures.addSimple(
    prof, vi(5), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
log.append("C2_BRACKET:OK")

# ── 组件 3: 电机减震垫 ──
c3 = nc(root, "120_RubberMount_draft_v1")
sk3 = c3.sketches.add(c3.xZConstructionPlane)
sk3.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 70/2)
sk3.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 60/2)
prof3 = sk3.profiles.item(1) if sk3.profiles.count >= 2 else sk3.profiles.item(0)
c3.features.extrudeFeatures.addSimple(
    prof3, vi(3), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
log.append("C3_MOUNT:OK")

log.append(f"STATS:COMPS={design.allComponents.count}")
print("|".join(log))
'''

print("\n🔋 Batch 1: doc + params + motor family...")
r = c.execute_script(SCRIPT, read_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(f"   {msg[:800]}")

# 立即检查 MCP 是否还活着
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2)
r2 = sock.connect_ex(('127.0.0.1', 27182))
mcp_ok = r2 == 0
print(f"\n   MCP_AFTER_BATCH1: {'ALIVE ✅' if mcp_ok else 'DEAD ❌'}")
sock.close()

c.disconnect()
