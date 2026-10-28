#!/usr/bin/env python3
"""NOTE6 上色 — 用正确的 Fusion API (design.appearances + body.appearance)"""
import sys, time
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

HEAD = 'def run(context): pass\n'
c = FusionMCPClient(timeout=120)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}")

COLOR_SCRIPT = HEAD + '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    design = app.activeDocument.design
    root = design.rootComponent
    
    # 颜色定义 (R, G, B, A)
    COLORS = {
        "steel_gray":    (128, 128, 135, 255),  # 金属传动件
        "motor_dark":    (80,  80,  90,  255),  # 电机
        "bearing_silver":(192, 192, 200, 255), # 轴承
        "rubber_orange": (230, 120, 50,  255),  # 橡胶
        "abs_gray":      (180, 180, 185, 255),  # ABS 外壳
        "battery_green": (60,  160, 80,  255),  # 电池
        "pcb_darkgreen": (40,  100, 50,  255),  # PCB
        "massage_blue":  (70,  130, 200, 255),  # 标准球
        "massage_cyan":  (100, 180, 220, 255),  # 小圆
        "massage_pink":  (220, 130, 170, 255),  # 小平
        "massage_purple":(150, 100, 200, 255),  # 大球
        "massage_yellow":(240, 220, 100, 255),  # 减震
        "massage_green": (100, 200, 130, 255),  # U型
        "screw_black":   (50,  50,  55,  255),  # 螺钉
    }
    
    # 先创建所有需要的颜色外观
    appearances = {}
    for name, (r, g, b, a) in COLORS.items():
        try:
            existing = design.appearances.itemByName(f"N6_{name}")
            if existing:
                appearances[name] = existing
            else:
                color = adsk.core.Color.create(r, g, b, a)
                app_lib = app.materialLibs.item("Fusion 360 Appearance Library")
                # 用 Plastic 作为基础模板
                plastic_app = app_lib.appearances.itemByName("Plastic - Matte")
                if plastic_app:
                    new_app = design.appearances.addByCopy(plastic_app, f"N6_{name}")
                    # 设置颜色
                    try:
                        new_prop = new_app.properties.item("Color")
                        if new_prop:
                            new_prop.value = color
                    except:
                        pass
                    appearances[name] = new_app
                else:
                    appearances[name] = None
        except Exception as e:
            print(f"  APP_ERR:{name}:{str(e)[:40]}")
            appearances[name] = None
    
    print(f"APPS_CREATED:{len([v for v in appearances.values() if v is not None])}")
    
    # 组件 → 颜色映射
    MAP = [
        ("100_Motor", "motor_dark"),
        ("110_MotorBracket", "steel_gray"),
        ("120_RubberMount", "rubber_orange"),
        ("220_FasteningScrew", "screw_black"),
        ("200_EccentricWheel", "steel_gray"),
        ("210_Bearing_608", "bearing_silver"),
        ("211_Bearing2_608", "bearing_silver"),
        ("300_ConnectingRod", "steel_gray"),
        ("310_PistonRod", "steel_gray"),
        ("320_PistonBushing", "steel_gray"),
        ("330_SoftRubberSleeve", "rubber_orange"),
        ("340_RodCap", "steel_gray"),
        ("341_RodCapScrew", "screw_black"),
        ("350_HingeScrew", "screw_black"),
        ("410_StandardBallHead", "massage_blue"),
        ("420_TriggerPointHead", "massage_cyan"),
        ("430_FlatHead", "massage_pink"),
        ("440_LargeBallHead", "massage_purple"),
        ("450_CushionHead", "massage_yellow"),
        ("460_UShapedHead", "massage_green"),
        ("510_BatteryCell", "battery_green"),
        ("511_BatteryCell", "battery_green"),
        ("512_BatteryCell", "battery_green"),
        ("513_BatteryCell", "battery_green"),
        ("514_BatteryCell", "battery_green"),
        ("515_BatteryCell", "battery_green"),
        ("516_BatteryCell", "battery_green"),
        ("520_BatteryHolder", "abs_gray"),
        ("610_MainPCB", "pcb_darkgreen"),
        ("710_UpperHousing", "abs_gray"),
        ("720_HandleHousing", "abs_gray"),
        ("730_SiliconeCover", "rubber_orange"),
        ("740_BottomDisplay", "steel_gray"),
        ("750_ButtonPanel", "steel_gray"),
        ("760_HoneycombVent", "abs_gray"),
        ("771_HousingScrew", "screw_black"),
        ("772_HousingScrew", "screw_black"),
        ("773_HousingScrew", "screw_black"),
        ("774_HousingScrew", "screw_black"),
    ]
    
    colored = 0
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        comp = occ.component
        cname = comp.name
        
        target_color = None
        for key, cname_target in MAP:
            if key in cname:
                target_color = cname_target
                break
        
        if target_color is None or target_color not in appearances:
            continue
        
        app_obj = appearances[target_color]
        if app_obj is None:
            continue
        
        for j in range(comp.bRepBodies.count):
            body = comp.bRepBodies.item(j)
            try:
                body.appearance = app_obj
                colored += 1
            except:
                pass
    
    print(f"COLORED_BODIES:{colored}")
    
    try:
        app.activeDocument.save("draft v2.0 — color coded by function")
        print("SAVE:OK")
    except Exception as e:
        print(f"SAVE:ERR:{str(e)[:80]}")

except Exception as fatal:
    print(f"FATAL:{str(fatal)[:200]}")
'''

print("🎨 Applying function-based color coding...")
r = c.execute_script(COLOR_SCRIPT, read_only=False)
msg = r.get('message', r.get('error', '')) if isinstance(r, dict) else str(r)
for line in msg.split('\n'):
    if line and 'Traceback' not in line and 'File' not in line and 'run' not in line and 'def' not in line:
        print(f"  {line}")

import time; time.sleep(1)
print("\n📸 Color-coded screenshots...")
for direction in ['iso-top-right', 'iso-top-left', 'front', 'top', 'right']:
    try:
        c.take_screenshot(direction=direction, height=1600)
        print(f"  {direction}: OK")
    except Exception as e:
        print(f"  {direction}: err")

c.disconnect()
print("\n✅ Done")
