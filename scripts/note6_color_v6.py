#!/usr/bin/env python3
"""NOTE6 上色 v6 — 用 Fusion Appearance Library 里确认存在的外观名"""
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
    
    lib = app.materialLibraries.itemByName("Fusion Appearance Library")
    
    # 从之前探测确认可用的外观名
    # 金属传动件 → Stainless Steel / Steel
    # 电机 → Dark Grey Metallic Paint
    # 轴承 → Chrome / Nickel
    # 橡胶 → Rubber - Hard / Soft
    # 外壳 ABS → Plastic - Matte (Grey)
    # 电池 → Green Plastic
    # PCB → Green Paint
    # 按摩头 → 不同颜色 Anodized Aluminum / Plastic
    # 螺钉 → Black Plastic
    
    # 组件名关键字 → Fusion 外观名
    # 只用之前探测确认存在的!
    MAP = [
        # 电机 (深灰色金属漆)
        ("100_Motor", "Paint - Metallic (Dark Grey)"),
        
        # 支架 + 轴承 + 螺钉 (金属)
        ("110_MotorBracket", "Steel - Satin"),
        ("200_EccentricWheel", "Stainless Steel - Polished"),
        ("210_Bearing_608", "Chrome"),
        ("211_Bearing2_608", "Chrome"),
        ("220_FasteningScrew", "Paint - Metallic (Black)"),
        
        # 连杆 + 活塞杆组件 (CNC 精加工金属)
        ("300_ConnectingRod", "Stainless Steel - Polished"),
        ("310_PistonRod", "Stainless Steel - Polished"),
        ("320_PistonBushing", "Steel - Satin"),
        ("330_SoftRubberSleeve", "Rubber - Hard"),
        ("340_RodCap", "Steel - Satin"),
        ("341_RodCapScrew", "Paint - Metallic (Black)"),
        ("350_HingeScrew", "Paint - Metallic (Black)"),
        ("120_RubberMount", "Rubber - Hard"),
        
        # 按摩头 — 不同颜色区分!
        ("410_StandardBallHead", "Paint - Metallic (Silver)"),
        ("420_TriggerPointHead", "Paint - Metallic (Blue)"),
        ("430_FlatHead", "Aluminum - Anodized Glossy (Red)"),
        ("440_LargeBallHead", "Paint - Metallic (Green)"),
        ("450_CushionHead", "Rubber - Soft"),
        ("460_UShapedHead", "Aluminum - Anodized Glossy (Grey)"),
        
        # 电池 (绿色)
        ("510_BatteryCell", "Plastic - Glossy (Green)"),
        ("511_BatteryCell", "Plastic - Glossy (Green)"),
        ("512_BatteryCell", "Plastic - Glossy (Green)"),
        ("513_BatteryCell", "Plastic - Glossy (Green)"),
        ("514_BatteryCell", "Plastic - Glossy (Green)"),
        ("515_BatteryCell", "Plastic - Glossy (Green)"),
        ("516_BatteryCell", "Plastic - Glossy (Green)"),
        ("520_BatteryHolder", "Plastic - Matte (Grey)"),
        
        # PCB
        ("610_MainPCB", "Paint - Metallic (Green)"),
        
        # 外壳 (ABS 阻燃塑料 = 灰色哑光)
        ("710_UpperHousing", "Plastic - Matte (Grey)"),
        ("720_HandleHousing", "Plastic - Matte (Grey)"),
        ("730_SiliconeCover", "Rubber - Soft"),
        ("740_BottomDisplay", "Paint - Metallic (Dark Grey)"),
        ("750_ButtonPanel", "Paint - Metallic (Dark Grey)"),
        ("760_HoneycombVent", "Plastic - Matte (Grey)"),
        ("771_HousingScrew", "Paint - Metallic (Black)"),
        ("772_HousingScrew", "Paint - Metallic (Black)"),
        ("773_HousingScrew", "Paint - Metallic (Black)"),
        ("774_HousingScrew", "Paint - Metallic (Black)"),
    ]
    
    # 预加载所有需要的外观
    app_cache = {}
    for _, app_name in MAP:
        if app_name not in app_cache:
            found = lib.appearances.itemByName(app_name)
            app_cache[app_name] = found
            if found is None:
                print(f"  NOT_FOUND:{app_name}")
    
    print(f"APPS_LOADED:{len([v for v in app_cache.values() if v is not None])}/{len(app_cache)}")
    
    # 应用上色
    colored_bodies = 0
    colored_comps = set()
    skipped = 0
    
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        comp = occ.component
        cname = comp.name
        
        target_app = None
        for key, app_name in MAP:
            if key in cname:
                target_app = app_cache.get(app_name)
                break
        
        if target_app is None:
            skipped += 1
            continue
        
        for j in range(comp.bRepBodies.count):
            body = comp.bRepBodies.item(j)
            try:
                body.appearance = target_app
                colored_bodies += 1
                colored_comps.add(cname)
            except Exception as e:
                pass
    
    print(f"COLORED_BODIES:{colored_bodies}")
    print(f"COLORED_COMPONENTS:{len(colored_comps)}")
    print(f"SKIPPED_NO_MATCH:{skipped}")
    
    try:
        app.activeDocument.save("draft v2.0 — professionally color coded")
        print("SAVE:OK")
    except Exception as e:
        print(f"SAVE:ERR:{str(e)[:80]}")

except Exception as fatal:
    print(f"FATAL:{str(fatal)[:200]}")
'''

print("🎨 v6 professional coloring...")
r = c.execute_script(COLOR_SCRIPT, read_only=False)
msg = r.get('message', r.get('error', '')) if isinstance(r, dict) else str(r)
for line in msg.split('\n'):
    if line and 'Traceback' not in line and 'File' not in line and 'run' not in line and 'def' not in line:
        print(f"  {line}")

import time; time.sleep(1)
print("\n📸 Professionally colored screenshots...")
for d in ['iso-top-right', 'iso-top-left', 'front', 'top', 'right']:
    try:
        c.take_screenshot(direction=d, height=1600)
        print(f"  {d}: OK")
    except: print(f"  {d}: err")

c.disconnect()
print("\n✅ Done!")
