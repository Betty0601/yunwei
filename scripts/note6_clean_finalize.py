#!/usr/bin/env python3
"""NOTE6 Clean v3 — 爆炸位置 + 上色 + saveAs + 截图"""
import sys, time
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

HEAD = 'def run(context): pass\n'
c = FusionMCPClient(timeout=120)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}")

# ========== Step 1: 爆炸视图 ==========
print("\n🎨 Step 1: Explosion view...")
EXPLODE = HEAD + '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    
    # 按文档 2.2 节 + 真实内部结构逻辑
    pos = {
        # 外壳层 (底部)
        "710_UpperHousing":     (0,   0,   0),
        "720_HandleHousing":    (0, -130,  0),
        "730_SiliconeCover":    (0, -200,  0),
        "740_BottomDisplay":   (40, -100, 40),
        "750_ButtonPanel":     (40,  -70, 40),
        "760_HoneycombVent":  (-40,   10, 40),
        "771_HousingScrew":   (60,  -50, 30),
        "772_HousingScrew":   (60,  -60, 30),
        "773_HousingScrew":   (60,  -70, 30),
        "774_HousingScrew":   (60,  -80, 30),
        
        # 电机层 (Y=50)
        "100_Motor":            (0,  50,   0),
        "110_MotorBracket":   (-40,  60,   0),
        "120_RubberMount":    (-40,  70,   0),
        "220_FasteningScrew":  (20,  80,   0),
        
        # 传动核心 (Y=120)
        "200_EccentricWheel":   (0, 120,   0),
        "210_Bearing_608":     (30, 130,   0),
        "211_Bearing2_608":    (30, 180,   0),
        
        # 连杆 (Y=200)
        "300_ConnectingRod":    (0, 200,   0),
        "340_RodCap":         (-30, 190,   0),
        "341_RodCapScrew":    (-40, 200,   0),
        "350_HingeScrew":      (30, 210,   0),
        
        # 活塞杆 (Y=250)
        "310_PistonRod":        (0, 250,   0),
        "320_PistonBushing":   (-30, 260,   0),
        "330_SoftRubberSleeve":(-30, 270,   0),
        
        # 按摩头 (Y=320, 顶部横向展开)
        "410_StandardBallHead": (-90, 320, 0),
        "420_TriggerPointHead": (-55, 320, 0),
        "430_FlatHead":          (-20, 320, 0),
        "440_LargeBallHead":     ( 15, 320, 0),
        "450_CushionHead":       ( 50, 320, 0),
        "460_UShapedHead":       ( 85, 320, 0),
        
        # 电池 (Y=-50, 手柄内部)
        "510_BatteryCell_18650": (40, -50, 0),
        "511_BatteryCell_v2":    (40, -60, 0),
        "512_BatteryCell_v2":    (55, -60, 0),
        "513_BatteryCell_v2":    (70, -60, 0),
        "514_BatteryCell_v2":    (40, -75, 0),
        "515_BatteryCell_v2":    (55, -75, 0),
        "516_BatteryCell_v2":    (70, -75, 0),
        "520_BatteryHolder":     (55, -90, 0),
        
        # PCB
        "610_MainPCB":           (0, -20, 40),
    }
    
    moved = 0
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        nm = occ.component.name
        for key, (x,y,z) in pos.items():
            if key in nm:
                mat = adsk.core.Matrix3D.create()
                mat.translation = adsk.core.Vector3D.create(x,y,z)
                occ.transform = mat
                moved += 1
                break
    
    print(f"EXPLODED:{moved}/{root.occurrences.count}")
except Exception as e:
    print(f"EXPLODE_ERR:{str(e)[:100]}")
