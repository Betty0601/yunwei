#!/usr/bin/env python3
"""NOTE6 上色 v7 — robust: try/except 包裹每个外观查找"""
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
    
    lib = None
    try:
        lib = app.materialLibraries.itemByName("Fusion Appearance Library")
    except:
        lib = app.materialLibraries.item(2)
    
    print(f"LIB:{lib.name}")
    
    # 先把库中所有外观名放进一个 dict 里 (小写 key)
    all_apperances = {}
    for i in range(lib.appearances.count):
        try:
            a = lib.appearances.item(i)
            all_apperances[a.name.lower()] = a
        except: pass
    print(f"ALL_APPS:{len(all_apperances)}")
    
    # 组件关键字 → 目标外观名 (小写匹配)
    MAP = [
        ("100_Motor", "Paint - Metallic (Dark Grey)"),
        ("110_MotorBracket", "Steel - Satin"),
        ("200_EccentricWheel", "Stainless Steel - Polished"),
        ("210_Bearing_608", "Chrome"),
        ("211_Bearing2_608", "Chrome"),
        ("220_FasteningScrew", "Paint - Metallic (Black)"),
        ("300_ConnectingRod", "Stainless Steel - Polished"),
        ("310_PistonRod", "Stainless Steel - Polished"),
        ("320_PistonBushing", "Steel - Satin"),
        ("330_SoftRubberSleeve", "Rubber - Hard"),
        ("340_RodCap", "Steel - Satin"),
        ("341_RodCapScrew", "Paint - Metallic (Black)"),
        ("350_HingeScrew", "Paint - Metallic (Black)"),
        ("120_RubberMount", "Rubber - Hard"),
        ("410_StandardBallHead", "Paint - Metallic (Silver)"),
        ("420_TriggerPointHead", "Paint - Metallic (Blue)"),
        ("430_FlatHead", "Aluminum - Anodized Glossy (Red)"),
        ("440_LargeBallHead", "Paint - Metallic (Green)"),
        ("450_CushionHead", "Rubber - Soft"),
        ("460_UShapedHead", "Aluminum - Anodized Glossy (Grey)"),
        ("510_BatteryCell", "Plastic - Glossy (Green)"),
        ("511_BatteryCell", "Plastic - Glossy (Green)"),
        ("512_BatteryCell", "Plastic - Glossy (Green)"),
        ("513_BatteryCell", "Plastic - Glossy (Green)"),
        ("514_BatteryCell", "Plastic - Glossy (Green)"),
        ("515_BatteryCell", "Plastic - Glossy (Green)"),
        ("516_BatteryCell", "Plastic - Glossy (Green)"),
        ("520_BatteryHolder", "Plastic - Matte (Grey)"),
        ("610_MainPCB", "Paint - Metallic (Green)"),
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
    
    # 上色
    colored = 0
    comps_colored = set()
    not_found_names = set()
    
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        comp = occ.component
        cname = comp.name
        
        target_app = None
        for key, app_name in MAP:
            if key in cname:
                target_app = all_apperances.get(app_name.lower())
                if target_app is None:
                    not_found_names.add(app_name)
                break
        
        if target_app is None:
            continue
        
        for j in range(comp.bRepBodies.count):
            body = comp.bRepBodies.item(j)
            try:
                body.appearance = target_app
                colored += 1
                comps_colored.add(cname)
            except:
                pass
    
    print(f"COLORED_BODIES:{colored}")
    print(f"COLORED_COMPS:{len(comps_colored)}")
    if not_found_names:
        print(f"NOT_FOUND:{not_found_names}")
    
    try:
        app.activeDocument.save("draft v2.0 — colored v7")
        print("SAVE:OK")
    except Exception as e:
        print(f"SAVE:ERR:{str(e)[:80]}")

except Exception as fatal:
    print(f"FATAL:{str(fatal)[:200]}")
'''

print("🎨 v7 robust coloring...")
r = c.execute_script(COLOR_SCRIPT, read_only=False)
msg = r.get('message', r.get('error', '')) if isinstance(r, dict) else str(r)
for line in msg.split('\n'):
    if line and 'Traceback' not in line and 'File' not in line and 'run' not in line and 'def' not in line:
        print(f"  {line}")

import time; time.sleep(1)
print("\n📸 Final colored screenshots...")
for d in ['iso-top-right', 'iso-top-left', 'front', 'top', 'right']:
    try:
        c.take_screenshot(direction=d, height=1600)
        print(f"  {d}: OK")
    except: print(f"  {d}: err")

c.disconnect()
print("\n✅ All done!")
