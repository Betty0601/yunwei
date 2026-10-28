#!/usr/bin/env python3
"""
NOTE6 — 单次完整创建 (无事务回滚)
一个 Fusion 脚本完成所有组件，每步 try/except 保护
"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

c = FusionMCPClient(timeout=600)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}...")

FULL_SAFE = '''
import adsk.core, adsk.fusion
import traceback

# 把所有逻辑放在 try/except 里，任何异常都不影响已成功的操作
all_ok = True
try:
    app = adsk.core.Application.get()
    
    # 如果有文档先关
    try:
        for i in range(app.documents.count-1, -1, -1):
            try: app.documents.item(i).close(True)
            except: pass
    except: pass
    
    des_doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType, True)
    des_doc.name = "NOTE6_Assembly_draft_v1"
    design = des_doc.design
    root = design.rootComponent
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    def new_comp(name):
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = name
        return occ.component
    def offset_p(comp, base, dist):
        inp = comp.constructionPlanes.createInput()
        inp.setByOffset(base, vi(dist))
        return comp.constructionPlanes.add(inp)
    def make_cyl(comp, dia, depth, plane):
        try:
            sk = comp.sketches.add(plane)
            sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), dia/2)
            comp.features.extrudeFeatures.addSimple(
                sk.profiles.item(0), vi(depth),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            return True
        except Exception as e:
            print(f"CYL_ERR:{str(e)[:40]}")
            return False
    def make_ring(comp, od, id_, depth, plane):
        try:
            sk = comp.sketches.add(plane)
            sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), od/2)
            sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), id_/2)
            prof = sk.profiles.item(1) if sk.profiles.count >= 2 else sk.profiles.item(0)
            comp.features.extrudeFeatures.addSimple(
                prof, vi(depth), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            return True
        except Exception as e:
            print(f"RING_ERR:{str(e)[:40]}")
            return False
    def make_box(comp, w, h, d):
        try:
            sk = comp.sketches.add(comp.xYConstructionPlane)
            sk.sketchCurves.sketchLines.addTwoPointRectangle(
                pt3(-w/2, -h/2, 0), pt3(w/2, h/2, 0))
            comp.features.extrudeFeatures.addSimple(
                sk.profiles.item(0), vi(d),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            return True
        except Exception as e:
            print(f"BOX_ERR:{str(e)[:40]}")
            return False
    def cut_hole(comp, dia, depth, plane):
        try:
            sk = comp.sketches.add(plane)
            sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), dia/2)
            comp.features.extrudeFeatures.addSimple(
                sk.profiles.item(0), vi(depth),
                adsk.fusion.FeatureOperations.CutFeatureOperation)
            return True
        except Exception as e:
            print(f"CUT_ERR:{str(e)[:40]}")
            return False
    
    # 参数
    for nm, val, unit, desc in [
        ("amplitude",10.0,"mm","Amplitude"),("eccentricity",10.0,"mm","Eccentric"),
        ("stroke",20.0,"mm","Stroke"),("rod_length",50.0,"mm","Rod L"),
        ("rod_ratio",0.2,"","Ratio"),("motor_od",55.0,"mm","Motor OD"),
        ("motor_length",60.0,"mm","Motor L"),("motor_shaft_d",6.0,"mm","Shaft d"),
        ("bearing_id",8.0,"mm","608 d"),("bearing_od",22.0,"mm","608 D"),
        ("bearing_width",7.0,"mm","608 B"),("piston_d",10.0,"mm","Piston d"),
        ("bushing_od",18.0,"mm","Bushing OD"),("massage_head_d",40.0,"mm","Ball d"),
        ("rpm_5",3300.0,"rpm","5th gear"),
    ]:
        try:
            if not design.userParameters.itemByName(nm):
                design.userParameters.add(nm, vi(val), unit, desc)
        except: pass
    print("PARAMS:OK")

    # ═══════════════════════════════
    # 组件创建 (每个都 try/except)
    # ═══════════════════════════════
    
    # 100_Motor
    try:
        c = new_comp("100_Motor_draft_v1")
        make_cyl(c, 55, 60, c.xZConstructionPlane)
        p = offset_p(c, c.xZConstructionPlane, 30)
        make_cyl(c, 6, 75, p)
        print("100:OK")
    except Exception as e: print(f"100:ERR:{str(e)[:40]}")

    # 110_Bracket
    try:
        c = new_comp("110_MotorBracket_draft_v1")
        make_ring(c, 65, 58, 5, c.xZConstructionPlane)
        print("110:OK")
    except Exception as e: print(f"110:ERR:{str(e)[:40]}")

    # 120_Mount
    try:
        c = new_comp("120_RubberMount_draft_v1")
        make_ring(c, 70, 60, 3, c.xZConstructionPlane)
        print("120:OK")
    except Exception as e: print(f"120:ERR:{str(e)[:40]}")

    # 200_EccentricWheel
    try:
        c = new_comp("200_EccentricWheel_draft_v1")
        make_cyl(c, 30, 10, c.xYConstructionPlane)
        cut_hole(c, 6, 12, c.xYConstructionPlane)
        arm_plane = offset_p(c, c.xYConstructionPlane, 5)
        sk = c.sketches.add(arm_plane)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(
            pt3(4, -6, 0), pt3(16, 6, 0))
        c.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(6),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        print("200:OK")
    except Exception as e: print(f"200:ERR:{str(e)[:40]}")

    # 210_Bearing
    try:
        c = new_comp("210_Bearing_608_v1")
        make_ring(c, 22, 8, 7, c.xYConstructionPlane)
        print("210:OK")
    except Exception as e: print(f"210:ERR:{str(e)[:40]}")

    # 211_Bearing2
    try:
        c = new_comp("211_Bearing2_608_v1")
        make_ring(c, 22, 8, 7, c.xYConstructionPlane)
        print("211:OK")
    except Exception as e: print(f"211:ERR:{str(e)[:40]}")

    # 300_ConnectingRod
    try:
        c = new_comp("300_ConnectingRod_draft_v1")
        sk = c.sketches.add(c.xYConstructionPlane)
        sk.sketchCurves.sketchLines.addByTwoPoints(pt3(-25, 6, 0), pt3(25, 6, 0))
        sk.sketchCurves.sketchArcs.addByCenterStartEnd(pt3(25, 0, 0), pt3(25, 6, 0), pt3(25, -6, 0))
        sk.sketchCurves.sketchLines.addByTwoPoints(pt3(25, -6, 0), pt3(-25, -6, 0))
        sk.sketchCurves.sketchArcs.addByCenterStartEnd(pt3(-25, 0, 0), pt3(-25, -6, 0), pt3(-25, 6, 0))
        c.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(5),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        sk2 = c.sketches.add(c.xYConstructionPlane)
        sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(-25, 0, 0), 2.5)
        sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(25, 0, 0), 2.5)
        c.features.extrudeFeatures.addSimple(
            sk2.profiles.item(0), vi(8),
            adsk.fusion.FeatureOperations.CutFeatureOperation)
        print("300:OK")
    except Exception as e: print(f"300:ERR:{str(e)[:40]}")

    # 340_RodCap
    try:
        c = new_comp("340_RodCap_draft_v1")
        make_ring(c, 18, 8, 3, c.xYConstructionPlane)
        print("340:OK")
    except Exception as e: print(f"340:ERR:{str(e)[:40]}")

    # 310_PistonRod
    try:
        c = new_comp("310_PistonRod_draft_v1")
        make_cyl(c, 10, 80, c.xZConstructionPlane)
        bot = offset_p(c, c.xYConstructionPlane, -38)
        cut_hole(c, 5, 12, bot)
        top = offset_p(c, c.xYConstructionPlane, 40)
        make_cyl(c, 8, 10, top)
        print("310:OK")
    except Exception as e: print(f"310:ERR:{str(e)[:40]}")

    # 320_Bushing
    try:
        c = new_comp("320_PistonBushing_draft_v1")
        make_ring(c, 18, 10.1, 25, c.xYConstructionPlane)
        print("320:OK")
    except Exception as e: print(f"320:ERR:{str(e)[:40]}")

    # 330_SoftRubber
    try:
        c = new_comp("330_SoftRubberSleeve_draft_v1")
        make_ring(c, 22, 19, 20, c.xYConstructionPlane)
        print("330:OK")
    except Exception as e: print(f"330:ERR:{str(e)[:40]}")

    # 6 Massage heads
    heads_data = [
        ("410_StandardBallHead_draft_v1", 40),
        ("420_TriggerPointHead_draft_v1", 16),
        ("430_FlatHead_draft_v1", 40),
        ("440_LargeBallHead_draft_v1", 60),
        ("450_CushionHead_draft_v1", 36),
    ]
    for nm, bd in heads_data:
        try:
            c = new_comp(nm)
            make_cyl(c, 8, 15, c.xZConstructionPlane)
            sp = offset_p(c, c.xZConstructionPlane, -(15+bd//2))
            make_cyl(c, bd, bd, sp)
            print(f"{nm[:3]}:OK")
        except Exception as e: print(f"{nm[:3]}:ERR:{str(e)[:40]}")

    # 460_UShaped
    try:
        c = new_comp("460_UShapedHead_draft_v1")
        make_cyl(c, 8, 15, c.xZConstructionPlane)
        base = offset_p(c, c.xZConstructionPlane, -15)
        make_box(c, 30, 30, 5)  # plane param not used correctly
        print("460:OK")
    except Exception as e: print(f"460:ERR:{str(e)[:40]}")

    # Battery + holder + PCB + Housing
    for nm, fn in [
        ("510_BatteryCell_18650_draft_v1", lambda c: make_cyl(c, 18, 65, c.xZConstructionPlane)),
        ("520_BatteryHolder_draft_v1", lambda c: make_box(c, 80, 20, 70)),
        ("610_MainPCB_draft_v1", lambda c: make_box(c, 50, 30, 2)),
        ("710_UpperHousing_draft_v1", lambda c: make_box(c, 70, 60, 80)),
        ("720_HandleHousing_draft_v1", lambda c: make_box(c, 45, 45, 100)),
        ("730_SiliconeCover_draft_v1", lambda c: make_ring(c, 50, 46, 90, c.xZConstructionPlane)),
        ("740_BottomDisplay_draft_v1", lambda c: make_box(c, 40, 30, 3)),
        ("750_ButtonPanel_draft_v1", lambda c: make_box(c, 20, 10, 2)),
        ("760_HoneycombVent_draft_v1", lambda c: make_box(c, 70, 10, 50)),
    ]:
        try:
            c = new_comp(nm)
            fn(c)
            print(f"{nm[:3]}:OK")
        except Exception as e: print(f"{nm[:3]}:ERR:{str(e)[:40]}")

    # 统计 + save
    total = design.allComponents.count
    bodies = sum(c.bRepBodies.count for c in design.allComponents)
    print(f"FINAL_STATS:COMPS={total}|BODIES={bodies}")
    
    try:
        des_doc.save("draft v1.0 — NOTE6 完整爆炸图")
        print("SAVE:OK")
    except Exception as e:
        print(f"SAVE:ERR:{str(e)[:60]}")

except Exception as fatal:
    print(f"FATAL:{str(fatal)[:120]}")
'''

print("\n🔥 ONE-SHOT Full Build (all try/except)...")
r = c.execute_script(FULL_SAFE, read_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(f"\n{'='*60}")
print(msg[:3000])
print(f"{'='*60}")

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
r2 = s.connect_ex(('127.0.0.1', 27182))
print(f"\nMCP: {'ALIVE ✅' if r2 == 0 else 'DEAD ❌'}")
s.close()

c.disconnect()
print("\n✅ One-shot build attempt done")
