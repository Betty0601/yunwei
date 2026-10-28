#!/usr/bin/env python3
"""NOTE6 上色 v5 — 直接用 Fusion Appearance Library 已有外观名"""
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
    
    # 1. 获取 Fusion Appearance Library
    lib = app.materialLibraries.itemByName("Fusion Appearance Library")
    if lib is None:
        lib = app.materialLibraries.item(2)  # 之前探测是 index 2
    print(f"LIB:{lib.name} | {lib.appearances.count} apps")
    
    # 2. 列出所有可用外观名 (按关键字分类)
    all_names = []
    for i in range(lib.appearances.count):
        try:
            all_names.append(lib.appearances.item(i).name)
        except: pass
    
    # 按关键字筛选
    keywords = ['Steel', 'Metal', 'Black', 'Rubber', 'Plastic', 'Green', 'Red', 
                'Blue', 'Yellow', 'Orange', 'Pink', 'Purple', 'Silver', 'Gray',
                'Grey', 'Copper', 'Brass', 'Aluminum', 'Brass', 'Chrome', 'Nickel']
    
    print("\\nAVAILABLE_APPEARANCES (by category):")
    for kw in keywords:
        matches = [n for n in all_names if kw.lower() in n.lower()]
        if matches:
            print(f"  [{kw}]")
            for m in matches[:8]:
                print(f"    {m}")
    
    # 3. 组件 → 外观名 映射 (用 Fusion 库里已有的)
    # 先从 design 里找是否已有库外观的 copy
    MAP = [
        # 金属传动件 → Steel
        ("100_Motor", "Stainless Steel - Polished"),
        ("110_MotorBracket", "Steel - Satin"),
        ("200_EccentricWheel", "Stainless Steel - Polished"),
        ("210_Bearing_608", "Chrome - Polished"),
        ("211_Bearing2_608", "Chrome - Polished"),
        ("220_FasteningScrew", "Black - Matte"),
        ("300_ConnectingRod", "Stainless Steel - Polished"),
        ("310_PistonRod", "Stainless Steel - Polished"),
        ("320_PistonBushing", "Steel - Satin"),
        ("330_SoftRubberSleeve", "Rubber - Satin"),
        ("340_RodCap", "Steel - Satin"),
        ("341_RodCapScrew", "Black - Matte"),
        ("350_HingeScrew", "Black - Matte"),
        ("120_RubberMount", "Rubber - Satin"),
        
        # 按摩头 (不同颜色)
        ("410_StandardBallHead", "Blue - Glossy"),
        ("420_TriggerPointHead", "Cyan - Glossy"),
        ("430_FlatHead", "Pink - Glossy"),
        ("440_LargeBallHead", "Purple - Glossy"),
        ("450_CushionHead", "Yellow - Glossy"),
        ("460_UShapedHead", "Green - Glossy"),
        
        # 电池
        ("510_BatteryCell", "Green - Satin"),
        ("511_BatteryCell", "Green - Satin"),
        ("512_BatteryCell", "Green - Satin"),
        ("513_BatteryCell", "Green - Satin"),
        ("514_BatteryCell", "Green - Satin"),
        ("515_BatteryCell", "Green - Satin"),
        ("516_BatteryCell", "Green - Satin"),
        ("520_BatteryHolder", "Plastic - Matte"),
        
        # PCB
        ("610_MainPCB", "Green - Satin"),
        
        # 外壳
        ("710_UpperHousing", "Plastic - Matte"),
        ("720_HandleHousing", "Plastic - Matte"),
        ("730_SiliconeCover", "Rubber - Satin"),
        ("740_BottomDisplay", "Black - Matte"),
        ("750_ButtonPanel", "Black - Matte"),
        ("760_HoneycombVent", "Plastic - Matte"),
        ("771_HousingScrew", "Black - Matte"),
        ("772_HousingScrew", "Black - Matte"),
        ("773_HousingScrew", "Black - Matte"),
        ("774_HousingScrew", "Black - Matte"),
    ]
    
    # 4. 上色 (跳过库中不存在的外观名)
    found_cache = {}
    colored = 0
    skipped_app = 0
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        comp = occ.component
        cname = comp.name
        
        target_app_name = None
        for key, app_name in MAP:
            if key in cname:
                target_app_name = app_name
                break
        
        if target_app_name is None:
            continue
        
        # 在 Fusion Appearance Library 里找
        if target_app_name not in found_cache:
            found = lib.appearances.itemByName(target_app_name)
            found_cache[target_app_name] = found
        
        app_obj = found_cache[target_app_name]
        if app_obj is None:
            skipped_app += 1
            continue
        
        for j in range(comp.bRepBodies.count):
            body = comp.bRepBodies.item(j)
            try:
                body.appearance = app_obj
                colored += 1
            except Exception as e:
                pass
    
    print(f"\\nCOLORED_BODIES:{colored}")
    print(f"SKIPPED_NOT_FOUND:{skipped_app}")
    
    # 打印没找到的外观名
    not_found = [name for name, found in found_cache.items() if found is None]
    if not_found:
        print(f"NOT_FOUND_NAMES:{not_found[:15]}")
    
    try:
        app.activeDocument.save("draft v2.0 — library color coded")
        print("SAVE:OK")
    except Exception as e:
        print(f"SAVE:ERR:{str(e)[:80]}")

except Exception as fatal:
    print(f"FATAL:{str(fatal)[:300]}")
'''

print("🎨 v5 coloring with Fusion library...")
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
