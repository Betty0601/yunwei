#!/usr/bin/env python3
"""修复大小写问题: XY → xY, XZ → xZ"""
import sys, time
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient

HEAD = 'def run(context): pass\n'
c = FusionMCPClient(timeout=120)
c.connect()
print(f"✅ MCP: {c.session_id[:8]}")

# 当前文档已 saveAs, 直接追加
def fix(name, code):
    full = HEAD + code
    r = c.execute_script(full, read_only=False)
    msg = r.get('message', r.get('error', ''))
    ok = False
    for line in msg.split('\n'):
        if 'OK:' in line or 'ERR:' in line:
            print(f"  {line.strip()}")
            ok = True
    time.sleep(0.2)

print("\n🔧 Fixing construction plane casing errors...")

fix("100_Motor", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "100_Motor_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 27.5)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(60), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xYConstructionPlane, vi(30))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 3)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(75), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:100_MOTOR")
except Exception as e: print(f"ERR:100:{str(e)[:60]}")
''')

fix("110_Bracket", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "110_MotorBracket_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 35)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 27.5)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(8), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:110_BRACKET")
except Exception as e: print(f"ERR:110:{str(e)[:60]}")
''')

fix("120_RubberMount", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "120_RubberMount_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 40)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 28)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(6), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:120_RUBBER")
except Exception as e: print(f"ERR:120:{str(e)[:60]}")
''')

fix("200_EccentricWheel_v2", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "200_EccentricWheel_v2"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    # 圆盘 φ30×10
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 15)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(10), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # 中心孔 φ6 @ (0,0,0)
    sk2 = comp.sketches.add(comp.xYConstructionPlane)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 3)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(12), adsk.fusion.FeatureOperations.CutFeatureOperation)
    # 偏心臂末端孔 φ8 @ (10,0,0)
    sk3 = comp.sketches.add(comp.xYConstructionPlane)
    sk3.sketchCurves.sketchCircles.addByCenterRadius(pt3(10,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk3.profiles.item(0), vi(12), adsk.fusion.FeatureOperations.CutFeatureOperation)
    print("OK:200_ECCENTRIC")
except Exception as e: print(f"ERR:200:{str(e)[:60]}")
''')

fix("210_Bearing1", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "210_Bearing_608_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 11)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(7), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:210_BEARING1")
except Exception as e: print(f"ERR:210:{str(e)[:60]}")
''')

fix("211_Bearing2", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "211_Bearing2_608_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 11)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(7), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:211_BEARING2")
except Exception as e: print(f"ERR:211:{str(e)[:60]}")
''')

fix("220_ScrewMotor", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "220_FasteningScrew_v2"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(3), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, vi(3))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 2)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(8), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:220_SCREW_MOTOR")
except Exception as e: print(f"ERR:220:{str(e)[:60]}")
''')

fix("340_RodCap", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "340_RodCap_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 8)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 4)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(4), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:340_CAP")
except Exception as e: print(f"ERR:340:{str(e)[:60]}")
''')

fix("341_CapScrew", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "341_RodCapScrew_v2"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 3)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(2), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, vi(2))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 1.5)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(4), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:341_CAPSCREW")
except Exception as e: print(f"ERR:341:{str(e)[:60]}")
''')

fix("320_Bushing", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "320_PistonBushing_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 9)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 5.05)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(25), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:320_BUSHING")
except Exception as e: print(f"ERR:320:{str(e)[:60]}")
''')

fix("330_SoftRubber", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "330_SoftRubberSleeve_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 11)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 9.5)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(20), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:330_SOFTRUBBER")
except Exception as e: print(f"ERR:330:{str(e)[:60]}")
''')

fix("350_HingeScrew", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "350_HingeScrew_v2"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 5)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(4), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xZConstructionPlane, vi(4))
    p2 = comp.constructionPlanes.add(inp)
    sk2 = comp.sketches.add(p2)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 2.5)
    comp.features.extrudeFeatures.addSimple(sk2.profiles.item(0), vi(10), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:350_HINGE")
except Exception as e: print(f"ERR:350:{str(e)[:60]}")
''')

fix("510_Battery18650", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "510_BatteryCell_18650_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 9)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(65), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:510_BATTERY")
except Exception as e: print(f"ERR:510:{str(e)[:60]}")
''')

fix("730_Silicone", '''
import adsk.core, adsk.fusion
try:
    app = adsk.core.Application.get()
    root = app.activeDocument.design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = "730_SiliconeCover_draft_v1"
    def vi(v): return adsk.core.ValueInput.createByReal(v)
    def pt3(x,y,z): return adsk.core.Point3D.create(x,y,z)
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 38)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt3(0,0,0), 34)
    comp.features.extrudeFeatures.addSimple(sk.profiles.item(1), vi(90), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    print("OK:730_SILICONE")
except Exception as e: print(f"ERR:730:{str(e)[:60]}")
''')

# FINAL VERIFY + SAVE + SCREENSHOTS
print("\n" + "="*60)
print("📊 FINAL VERIFICATION")
print("="*60)
FINAL = HEAD + '''
import adsk.core
try:
    app = adsk.core.Application.get()
    d = app.activeDocument
    design = d.design
    root = design.rootComponent
    bodies = sum(c.bRepBodies.count for c in design.allComponents)
    print(f"FINAL:DOC={d.name}|COMPS={design.allComponents.count}|OCCS={root.occurrences.count}|BODIES={bodies}")
    try:
        d.save("draft v2.0 — complete all 40+ components")
        print("SAVE:OK")
    except Exception as e:
        print(f"SAVE:ERR:{str(e)[:80]}")
except Exception as e:
    print(f"V_ERR:{str(e)[:100]}")
'''
r = c.execute_script(FINAL, read_only=False)
print(f"  {r.get('message', r.get('error',''))[:500]}")

# Screenshots
print("\n📸 Screenshots...")
for direction in ['iso-top-right', 'iso-top-left', 'front', 'top']:
    try:
        c.take_screenshot(direction=direction, height=1600)
        print(f"  {direction}: OK")
    except Exception as e:
        print(f"  {direction}: err")

c.disconnect()
print("\n✅ ALL COMPLETE!")
