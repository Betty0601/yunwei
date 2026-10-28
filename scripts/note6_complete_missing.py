#!/usr/bin/env python3
"""
NOTE6 补全缺失组件 — 文档 2.2 节逐项核对

已创建 (26): 按摩头×6 + 活塞杆组3 + 传动组5 + 偏心轮 + 电机组3 + 电池2 + 控制板 + 外壳6
缺失:
  ❌ 220_FasteningScrew — 电机输出端紧固螺钉 (专利R4)
  ❌ 350_HingeScrew — 连杆-活塞杆铰接螺钉 (专利R4)  
  ❌ 511-516 — 6 个独立 18650 电芯实例 (现在只建了 1 个)
  ❌ 连杆两端的铰接轴承孔位置 — 需要与轴承尺寸匹配
  ❌ 偏心轮偏心臂末端的轴承间隙配合孔 — 已建但尺寸需确认
"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

c = FusionMCPClient(timeout=300)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}...")

COMPLETE_SCRIPT = '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    des_doc = app.activeDocument
    design = des_doc.design
    root = design.rootComponent
    print(f"BEFORE:{root.occurrences.count}")
    
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    def new_comp(name):
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = name
        return occ.component
    def make_cyl(comp, dia, depth, plane):
        sk = comp.sketches.add(plane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), dia/2)
        comp.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(depth),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    def make_countersunk_screw(comp, head_d, shank_d, shank_l, total_l, plane):
        """模拟内六角/沉头螺钉: 头部圆柱 + 螺纹杆"""
        # 头部 (沉头)
        sk = comp.sketches.add(plane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), head_d/2)
        comp.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(total_l - shank_l),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        # 螺纹杆
        p2 = None
        try:
            inp = comp.constructionPlanes.createInput()
            inp.setByOffset(plane, vi(total_l - shank_l))
            p2 = comp.constructionPlanes.add(inp)
        except:
            p2 = plane
        make_cyl(comp, shank_d, shank_l, p2)
    
    # ── 紧固螺钉 (电机输出端 M4×8) ──
    try:
        c220 = new_comp("220_FasteningScrew_draft_v1")
        make_countersunk_screw(c220, 8, 4, 6, 8, c220.xZConstructionPlane)
        print("220_SCREW_MOTOR:OK")
    except Exception as e: print(f"220:ERR:{str(e)[:40]}")

    # ── 铰接螺钉 (连杆-活塞杆 M5×12) ──
    try:
        c350 = new_comp("350_HingeScrew_draft_v1")
        make_countersunk_screw(c350, 10, 5, 8, 12, c350.xZConstructionPlane)
        print("350_SCREW_HINGE:OK")
    except Exception as e: print(f"350:ERR:{str(e)[:40]}")

    # ── 连杆压盖螺钉 ×2 (M3×4) ──
    try:
        c341 = new_comp("341_RodCapScrew_draft_v1")
        make_countersunk_screw(c341, 6, 3, 2, 4, c341.xZConstructionPlane)
        print("341_SCREW_CAP:OK")
    except Exception as e: print(f"341:ERR:{str(e)[:40]}")

    # ── 6 个独立 18650 电芯实例 ──
    positions = [(0,0), (20,0), (40,0), (0,18), (20,18), (40,18)]
    for i, (x, y) in enumerate(positions):
        try:
            cnm = f"51{i+1}_BatteryCell_draft_v1"
            c = new_comp(cnm)
            make_cyl(c, 18, 65, c.xZConstructionPlane)
            mat = adsk.core.Matrix3D.create()
            mat.translation = adsk.core.Vector3D.create(x, y, 0)
            root.occurrences.item(root.occurrences.count-1).transform = mat
            print(f"{cnm}:OK")
        except Exception as e: print(f"{cnm}:ERR:{str(e)[:30]}")

    # ── 外壳自攻螺钉 ×4 (M2.5×6) ──
    try:
        for i in range(1, 5):
            c = new_comp(f"77{i}_HousingScrew_draft_v1")
            make_countersunk_screw(c, 5, 2.5, 4, 6, c.xZConstructionPlane)
        print("770_SCREWS_HOUSING:OK")
    except Exception as e: print(f"770:ERR:{str(e)[:40]}")

    # ── 连杆压盖本体 (之前只建了一个简单 ring, 补充压盖几何) ──
    try:
        # 查找已有的压盖组件, 如果没有就新建
        found = None
        for i in range(design.allComponents.count):
            if "RodCap" in design.allComponents.item(i).name:
                found = design.allComponents.item(i)
                break
        if not found:
            c = new_comp("340_RodCap_Detail_draft_v1")
            # 压盖: 带两个固定螺钉孔的板
            sk = c.sketches.add(c.xYConstructionPlane)
            sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 12)
            sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 3)
            prof = sk.profiles.item(1) if sk.profiles.count >= 2 else sk.profiles.item(0)
            c.features.extrudeFeatures.addSimple(
                prof, vi(3), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            print("340_DETAIL:OK")
    except Exception as e: print(f"340D:ERR:{str(e)[:40]}")

    total = design.allComponents.count
    bodies = sum(c.bRepBodies.count for c in design.allComponents)
    print(f"FINAL_STATS:COMPS={total}|BODIES={bodies}|OCCS={root.occurrences.count}")
    
    try:
        des_doc.save("draft v1.0 — NOTE6 补全紧固件+电池+压盖")
        print("SAVE:OK")
    except Exception as e:
        print(f"SAVE:ERR:{str(e)[:60]}")

except Exception as fatal:
    print(f"FATAL:{str(fatal)[:150]}")
'''

print("\n🔩 Completing missing components...")
r = c.execute_script(COMPLETE_SCRIPT, read_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(f"\n{'='*60}")
print(msg[:2000])
print(f"{'='*60}")

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
r2 = s.connect_ex(('127.0.0.1', 27182))
print(f"\nMCP: {'ALIVE ✅' if r2 == 0 else 'DEAD ❌'}")
s.close()

c.disconnect()
print("\n✅ Completion done")
