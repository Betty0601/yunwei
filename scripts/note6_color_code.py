#!/usr/bin/env python3
"""
NOTE6 组件分类上色 — 按真实功能逻辑
金属传动件=钢灰 | 电机=深灰 | 轴承=银 | 橡胶=橙 | 外壳=ABS灰 | 电池=绿 | PCB=深绿 | 按摩头=不同色 | 螺钉=黑
"""
import sys, time
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

HEAD = 'def run(context): pass\n'
c = FusionMCPClient(timeout=120)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}")

COLOR_SCRIPT = HEAD + '''
import adsk.core, adsk.fusion, adsk.material
try:
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = app.activeDocument.design
    root = design.rootComponent
    
    # 定义颜色 RGB (0-255)
    colors = {
        "steel_gray":   (128, 128, 135),  # 金属传动件
        "motor_dark":   (80,  80,  90),   # 电机外壳
        "bearing_silver":(192, 192, 200), # 轴承
        "rubber_orange":(230, 120, 50),   # 橡胶/软胶
        "abs_gray":     (180, 180, 185),  # ABS 外壳
        "battery_green":(60,  160, 80),   # 电池
        "pcb_darkgreen":(40,  100, 50),   # PCB
        "massage_blue": (70,  130, 200),  # 标准球形头
        "massage_cyan": (100, 180, 220),  # 小圆头
        "massage_pink": (220, 130, 170),  # 小平头
        "massage_purple":(150, 100, 200), # 大号球形头
        "massage_yellow":(240, 220, 100), # 减震头
        "massage_green":(100, 200, 130),  # U型头
        "screw_black":  (50,  50,  55),   # 螺钉
    }
    
    # 创建外观并应用
    # 用 materialManager 创建颜色外观
    try:
        mat_lib = app.materialLibs.item("Fusion 360 Appearance Library")
    except:
        try:
            mat_lib = app.materialLibs.item(0)
        except:
            mat_lib = None
    
    print(f"LIB:{mat_lib.name if mat_lib else 'None'}")
    
    # 组件 → 颜色 映射
    comp_color_map = {
        # 电机组 (深灰色)
        "100_Motor": "motor_dark",
        "110_MotorBracket": "steel_gray",
        "120_RubberMount": "rubber_orange",
        "220_FasteningScrew": "screw_black",
        
        # 传动核心 (钢灰色金属)
        "200_EccentricWheel": "steel_gray",
        "210_Bearing_608": "bearing_silver",
        "211_Bearing2_608": "bearing_silver",
        
        # 连杆 + 活塞杆 (钢灰色)
        "300_ConnectingRod": "steel_gray",
        "310_PistonRod": "steel_gray",
        "320_PistonBushing": "steel_gray",
        "330_SoftRubberSleeve": "rubber_orange",
        "340_RodCap": "steel_gray",
        "341_RodCapScrew": "screw_black",
        "350_HingeScrew": "screw_black",
        
        # 按摩头 (不同颜色区分)
        "410_StandardBallHead": "massage_blue",
        "420_TriggerPointHead": "massage_cyan",
        "430_FlatHead": "massage_pink",
        "440_LargeBallHead": "massage_purple",
        "450_CushionHead": "massage_yellow",
        "460_UShapedHead": "massage_green",
        
        # 电池 (绿色)
        "510_BatteryCell": "battery_green",
        "511_BatteryCell": "battery_green",
        "512_BatteryCell": "battery_green",
        "513_BatteryCell": "battery_green",
        "514_BatteryCell": "battery_green",
        "515_BatteryCell": "battery_green",
        "516_BatteryCell": "battery_green",
        "520_BatteryHolder": "abs_gray",
        
        # 控制板
        "610_MainPCB": "pcb_darkgreen",
        
        # 外壳 (ABS 灰)
        "710_UpperHousing": "abs_gray",
        "720_HandleHousing": "abs_gray",
        "730_SiliconeCover": "rubber_orange",
        "740_BottomDisplay": "steel_gray",
        "750_ButtonPanel": "steel_gray",
        "760_HoneycombVent": "abs_gray",
        "771_HousingScrew": "screw_black",
        "772_HousingScrew": "screw_black",
        "773_HousingScrew": "screw_black",
        "774_HousingScrew": "screw_black",
    }
    
    # 给每个组件的所有 body 应用颜色
    colored = 0
    skipped = 0
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        comp = occ.component
        comp_name = comp.name
        
        # 找匹配的颜色
        target_color = None
        for key, cname in comp_color_map.items():
            if key in comp_name:
                target_color = cname
                break
        
        if target_color is None:
            skipped += 1
            continue
        
        r, g, b = colors[target_color]
        
        # 给组件里所有 body 设置颜色
        body_count = 0
        for j in range(comp.bRepBodies.count):
            body = comp.bRepBodies.item(j)
            # 创建颜色属性
            try:
                color = adsk.core.Color.create(r, g, b, 255)
                appearance = design.appearances.itemByName(f"NOTE6_{target_color}")
                if appearance is None:
                    appearance = design.appearances.addByColor(
                        f"NOTE6_{target_color}", color)
                body.appearance = appearance
                body_count += 1
            except Exception as e:
                pass
        
        if body_count > 0:
            colored += 1
        else:
            skipped += 1
    
    print(f"COLORED:{colored} SKIPPED:{skipped}")
    
    try:
        app.activeDocument.save("draft v2.0 — color coded")
        print("SAVE:OK")
    except Exception as e:
        print(f"SAVE:ERR:{str(e)[:80]}")

except Exception as fatal:
    print(f"FATAL:{str(fatal)[:200]}")
'''

print("🎨 Applying color coding to 53 components...")
r = c.execute_script(COLOR_SCRIPT, read_only=False)
msg = r.get('message', r.get('error', '')) if isinstance(r, dict) else str(r)
for line in msg.split('\n'):
    if line and 'Traceback' not in line and 'File' not in line and 'run' not in line and 'def' not in line:
        print(f"  {line}")

# 截图
import time; time.sleep(1)
print("\n📸 Color-coded screenshots...")
for direction in ['iso-top-right', 'iso-top-left', 'front', 'top', 'right']:
    try:
        c.take_screenshot(direction=direction, height=1600)
        print(f"  {direction}: OK")
    except Exception as e:
        print(f"  {direction}: err")

c.disconnect()
print("\n✅ Color coding complete")
