#!/usr/bin/env python3
"""NOTE6 Final: 爆炸视图 + saveAs + 截图"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

c = FusionMCPClient(timeout=300)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}...")

# 爆炸视图位置 (按文档 2.2 自下而上)
EXPLODE = r'''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    des_doc = app.activeDocument
    design = des_doc.design
    root = design.rootComponent
    print(f"OCCS:{root.occurrences.count}")
    
    positions = {
        # 外壳底层
        "710_UpperHousing_draft_v1":       (0,    0,  0),
        "720_HandleHousing_draft_v1":      (0, -120,  0),
        "730_SiliconeCover_draft_v1":      (0, -180,  0),
        "740_BottomDisplay_draft_v1":    (40, -100,  0),
        "750_ButtonPanel_draft_v1":      (40,  -70,  0),
        "760_HoneycombVent_draft_v1":   (-40,   10,  0),
        # 电机层
        "100_Motor_draft_v1":              (0,   60,  0),
        "110_MotorBracket_draft_v1":    (-40,   70,  0),
        "120_RubberMount_draft_v1":     (-40,   80,  0),
        # 电池+控制板
        "510_BatteryCell_18650_draft_v1":(60,  -30,  0),
        "520_BatteryHolder_draft_v1":   (60,  -40,  0),
        "610_MainPCB_draft_v1":           (0,  -50,  0),
        # 传动核心
        "200_EccentricWheel_draft_v1":     (0,  140,  0),
        "210_Bearing_608_v1":             (30,  150,  0),
        "211_Bearing2_608_v1":           (30,  210,  0),
        "300_ConnectingRod_draft_v1":      (0,  230,  0),
        "340_RodCap_draft_v1":           (30,  220,  0),
        # 活塞杆组
        "310_PistonRod_draft_v1":          (0,  290,  0),
        "320_PistonBushing_draft_v1":      (0,  340,  0),
        "330_SoftRubberSleeve_draft_v1":  (30,  350,  0),
        # 按摩头 顶部一排
        "410_StandardBallHead_draft_v1": (-80, 410,  0),
        "420_TriggerPointHead_draft_v1": (-50, 410,  0),
        "430_FlatHead_draft_v1":          (-20, 410,  0),
        "440_LargeBallHead_draft_v1":      (10, 410,  0),
        "450_CushionHead_draft_v1":       (40, 410,  0),
        "460_UShapedHead_draft_v1":       (70, 410,  0),
    }
    
    moved = 0
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        nm = occ.component.name
        if nm in positions:
            x, y, z = positions[nm]
            mat = adsk.core.Matrix3D.create()
            mat.translation = adsk.core.Vector3D.create(x, y, z)
            try:
                occ.transform = mat
                moved += 1
            except Exception as e:
                print(f"MOVE_ERR:{nm}:{str(e)[:40]}")
    print(f"EXPLODED:{moved}/{len(positions)}")
    
    # saveAs
    try:
        projects = app.data.projects
        default_proj = projects.itemByName("Default Project")
        if default_proj:
            root_folder = default_proj.rootFolder
            des_doc.saveAs("NOTE6_Assembly_draft_v1", root_folder,
                          "NOTE6 逆向工程完整爆炸图 — draft v1.0 — 26组件35实体", "draft_v1.0")
            print("SAVEAS:OK")
        else:
            try:
                des_doc.save("draft v1.0")
                print("SAVE_FALLBACK:OK")
            except Exception as e2:
                print(f"SAVE_FALLBACK:ERR:{str(e2)[:80]}")
    except Exception as e1:
        print(f"SAVEAS:ERR:{str(e1)[:100]}")
        
except Exception as fatal:
    print(f"FATAL:{str(fatal)[:150]}")
'''

print("\n🎨 Explode view + saveAs...")
r = c.execute_script(EXPLODE, read_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(f"   {msg[:1500]}")

# 截图
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
mcp_ok = s.connect_ex(('127.0.0.1', 27182)) == 0
s.close()
print(f"\n   MCP: {'ALIVE ✅' if mcp_ok else 'DEAD ❌'}")

if mcp_ok:
    print("\n📸 Taking screenshots...")
    for direction, tag in [('iso-top-right','ISO_TOP'), ('front','FRONT'), ('top','TOP')]:
        try:
            ss = c.take_screenshot(direction=direction, height=1600)
            print(f"   Screenshot {tag}: OK")
        except Exception as e:
            print(f"   Screenshot {tag}: warn {str(e)[:40]}")

c.disconnect()
print("\n✅ Finalization attempt complete")
