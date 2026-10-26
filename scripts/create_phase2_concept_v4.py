#!/usr/bin/env python3
"""阶段 2 DMS Concept v4 — 修复统计 API + saveAs"""
import sys
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import connect

c = connect()

SCRIPT = '''
import adsk.core, adsk.fusion, traceback

_fusion_app = adsk.core.Application.get()
def vi(v): return adsk.core.ValueInput.createByReal(v)
_log = []
def log_msg(m): _log.append(str(m))

try:
    _des = _fusion_app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType, True)
    _design = _des.design
    _doc = _des
    log_msg(f"✅ 新建: {_doc.name}")
    
    root = _design.rootComponent
    params = _design.userParameters

    # 15 个参数
    for nm, val, u, d in [
        ('TMP_MotorDia',40.0,'mm','电机占位直径'),('TMP_MotorLen',50.0,'mm','电机长度'),
        ('TMP_Eccentricity',8.0,'mm','偏心距'),('TMP_CrankLen',10.0,'mm','曲柄半径'),
        ('TMP_RodLen',40.0,'mm','连杆长度'),('TMP_Stroke',16.0,'mm','输出行程'),
        ('TMP_GuideLen',60.0,'mm','导向长度'),('TMP_OutputRodDia',8.0,'mm','输出杆直径'),
        ('TMP_TxHeadDia',18.0,'mm','治疗头直径'),('TMP_FrameLen',80.0,'mm','机架长度'),
        ('TMP_FrameWid',50.0,'mm','机架宽度'),('TMP_FrameHt',35.0,'mm','机架高度'),
        ('TMP_ShaftDia',6.0,'mm','驱动轴直径'),('DRV_Speed',3000.0,'rpm','电机转速'),
        ('KIN_Freq',50.0,'Hz','输出频率')]:
        if not params.itemByName(nm):
            params.add(nm, vi(val), u, d)
    log_msg(f"✅ {params.count} UserParameters")

    # 7 个组件
    def nc(n):
        o = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        o.component.name = n
        return o.component
    c_m=nc('DMS-100_Motor'); c_e=nc('DMS-200A_Eccentric')
    c_c=nc('DMS-200B_CrankSlider'); c_g=nc('DMS-300_GuideOutput')
    c_h=nc('DMS-400_TxHead'); c_f=nc('DMS-500_Frame'); c_s=nc('DMS-600_Housing')
    log_msg(f"✅ 7 组件创建")

    # 几何
    def cyl(co,d,dep,n):
        sk=co.sketches.create(co.xYConstructionPlane); sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0),d/2)
        f=co.features.extrudeFeatures.addSimple(sk.profiles.item(0),vi(dep),adsk.fusion.FeatureOperations.NewBodyFeatureOperation); f.name=n
    def box(co,w,h,d,n):
        sk=co.sketches.create(co.xYConstructionPlane); sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(-w/2,-h/2,0),adsk.core.Point3D.create(w/2,h/2,0))
        f=co.features.extrudeFeatures.addSimple(sk.profiles.item(0),vi(d),adsk.fusion.FeatureOperations.NewBodyFeatureOperation); f.name=n

    box(c_f,80,50,8,'Frame_Bottom'); box(c_s,100,60,70,'HousingShell')
    cyl(c_m,40,50,'MotorBody'); cyl(c_m,8,15,'DriveShaft')
    cyl(c_e,30,6,'EccentricWheel'); cyl(c_c,16,10,'CrankDisc'); box(c_c,6,40,6,'ConnectingRod')
    cyl(c_g,8,60,'OutputRod'); box(c_g,12,12,30,'GuideBush')
    cyl(c_h,18,20,'TreatmentHead'); cyl(c_h,6,10,'HeadMount')

    # 用 design.allComponents 统计 (Fusion 2026+ API)
    total_comps = _design.allComponents.count
    total_bodies = sum(cc.bRepBodies.count for cc in _design.allComponents)
    log_msg(f"✅ 几何完成! 组件:{total_comps-1} 实体体:{total_bodies} 关节:{root.joints.count}")
    
except Exception as e:
    log_msg(f"❌ {traceback.format_exc()}")

print("|".join(_log))
'''

print("🚀 DMS Concept v4...")
result = c.execute_script(SCRIPT, read_only=False)
msg = result.get('message', str(result)) if isinstance(result, dict) else str(result)
print(f"\n📋 {msg[:2000]}")
print("\n📸 截图...")
print(c.take_screenshot())
c.disconnect()
