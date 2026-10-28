#!/usr/bin/env python3
"""
NOTE6 爆炸视图变换 — 按真实逻辑
自下而上: 外壳 → 控制板 → 电池 → 电机 → 偏心轮 → 连杆 → 活塞杆 → 按摩头

坐标系:
  - X 轴: 水平 (活塞杆伸缩方向)
  - Y 轴: 竖直 (手柄方向)
  - Z 轴: 垂直纸面
  
爆炸间距: 每层 50mm 间隔
"""
import sys, time
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

HEAD = 'def run(context): pass\n'
c = FusionMCPClient(timeout=120)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}")

# 爆炸视图变换 — 按文档 2.2 节 + 真实内部结构逻辑
# 每层 Y 偏移 + 特殊组件的 X/Z 偏移
EXPLODE_SCRIPT = HEAD + '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ_count = root.occurrences.count
    print(f"OCC_COUNT:{occ_count}")
    
    # 爆炸位置字典 (按组件名匹配)
    # Y=0 为外壳层 (底部), Y=+250 为按摩头 (顶部)
    explode_positions = {}
    
    # ── 第 1 层: 外壳组 (最底层) ── Y=0
    explode_positions["710_UpperHousing"]     = (0,   0,  0)   # 上壳体
    explode_positions["720_HandleHousing"]    = (0, -80,  0)   # 手柄壳体 (向下)
    explode_positions["730_SiliconeCover"]    = (0,-160,  0)   # 硅胶套 (手柄外)
    explode_positions["740_BottomDisplay"]    = (20,-100, 40)  # 曲面屏 (手柄底部)
    explode_positions["750_ButtonPanel"]      = (20, -70, 40)  # 按键面板
    explode_positions["760_HoneycombVent"]    = (-20, 20, 40)  # 散热孔 (上壳)
    explode_positions["771_HousingScrew"]     = (30,-50, 30)   # 外壳螺钉
    explode_positions["772_HousingScrew"]     = (30,-60, 30)
    explode_positions["773_HousingScrew"]     = (30,-70, 30)
    explode_positions["774_HousingScrew"]     = (30,-80, 30)
    
    # ── 第 2 层: 电机组 (Y=50) ──
    explode_positions["100_Motor"]             = (0,  50,  0)
    explode_positions["110_MotorBracket"]      = (-40, 60, 0)  # 支架 (电机后)
    explode_positions["120_RubberMount"]       = (-40, 70, 0)  # 橡胶减震垫
    explode_positions["220_FasteningScrew"]    = (20, 80, 0)   # 电机端紧固螺钉
    
    # ── 第 3 层: 传动核心 (Y=120-180) ──
    explode_positions["200_EccentricWheel"]    = (0, 120,  0)  # 偏心轮 (连电机输出轴)
    explode_positions["210_Bearing_608"]       = (30,130,  0)  # 第一轴承 (偏心臂端)
    explode_positions["211_Bearing2_608"]      = (30,180,  0)  # 第二轴承 (连杆端)
    
    # ── 第 4 层: 连杆 + 压盖 (Y=200) ──
    explode_positions["300_ConnectingRod"]    = (0, 200,  0)  # 水平连杆
    explode_positions["340_RodCap"]            = (-30,190,  0) # 连杆压盖
    explode_positions["341_RodCapScrew"]       = (-40,200,  0) # 压盖螺钉
    explode_positions["350_HingeScrew"]        = (30,210,  0)  # 铰接螺钉
    
    # ── 第 5 层: 活塞杆组件 (Y=250) ──
    explode_positions["310_PistonRod"]         = (0, 250,  0)  # 活塞杆 (沿 X 伸)
    explode_positions["320_PistonBushing"]     = (-30,260,  0) # 滑套
    explode_positions["330_SoftRubberSleeve"]  = (-30,270,  0) # 软胶套
    
    # ── 第 6 层: 电池组 (手柄内部, Y=-50) ──
    explode_positions["510_BatteryCell_18650"] = (40,-50,  0)  # 占位
    explode_positions["511_BatteryCell_v2"]    = (40,-60,  0)
    explode_positions["512_BatteryCell_v2"]    = (55,-60,  0)
    explode_positions["513_BatteryCell_v2"]    = (70,-60,  0)
    explode_positions["514_BatteryCell_v2"]    = (40,-75,  0)
    explode_positions["515_BatteryCell_v2"]    = (55,-75,  0)
    explode_positions["516_BatteryCell_v2"]    = (70,-75,  0)
    explode_positions["520_BatteryHolder"]     = (55,-90,  0)
    
    # ── 第 7 层: 控制板 (手柄内, Y=-20) ──
    explode_positions["610_MainPCB"]           = (0, -20, 40)
    
    # ── 第 8 层: 6 款按摩头 (顶部横向展开, Y=320) ──
    head_positions = [(-90, 320, 0), (-55, 320, 0), (-20, 320, 0),
                      (15, 320, 0), (50, 320, 0), (85, 320, 0)]
    head_names = ["410_StandardBallHead", "420_TriggerPointHead", 
                  "430_FlatHead", "440_LargeBallHead",
                  "450_CushionHead", "460_UShapedHead"]
    for name, pos in zip(head_names, head_positions):
        explode_positions[name] = pos
    
    # 遍历所有 occurrence, 匹配名称关键字并设置位置
    moved = 0
    unmatched = []
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        full_name = occ.component.name
        
        matched = False
        for key, (x, y, z) in explode_positions.items():
            if key in full_name:
                try:
                    mat = adsk.core.Matrix3D.create()
                    mat.translation = adsk.core.Vector3D.create(x, y, z)
                    occ.transform = mat
                    moved += 1
                    matched = True
                except Exception as e:
                    print(f"ERR_MOVE:{full_name[:20]}:{str(e)[:30]}")
                break
        
        if not matched:
            unmatched.append(full_name)
    
    print(f"EXPLODED:{moved}/{occ_count}")
    if unmatched:
        print(f"UNMATCHED:{len(unmatched)}")
        for n in unmatched[:10]:
            print(f"  {n}")
    
    try:
        app.activeDocument.save("draft v2.0 — explosion view")
        print("SAVE:OK")
    except Exception as e:
        print(f"SAVE:ERR:{str(e)[:80]}")

except Exception as fatal:
    print(f"FATAL:{str(fatal)[:150]}")
'''

print("🎨 Setting explosion view positions...")
r = c.execute_script(EXPLODE_SCRIPT, read_only=False)
msg = r.get('message', r.get('error', '')) if isinstance(r, dict) else str(r)
for line in msg.split('\n'):
    if line and 'Traceback' not in line and 'File' not in line and 'run' not in line and 'def' not in line:
        print(f"  {line}")

# 最终截图
import time; time.sleep(1)
print("\n📸 Final explosion view screenshots...")
for direction in ['iso-top-right', 'iso-top-left', 'front', 'top', 'right', 'iso-top']:
    try:
        c.take_screenshot(direction=direction, height=1600)
        print(f"  {direction}: OK")
    except Exception as e:
        print(f"  {direction}: err")

c.disconnect()
print("\n✅ Explosion view complete")
