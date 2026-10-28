#!/usr/bin/env python3
"""NOTE6 Final explode update + screenshot + git"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

c = FusionMCPClient(timeout=300)
c.connect()

# 更新爆炸视图位置 — 包含所有 40 组件
UPDATE = r'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    des_doc = app.activeDocument
    design = des_doc.design
    root = design.rootComponent
    
    # 完整爆炸视图 (按文档 2.2 节自下而上 + 新增组件)
    pos = {
        # ── 外壳层 (最底层) ──
        "710_UpperHousing_draft_v1":       (0,    0,  0),
        "720_HandleHousing_draft_v1":      (0, -130,  0),
        "730_SiliconeCover_draft_v1":      (0, -200,  0),
        "740_BottomDisplay_draft_v1":    (40, -100,  0),
        "750_ButtonPanel_draft_v1":      (40,  -70,  0),
        "760_HoneycombVent_draft_v1":   (-40,   10,  0),
        "771_HousingScrew_draft_v1":    (60,  -50,  0),
        "772_HousingScrew_draft_v1":    (60,  -60,  0),
        "773_HousingScrew_draft_v1":    (60,  -70,  0),
        "774_HousingScrew_draft_v1":    (60,  -80,  0),
        
        # ── 电机层 ──
        "100_Motor_draft_v1":              (0,   60,  0),
        "110_MotorBracket_draft_v1":    (-40,   70,  0),
        "120_RubberMount_draft_v1":     (-40,   80,  0),
        "220_FasteningScrew_draft_v1":  (20,  100,  0),  # 电机端紧固螺钉
        
        # ── 电池组 (6S) ──
        "510_BatteryCell_18650_draft_v1":(80,  -30,  0),
        "511_BatteryCell_draft_v1":     (80,  -40,  0),
        "512_BatteryCell_draft_v1":     (95,  -40,  0),
        "513_BatteryCell_draft_v1":    (110,  -40,  0),
        "514_BatteryCell_draft_v1":     (80,  -55,  0),
        "515_BatteryCell_draft_v1":     (95,  -55,  0),
        "516_BatteryCell_draft_v1":    (110,  -55,  0),
        "520_BatteryHolder_draft_v1":   (95,  -70,  0),
        
        # ── 控制板 ──
        "610_MainPCB_draft_v1":           (0,  -50,  0),
        
        # ── 传动核心层 ──
        "200_EccentricWheel_draft_v1":     (0,  150,  0),
        "210_Bearing_608_v1":             (30,  160,  0),  # 第一轴承 (间隙配合端)
        "211_Bearing2_608_v1":           (30,  230,  0),  # 第二轴承 (连杆端)
        
        # ── 连杆层 ──
        "300_ConnectingRod_draft_v1":      (0,  250,  0),
        "340_RodCap_draft_v1":           (-30, 240,  0),  # 连杆压盖
        "341_RodCapScrew_draft_v1":      (-40, 250,  0),  # 压盖螺钉
        
        # ── 活塞杆组件 ──
        "330_SoftRubberSleeve_draft_v1":  (-30, 280,  0),  # 软胶套
        "320_PistonBushing_draft_v1":      (0,  300,  0),  # 滑套
        "310_PistonRod_draft_v1":          (0,  340,  0),  # 活塞杆
        
        # ── 铰接螺钉 ──
        "350_HingeScrew_draft_v1":        (30,  330,  0),  # 铰接螺钉
        
        # ── 按摩头 (顶部一排横向展开) ──
        "410_StandardBallHead_draft_v1": (-90, 420,  0),
        "420_TriggerPointHead_draft_v1": (-55, 420,  0),
        "430_FlatHead_draft_v1":          (-20, 420,  0),
        "440_LargeBallHead_draft_v1":      (15, 420,  0),
        "450_CushionHead_draft_v1":       (50, 420,  0),
        "460_UShapedHead_draft_v1":       (85, 420,  0),
    }
    
    moved = 0
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        nm = occ.component.name
        if nm in pos:
            x, y, z = pos[nm]
            try:
                mat = adsk.core.Matrix3D.create()
                mat.translation = adsk.core.Vector3D.create(x, y, z)
                occ.transform = mat
                moved += 1
            except Exception as e:
                print(f"ERR:{nm[:10]}:{str(e)[:30]}")
    
    print(f"EXPLODED:{moved}/{len(pos)}")
    
    try:
        des_doc.save("draft v1.0 — complete 40 components explode")
        print("SAVE:OK")
    except Exception as e:
        print(f"SAVE:ERR:{str(e)[:60]}")
        
except Exception as fatal:
    print(f"FATAL:{str(fatal)[:150]}")
'''

print("\n🎨 Update explode + final save...")
r = c.execute_script(UPDATE, read_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(f"   {msg[:800]}")

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
alive = s.connect_ex(('127.0.0.1', 27182)) == 0
s.close()
print(f"   MCP: {'ALIVE ✅' if alive else 'DEAD ❌'}")

if alive:
    # 最终截图
    print("\n📸 Final screenshots...")
    for d in ['iso-top-right', 'iso-top-left', 'iso-top', 'front']:
        try:
            c.take_screenshot(direction=d, height=1600)
            print(f"   {d}: OK")
        except Exception as e:
            print(f"   {d}: warn")
    
    # 最终统计
    s2 = '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    d = app.activeDocument
    design = d.design
    root = design.rootComponent
    total_bodies = sum(c.bRepBodies.count for c in design.allComponents)
    print(f"FINAL:DOC={d.name}|SAVED={d.isSaved}|COMPS={design.allComponents.count}|OCCS={root.occurrences.count}|BODIES={total_bodies}")
except Exception as e:
    print(f"ERR:{str(e)[:80]}")
'''
    r2 = c.execute_script(s2, read_only=False)
    print(f"\n   {r2.get('message','')[:500]}")

c.disconnect()
print("\n✅ Final update complete")
