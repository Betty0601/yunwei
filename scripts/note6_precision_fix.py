#!/usr/bin/env python3
"""
NOTE6 深度尺寸核对 + 嵌套关系修复

按文档精确核对每个零件的尺寸和位置:

【偏心轮】(专利 R4 + 技术规格):
  - 旋转中心 = (0,0,0)
  - 中心电机轴孔 = φ6mm (间隙配合 H7/g6)
  - 偏心臂中心 = (e,0,0) = (10,0,0)  ← 必须精确!
  - 偏心臂末端孔 = φ8mm (第一轴承间隙配合)
  
【轴承 608ZZ】(行业标准):
  - ID=8mm, OD=22mm, W=7mm ✓
  
【连杆】:
  - 总长 L ≈ 50mm, 两端孔中心距 = 50mm
  - 两端孔径 = φ5mm (与轴承/铰接螺钉配合)
  - 中心在原点, 左右孔中心 = (-25,0,0) 和 (25,0,0) ✓

【活塞杆】:
  - φ10mm × 80mm, 中心在原点, 沿 Y 轴
  - 底端铰接孔 Y = -40 + 2 = -38mm 处 ✓
  - 顶端接口柱 Y = +40mm 处 ✓

【关键嵌套关系】:
  电机输出轴(φ6) → 偏心轮中心孔(φ6) ✓
  偏心轮偏心臂(10mm位置) → 第一轴承(ID8) → 连杆一端(φ5孔)
  连杆另一端(φ5孔) → 第二轴承(ID8) → 活塞杆底端(φ5孔)
  
问题发现:
  ❌ 偏心轮缺少 (10,0,0) 处的 φ8 轴承孔
  ❌ 偏心臂矩形应该对齐中心 (10,0,0)
"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

c = FusionMCPClient(timeout=600)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}...")

FIX_SCRIPT = '''
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
    def offset_p(comp, base, dist):
        inp = comp.constructionPlanes.createInput()
        inp.setByOffset(base, vi(dist))
        return comp.constructionPlanes.add(inp)
    def make_cyl(comp, dia, depth, plane):
        sk = comp.sketches.add(plane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), dia/2)
        comp.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(depth),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    def make_ring(comp, od, id_, depth, plane):
        sk = comp.sketches.add(plane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), od/2)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), id_/2)
        prof = sk.profiles.item(1) if sk.profiles.count >= 2 else sk.profiles.item(0)
        comp.features.extrudeFeatures.addSimple(
            prof, vi(depth), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    def cut_hole_at(comp, dia, depth, plane, cx, cy):
        """在 (cx, cy) 位置打中心孔"""
        sk = comp.sketches.add(plane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(cx, cy, 0), dia/2)
        comp.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), vi(depth),
            adsk.fusion.FeatureOperations.CutFeatureOperation)

    # ═══════════════════════════════
    # 重新建模偏心轮 — 精确嵌套关系
    # ═══════════════════════════════
    try:
        c200 = new_comp("200_EccentricWheel_v2")
        
        # Step 1: 圆盘主体 φ30×10 (XY 平面, 中心=旋转中心=(0,0,0))
        make_cyl(c200, 30, 10, c200.xYConstructionPlane)
        
        # Step 2: 中心电机轴孔 φ6 @ (0,0,0) — 间隙配合 H7/g6
        cut_hole_at(c200, 6, 12, c200.xYConstructionPlane, 0, 0)
        
        # Step 3: 偏心臂 — 精确对齐中心 (10,0,0)
        # 矩形: x ∈ [4, 16] (中心 x=10, 宽 12), y ∈ [-6, 6] (宽 12)
        arm_mid = offset_p(c200, c200.xYConstructionPlane, 5)  # z=5mm (圆盘中间)
        sk_arm = c200.sketches.add(arm_mid)
        sk_arm.sketchCurves.sketchLines.addTwoPointRectangle(
            pt3(4, -6, 0), pt3(16, 6, 0))
        c200.features.extrudeFeatures.addSimple(
            sk_arm.profiles.item(0), vi(6),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        # Step 4: 【关键!】偏心臂末端孔 φ8 @ (10,0,0) — 第一轴承间隙配合
        # 偏心距 e = 10mm 精确位置!
        cut_hole_at(c200, 8, 12, c200.xYConstructionPlane, 10, 0)
        
        print("200_ECCENTRIC_V2:OK [圆盘+中心孔+偏心臂@10mm+末端φ8孔]")
    except Exception as e:
        print(f"200V2:ERR:{str(e)[:60]}")

    # ═══════════════════════════════
    # 补全缺失的紧固件
    # ═══════════════════════════════
    try:
        c220 = new_comp("220_FasteningScrew_v2")
        # 内六角圆柱头螺钉 M4×8
        make_cyl(c220, 8, 3, c220.xZConstructionPlane)  # 头部
        p220 = offset_p(c220, c220.xZConstructionPlane, 3)
        make_cyl(c220, 4, 8, p220)
        print("220_SCREW:OK")
    except Exception as e: print(f"220:ERR:{str(e)[:40]}")

    try:
        c350 = new_comp("350_HingeScrew_v2")
        make_cyl(c350, 10, 4, c350.xZConstructionPlane)
        p350 = offset_p(c350, c350.xZConstructionPlane, 4)
        make_cyl(c350, 5, 10, p350)
        print("350_HINGE:OK")
    except Exception as e: print(f"350:ERR:{str(e)[:40]}")

    try:
        c341 = new_comp("341_RodCapScrew_v2")
        make_cyl(c341, 6, 2, c341.xZConstructionPlane)
        p341 = offset_p(c341, c341.xZConstructionPlane, 2)
        make_cyl(c341, 3, 4, p341)
        print("341_CAPSCREW:OK")
    except Exception as e: print(f"341:ERR:{str(e)[:40]}")

    # ═══════════════════════════════
    # 6 个独立 18650 电芯 (隔离支架 2×3 排列)
    # ═══════════════════════════════
    bat_pos = [(0,0), (20,0), (40,0), (0,20), (20,20), (40,20)]
    for i, (bx, by) in enumerate(bat_pos):
        try:
            cn = f"51{i+1}_BatteryCell_v2"
            bc = new_comp(cn)
            make_cyl(bc, 18, 65, bc.xZConstructionPlane)
            mat = adsk.core.Matrix3D.create()
            mat.translation = adsk.core.Vector3D.create(bx, by, 0)
            root.occurrences.item(root.occurrences.count-1).transform = mat
            print(f"{cn}:OK@({bx},{by})")
        except Exception as e: print(f"{cn}:ERR:{str(e)[:30]}")

    # 外壳自攻螺钉 ×4
    for i in range(1, 5):
        try:
            c = new_comp(f"77{i}_HousingScrew_v2")
            make_cyl(c, 5, 2, c.xZConstructionPlane)
            p = offset_p(c, c.xZConstructionPlane, 2)
            make_cyl(c, 2.5, 5, p)
            print(f"77{i}:OK")
        except Exception as e: print(f"77{i}:ERR:{str(e)[:30]}")

    # 最终统计
    total = design.allComponents.count
    bodies = sum(c.bRepBodies.count for c in design.allComponents)
    print(f"FINAL:COMPS={total}|BODIES={bodies}|OCCS={root.occurrences.count}")
    
    try:
        des_doc.save("draft v1.0 — 补全偏心臂轴承孔+紧固件+6电池")
        print("SAVE:OK")
    except Exception as e:
        print(f"SAVE:ERR:{str(e)[:80]}")

except Exception as fatal:
    print(f"FATAL:{str(fatal)[:150]}")
'''

print("\n🔧 Precision fix: eccentric arm bearing hole + fasteners + 6 batteries...")
r = c.execute_script(FIX_SCRIPT, read_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(f"\n{'='*60}")
print(msg[:2500])
print(f"{'='*60}")

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
r2 = s.connect_ex(('127.0.0.1', 27182))
print(f"\nMCP: {'ALIVE ✅' if r2 == 0 else 'DEAD ❌'}")
s.close()

c.disconnect()
