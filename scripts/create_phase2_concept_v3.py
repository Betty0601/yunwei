#!/usr/bin/env python3
"""
阶段 2：DMS 概念总装 v3 — 修复 root.name + 变量名冲突
"""
import sys
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import connect

c = connect()

SCRIPT = '''
import adsk.core, adsk.fusion, traceback

_fusion_app = adsk.core.Application.get()

def vi(v):
    return adsk.core.ValueInput.createByReal(v)

_log = []
def log_msg(m):
    _log.append(str(m))

try:
    # 新建设计文档 (Fusion 允许一个 untitled)
    _des = _fusion_app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType, True)
    _design = _des.design
    _doc = _des
    log_msg(f"✅ 新建设计: {_doc.name}")
    
    root = _design.rootComponent

    # === UserParameters ===
    params = _design.userParameters
    param_defs = [
        ('TMP_MotorDia',      40.0, 'mm',  '概念电机占位直径'),
        ('TMP_MotorLen',      50.0, 'mm',  '概念电机占位长度'),
        ('TMP_Eccentricity',   8.0, 'mm',  '偏心距'),
        ('TMP_CrankLen',      10.0, 'mm',  '曲柄半径'),
        ('TMP_RodLen',        40.0, 'mm',  '连杆长度'),
        ('TMP_Stroke',        16.0, 'mm',  '输出行程 (2×偏心距)'),
        ('TMP_GuideLen',      60.0, 'mm',  '导向长度'),
        ('TMP_OutputRodDia',   8.0, 'mm',  '输出杆直径'),
        ('TMP_TxHeadDia',     18.0, 'mm',  '治疗头直径'),
        ('TMP_FrameLen',      80.0, 'mm',  '机架长度'),
        ('TMP_FrameWid',      50.0, 'mm',  '机架宽度'),
        ('TMP_FrameHt',       35.0, 'mm',  '机架高度'),
        ('TMP_ShaftDia',       6.0, 'mm',  '驱动轴直径'),
        ('DRV_Speed',       3000.0, 'rpm', '概念电机转速'),
        ('KIN_Freq',          50.0, 'Hz',  '输出频率'),
    ]
    for nm, val, u, d in param_defs:
        if not params.itemByName(nm):
            params.add(nm, vi(val), u, d)
    log_msg(f"✅ UserParameters: {params.count}")

    # === 创建 7 个组件 ===
    def new_comp(name):
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = name
        return occ.component
    
    c_motor  = new_comp('DMS-100_Motor')
    c_ecc    = new_comp('DMS-200A_Eccentric')
    c_crank  = new_comp('DMS-200B_CrankSlider')
    c_guide  = new_comp('DMS-300_GuideOutput')
    c_head   = new_comp('DMS-400_TxHead')
    c_frame  = new_comp('DMS-500_Frame')
    c_house  = new_comp('DMS-600_Housing')
    log_msg(f"✅ 组件创建: {root.allComponents.count - 1}")

    # === 创建几何 ===
    def make_cyl(comp, dia, depth, name):
        sk = comp.sketches.create(comp.xYConstructionPlane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), dia/2)
        f = comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(depth), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        f.name = name
        return f
    
    def make_box(comp, w, h, d, name):
        sk = comp.sketches.create(comp.xYConstructionPlane)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-w/2, -h/2, 0),
            adsk.core.Point3D.create(w/2, h/2, 0))
        f = comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(d), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        f.name = name
        return f

    # 6 个组件各创建几何
    make_box(c_frame,  80, 50, 8, 'Frame_Bottom')
    make_cyl(c_motor,  40, 50, 'MotorBody')
    make_cyl(c_motor,   8, 15, 'DriveShaft')
    make_cyl(c_ecc,    30,  6, 'EccentricWheel')
    make_cyl(c_crank,  16, 10, 'CrankDisc')
    make_box(c_crank,   6, 40, 6, 'ConnectingRod')
    make_cyl(c_guide,   8, 60, 'OutputRod')
    make_box(c_guide,  12, 12, 30, 'GuideBush')
    make_cyl(c_head,   18, 20, 'TreatmentHead')
    make_cyl(c_head,    6, 10, 'HeadMount')
    make_box(c_house, 100, 60, 70, 'HousingShell')
    
    total_bodies = sum(cc.bRepBodies.count for cc in root.allComponents)
    log_msg(f"✅ 几何完成! 组件:{root.allComponents.count - 1} 实体:{total_bodies} 参数:{params.count}")

    _doc.save()
    log_msg(f"✅ 已保存: {_doc.name}")
    
except Exception as e:
    log_msg(f"❌ {traceback.format_exc()}")

print("|".join(_log))
'''

print("🚀 执行 DMS Concept Assembly v3...")
result = c.execute_script(SCRIPT, read_only=False)
msg = result.get('message', str(result)) if isinstance(result, dict) else str(result)
print(f"\n📋 返回:\n{msg[:3000]}")

print("\n📸 截图...")
shot = c.take_screenshot()
print(f"   {shot}")

c.disconnect()