'''
r = c.execute_script(EXPLODE, read_only=False)
for line in r.get('message', r.get('error', '')).split('\n'):
    if 'EXPLODED' in line or 'ERR' in line:
        print(f"  {line.strip()}")
time.sleep(0.5)

# ========== Step 2: 上色 ==========
print("\n🎨 Step 2: Coloring (Fusion Appearance Library)...")
COLOR = HEAD + '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    design = app.activeDocument.design
    root = design.rootComponent
    lib = app.materialLibraries.itemByName("Fusion Appearance Library")
    
    # 预加载所有外观到 dict (小写 key)
    all_apps = {}
    for i in range(lib.appearances.count):
        try:
            a = lib.appearances.item(i)
            all_apps[a.name.lower()] = a
        except: pass
    
    def find_app(name):
        return all_apps.get(name.lower())
    
    MAP = [
        ("100_Motor", "Paint - Metallic (Dark Grey)"),
        ("110_MotorBracket", "Steel - Satin"),
        ("120_RubberMount", "Rubber - Hard"),
        ("220_FasteningScrew", "Paint - Metallic (Black)"),
        ("200_EccentricWheel", "Stainless Steel - Polished"),
        ("210_Bearing_608", "Chrome"),
        ("211_Bearing2_608", "Chrome"),
        ("300_ConnectingRod", "Stainless Steel - Polished"),
        ("340_RodCap", "Steel - Satin"),
        ("341_RodCapScrew", "Paint - Metallic (Black)"),
        ("350_HingeScrew", "Paint - Metallic (Black)"),
        ("310_PistonRod", "Stainless Steel - Polished"),
        ("320_PistonBushing", "Steel - Satin"),
        ("330_SoftRubberSleeve", "Rubber - Hard"),
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
        ("520_BatteryHolder", "Plastic - Glossy (Grey)"),
        ("610_MainPCB", "Paint - Metallic (Green)"),
        ("710_UpperHousing", "Plastic - Glossy (Grey)"),
        ("720_HandleHousing", "Plastic - Glossy (Grey)"),
        ("730_SiliconeCover", "Rubber - Soft"),
        ("740_BottomDisplay", "Paint - Metallic (Dark Grey)"),
        ("750_ButtonPanel", "Paint - Metallic (Dark Grey)"),
        ("760_HoneycombVent", "Plastic - Glossy (Grey)"),
        ("771_HousingScrew", "Paint - Metallic (Black)"),
        ("772_HousingScrew", "Paint - Metallic (Black)"),
        ("773_HousingScrew", "Paint - Metallic (Black)"),
        ("774_HousingScrew", "Paint - Metallic (Black)"),
    ]
    
    colored = 0
    not_found = set()
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        comp = occ.component
        cname = comp.name
        
        target = None
        for key, app_name in MAP:
            if key in cname:
                target = find_app(app_name)
                if target is None:
                    not_found.add(app_name)
                break
        
        if target is None:
            continue
        
        for j in range(comp.bRepBodies.count):
            body = comp.bRepBodies.item(j)
            try:
                body.appearance = target
                colored += 1
            except: pass
    
    print(f"COLORED:{colored}")
    if not_found:
        print(f"NOT_FOUND:{not_found}")
    
    try:
        folder = app.data.activeFolder
        app.activeDocument.saveAs("NOTE6_Clean_v3_Complete", folder, "干净重建: 39组件零重复零空壳", "NOTE6")
        print("SAVEAS:OK")
    except Exception as e:
        try:
            app.activeDocument.save("draft v3.0 clean")
            print("SAVE:OK")
        except Exception as e2:
            print(f"SAVE_ERR:{str(e2)[:80]}")
except Exception as fatal:
    print(f"FATAL:{str(fatal)[:200]}")
'''
r = c.execute_script(COLOR, read_only=False)
for line in r.get('message', r.get('error', '')).split('\n'):
    if line and 'Traceback' not in line and 'File' not in line and 'run' not in line and 'def' not in line:
        print(f"  {line.strip()}")

# ========== Step 3: 截图 ==========
import time; time.sleep(1)
print("\n📸 Final screenshots...")
for d in ['iso-top-right', 'iso-top-left', 'front', 'top', 'right']:
    try:
        c.take_screenshot(direction=d, height=1600)
        print(f"  {d}: OK")
    except Exception as e:
        print(f"  {d}: err")

c.disconnect()
print("\n✅ Clean v3 complete!")
