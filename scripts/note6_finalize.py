#!/usr/bin/env python3
"""NOTE6 — Final: 爆炸视图变换 + saveAs 保存 + 截图"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

c = FusionMCPClient(timeout=300)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}...")

EXPLODE_SCRIPT = r'''
import adsk.core, adsk.fusion
app = adsk.core.Application.get()
log = []

des_doc = app.activeDocument
design = des_doc.design
root = design.rootComponent
log.append(f"DOC:{des_doc.name}")
log.append(f"OCCS_BEFORE:{root.occurrences.count}")

# 爆炸视图位置 (按文档 2.2 节自下而上顺序)
# x 轴: 横向展开, y 轴: 垂直展开 (自下而上)
positions = {
    # ── 底部: 外壳组 ──
    "710_UpperHousing_draft_v1":      (0,   0,  0),   # 上壳体 基准
    "720_HandleHousing_draft_v1":     (0, -100,  0),   # 手柄壳体 下方
    "730_SiliconeCover_draft_v1":     (0, -150,  0),   # 硅胶套 最下
    "740_BottomDisplay_draft_v1":    (30, -80,  0),   # 曲面屏 侧方
    "750_ButtonPanel_draft_v1":      (30, -60,  0),   # 按键面板 侧方
    "760_HoneycombVent_draft_v1":    (-30,  10,  0),   # 散热孔 侧方

    # ── 中下部: 电机 + 电池 + 控制板 ──
    "100_Motor_draft_v1":            (0,   40,  0),   # 电机 在壳体内
    "110_MotorBracket_draft_v1":    (-30,  50,  0),   # 电机支架
    "120_RubberMount_draft_v1":     (-30,  60,  0),   # 减震垫
    "510_BatteryCell_18650_draft_v1":(40, -20,  0),   # 电池 (6个 排一列)
    "520_BatteryHolder_draft_v1":   (40, -30,  0),   # 电池支架
    "610_MainPCB_draft_v1":          (0,  -40,  0),   # 控制板

    # ── 中部: 偏心轮 + 轴承 + 连杆 ──
    "200_EccentricWheel_draft_v1":   (0,  120,  0),   # 偏心轮 电机上方
    "210_Bearing_608_v1":           (20,  130,  0),   # 第一轴承 偏心轮侧
    "211_Bearing2_608_v1":          (20,  180,  0),   # 第二轴承 连杆侧
    "300_ConnectingRod_draft_v1":    (0,  200,  0),   # 连杆
    "340_RodCap_draft_v1":          (20,  190,  0),   # 连杆压盖

    # ── 上部: 活塞杆 + 滑套 + 软胶套 ──
    "310_PistonRod_draft_v1":        (0,  260,  0),   # 活塞杆
    "320_PistonBushing_draft_v1":    (0,  300,  0),   # 滑套
    "330_SoftRubberSleeve_draft_v1":(20,  310,  0),   # 软胶套

    # ── 顶部: 6 款按摩头 ──
    "410_StandardBallHead_draft_v1":(-60, 360,  0),   # 标准球头 左上
    "420_TriggerPointHead_draft_v1":(-30, 360,  0),   # 小圆头
    "430_FlatHead_draft_v1":           (0, 360,  0),   # 小平头
    "440_LargeBallHead_draft_v1":    (30, 360,  0),   # 大球头
    "450_CushionHead_draft_v1":       (60, 360,  0),   # 减震头
    "460_UShapedHead_draft_v1":      (90, 360,  0),   # U型头
}

transformed = 0
for i in range(root.occurrences.count):
    occ = root.occurrences.item(i)
    nm = occ.component.name
    if nm in positions:
        x, y, z = positions[nm]
        mat = adsk.core.Matrix3D.create()
        mat.translation = adsk.core.Vector3D.create(x, y, z)
        occ.transform = mat
        transformed += 1
        log.append(f"MOVED:{nm}")

log.append(f"TRANSFORMED:{transformed}/{len(positions)}")
log.append(f"STATS:COMPS={design.allComponents.count}|BODIES={sum(c.bRepBodies.count for c in design.allComponents)}")

print("\n".join(log))
'''

SAVE_SCRIPT = r'''
import adsk.core, adsk.fusion
app = adsk.core.Application.get()
log = []

des_doc = app.activeDocument
try:
    # 先尝试获取项目和文件夹
    projects = app.data.projects
    default_proj = projects.itemByName("Default Project")
    if default_proj:
        root_folder = default_proj.rootFolder
        des_doc.saveAs("NOTE6_Assembly_draft_v1", root_folder, 
                      "NOTE6 逆向工程完整爆炸图 — draft v1.0 — 19组件25实体", "draft_v1.0")
        log.append("SAVEAS:OK")
    else:
        # 没有 Default Project 就用 save
        ok = des_doc.save("NOTE6 Assembly draft v1.0 pre-save")
        log.append(f"SAVE_FALLBACK:{ok}")
except Exception as e:
    log.append(f"SAVE_ERR:{str(e)[:150]}")

print("|".join(log))
'''

print("\n🎨 Final: Explode view transform...")
r1 = c.execute_script(EXPLODE_SCRIPT, read_only=False)
msg1 = r1.get('message', str(r1)) if isinstance(r1, dict) else str(r1)
print(f"   {msg1[:1500]}")

import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2)
mcp_ok = sock.connect_ex(('127.0.0.1', 27182)) == 0
sock.close()
print(f"\n   MCP_AFTER_EXPLODE: {'ALIVE ✅' if mcp_ok else 'DEAD ❌'}")

if mcp_ok:
    print("\n💾 Final: saveAs to cloud...")
    r2 = c.execute_script(SAVE_SCRIPT, read_only=False)
    msg2 = r2.get('message', str(r2)) if isinstance(r2, dict) else str(r2)
    print(f"   {msg2[:500]}")

    print("\n📸 Screenshot...")
    try:
        ss = c.take_screenshot(direction='iso-top-right', height=1600)
        print(f"   Screenshot OK")
    except Exception as e:
        print(f"   Screenshot warn: {e}")

c.disconnect()
print("\n✅ NOTE6 build complete!")
