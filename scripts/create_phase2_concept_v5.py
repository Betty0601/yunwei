#!/usr/bin/env python3
"""阶段 2 DMS Concept — 修复 saveAs"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import connect

c = connect()

SCRIPT = '''
import adsk.core, adsk.fusion

app = adsk.core.Application.get()
def vi(v): return adsk.core.ValueInput.createByReal(v)
out = []

# 关掉多余的 untitled
for d in list(app.documents):
    if not d.isSaved and 'DMS' not in d.name and 'Baseline' not in d.name:
        try: d.close(False)
        except: pass

# 新建
des_doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType, True)
design = des_doc.design
root = design.rootComponent

# 15 参数
pdefs = [
    ('TMP_MotorDia',40.0,'mm','电机占位直径'),('TMP_MotorLen',50.0,'mm','电机长度'),
    ('TMP_Eccentricity',8.0,'mm','偏心距'),('TMP_CrankLen',10.0,'mm','曲柄半径'),
    ('TMP_RodLen',40.0,'mm','连杆长度'),('TMP_Stroke',16.0,'mm','输出行程'),
    ('TMP_GuideLen',60.0,'mm','导向长度'),('TMP_OutputRodDia',8.0,'mm','输出杆直径'),
    ('TMP_TxHeadDia',18.0,'mm','治疗头直径'),('TMP_FrameLen',80.0,'mm','机架长度'),
    ('TMP_FrameWid',50.0,'mm','机架宽度'),('TMP_FrameHt',35.0,'mm','机架高度'),
    ('TMP_ShaftDia',6.0,'mm','驱动轴直径'),('DRV_Speed',3000.0,'rpm','电机转速'),
    ('KIN_Freq',50.0,'Hz','输出频率')]
params = design.userParameters
for nm,val,u,d in pdefs:
    if not params.itemByName(nm): params.add(nm, vi(val), u, d)

# 7 组件
def nc(n):
    o = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    o.component.name = n; return o.component

c_m=nc('DMS-100_Motor'); c_e=nc('DMS-200A_Eccentric')
c_c=nc('DMS-200B_CrankSlider'); c_g=nc('DMS-300_GuideOutput')
c_h=nc('DMS-400_TxHead'); c_f=nc('DMS-500_Frame'); c_s=nc('DMS-600_Housing')

def cyl(co,d,dep,n):
    sk = co.sketches.add(co.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), d/2)
    co.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(dep), adsk.fusion.FeatureOperations.NewBodyFeatureOperation).name = n

def box(co,w,h,d,n):
    sk = co.sketches.add(co.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-w/2,-h/2,0), adsk.core.Point3D.create(w/2,h/2,0))
    co.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(d), adsk.fusion.FeatureOperations.NewBodyFeatureOperation).name = n

box(c_f,80,50,8,'Frame_Bottom'); box(c_s,100,60,70,'HousingShell')
cyl(c_m,40,50,'MotorBody'); cyl(c_m,8,15,'DriveShaft')
cyl(c_e,30,6,'EccentricWheel'); cyl(c_c,16,10,'CrankDisc'); box(c_c,6,40,6,'ConnectingRod')
cyl(c_g,8,60,'OutputRod'); box(c_g,12,12,30,'GuideBush')
cyl(c_h,18,20,'TreatmentHead'); cyl(c_h,6,10,'HeadMount')

bc = sum(cc.bRepBodies.count for cc in design.allComponents)
out.append(f"DOC:{des_doc.name} COMP:{design.allComponents.count-1} BODY:{bc} PARAM:{params.count} JOINT:{root.joints.count}")

# saveAs
try:
    dh = app.data.dataProjects[0].rootFolder
    # 创建 DMS 子文件夹
    sub = dh.dataFolders.createFolder('DMS_Phase2')
    fi = sub.dataFiles.createFile('DMS_Concept_Assembly', des_doc.file.saveAsVersion, des_doc)
    out.append(f"SAVEOK:{fi.name}")
except Exception as se:
    out.append(f"SAVEERR:{str(se)[:80]}")

print("|".join(out))
'''

print("🚀 DMS Concept v5...")
r = c.execute_script(SCRIPT, read_only=False)
msg = r.get('message', str(r)) if isinstance(r, dict) else str(r)
print(f"\n📋 {msg}")
print("\n📸 截图...")
shot = c.take_screenshot()
print(f"   shot: {shot}")
c.disconnect()
