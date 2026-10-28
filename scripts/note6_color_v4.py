#!/usr/bin/env python3
"""NOTE6 上色 v4 — 正确 API: app.materialLibraries + design.appearances"""
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
    
    # 1. 先列出所有可用的 appearance library
    print(f"LIBS_COUNT:{app.materialLibraries.count}")
    lib = None
    for i in range(app.materialLibraries.count):
        l = app.materialLibraries.item(i)
        print(f"  LIB[{i}]:{l.name} | appearances={l.appearances.count}")
        if 'Fusion' in l.name or 'Appearance' in l.name:
            lib = l
    
    if lib is None and app.materialLibraries.count > 0:
        lib = app.materialLibraries.item(0)
    
    # 2. 列出常用外观名
    target_apperances = {
        "steel_gray": None,
        "motor_dark": None,
        "bearing_silver": None,
        "rubber_orange": None,
        "abs_gray": None,
        "battery_green": None,
        "pcb_darkgreen": None,
        "massage_blue": None,
        "screw_black": None,
    }
    
    if lib:
        names = []
        for i in range(lib.appearances.count):
            try:
                an = lib.appearances.item(i).name
                names.append(an)
            except: pass
        
        # 找匹配
        for n in names:
            nl = n.lower()
            if 'steel' in nl and target_apperances["steel_gray"] is None:
                target_apperances["steel_gray"] = n
            elif 'black' in nl and target_apperances["screw_black"] is None:
                target_apperances["screw_black"] = n
            elif 'rubber' in nl and target_apperances["rubber_orange"] is None:
                target_apperances["rubber_orange"] = n
            elif 'plastic' in nl and 'matte' in nl and target_apperances["abs_gray"] is None:
                target_apperances["abs_gray"] = n
        
        print(f"FOUND_NAMES:{target_apperances}")
    
    # 3. 创建自定义颜色外观 (通过 design.appearances)
    # 先找一个基础外观来 copy
    base_app = None
    try:
        if design.appearances.count > 0:
            base_app = design.appearances.item(0)
    except: pass
    
    if base_app is None and lib:
        try:
            base_app = lib.appearances.itemByName("Plastic - Matte")
            if base_app is None:
                base_app = lib.appearances.item(0)
        except: pass
    
    print(f"BASE_APP:{base_app.name if base_app else 'None'}")
    
    # 定义颜色
    COLORS_RGB = {
        "steel_gray":    (128, 128, 135),
        "motor_dark":    (80,  80,  90),
        "bearing_silver":(192, 192, 200),
        "rubber_orange": (230, 120, 50),
        "abs_gray":      (180, 180, 185),
        "battery_green": (60,  160, 80),
        "pcb_darkgreen": (40,  100, 50),
        "massage_blue":  (70,  130, 200),
        "massage_cyan":  (100, 180, 220),
        "massage_pink":  (220, 130, 170),
        "massage_purple":(150, 100, 200),
        "massage_yellow":(240, 220, 100),
        "massage_green": (100, 200, 130),
        "screw_black":   (50,  50,  55),
    }
    
    # 创建颜色外观
    custom_apps = {}
    if base_app:
        for color_name, (r, g, b) in COLORS_RGB.items():
            try:
                existing = design.appearances.itemByName(f"N6_{color_name}")
                if existing:
                    custom_apps[color_name] = existing
                    continue
                
                new_app = design.appearances.addByCopy(base_app, f"N6_{color_name}")
                # 设置颜色属性
                color_prop = new_app.properties.item("Color")
                if color_prop and color_prop.value is not None:
                    # 尝试设置颜色
                    new_color = adsk.core.Color.create(r, g, b, 255)
                    try:
                        color_prop.value = new_color
                    except:
                        pass
                custom_apps[color_name] = new_app
            except Exception as e:
                print(f"  CREATE_ERR:{color_name}:{str(e)[:40]}")
    
    print(f"APPS_READY:{len(custom_apps)}")
    
    # 4. 给组件上色
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
    components_colored = set()
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        comp = occ.component
        cname = comp.name
        
        target_color = None
        for key, cname_target in MAP:
            if key in cname:
                target_color = cname_target
                break
        
        if target_color is None or target_color not in custom_apps:
            continue
        
        app_obj = custom_apps[target_color]
        
        for j in range(comp.bRepBodies.count):
            body = comp.bRepBodies.item(j)
            try:
                body.appearance = app_obj
                colored += 1
                components_colored.add(cname)
            except:
                pass
    
    print(f"COLORED_BODIES:{colored} COMPONENTS:{len(components_colored)}")
    
    try:
        app.activeDocument.save("draft v2.0 — function color coded")
        print("SAVE:OK")
    except Exception as e:
        print(f"SAVE:ERR:{str(e)[:80]}")

except Exception as fatal:
    print(f"FATAL:{str(fatal)[:300]}")
'''

print("🎨 Applying v4 coloring...")
r = c.execute_script(COLOR_SCRIPT, read_only=False)
msg = r.get('message', r.get('error', '')) if isinstance(r, dict) else str(r)
for line in msg.split('\n'):
    if line and 'Traceback' not in line and 'File' not in line and 'run' not in line and 'def' not in line:
        print(f"  {line}")

import time; time.sleep(1)
print("\n📸 Color screenshots...")
for d in ['iso-top-right', 'iso-top-left', 'front', 'top', 'right']:
    try:
        c.take_screenshot(direction=d, height=1600)
        print(f"  {d}: OK")
    except: print(f"  {d}: err")

c.disconnect()
print("\n✅ Done")
