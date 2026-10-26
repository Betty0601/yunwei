#!/usr/bin/env python3
"""
阶段 2：DMS 概念总装创建脚本 v2
修复: 用 print 代替 return, 更好的错误处理

创建内容:
- 7 个组件 (DMS-100~DMS-600)
- 15 个参数化 UserParameters
- 两套候选机构: 偏心 + 曲柄连杆
"""

import sys
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import connect

c = connect()

SCRIPT = '''
import adsk.core, adsk.fusion, traceback

app = adsk.core.Application.get()

def vi(val):
    return adsk.core.ValueInput.createByReal(val)

out = []
def log(msg):
    out.append(str(msg))

try:
    # === 1. 创建新设计文档 ===
    doc = app.activeDocument
    design = None
    
    if doc and 'Concept' in doc.name:
        design = doc.design
        log(f"使用现有文档: {doc.name}")
    else:
        des_doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType, True)
        design = des_doc.design
        doc = des_doc
        log(f"✅ 新建概念设计文档: {doc.name}")
    
    root = design.rootComponent
    root.name = 'DMS-000_TopAssembly'

    # === 2. UserParameters ===
    params = design.userParameters
    
    param_defs = [
        ('TMP_MotorDia',       40.0, 'mm',   '概念电机占位直径'),
        ('TMP_MotorLen',       50.0, 'mm',   '概念电机占位长度'),
        ('TMP_Eccentricity',    8.0, 'mm',   '偏心距 (2×=行程)'),
        ('TMP_CrankLen',       10.0, 'mm',   '曲柄半径'),
        ('TMP_RodLen',         40.0, 'mm',   '连杆长度'),
        ('TMP_Stroke',         16.0, 'mm',   '输出行程 (TMP)'),
        ('TMP_GuideLen',       60.0, 'mm',   '导向杆长度'),
        ('TMP_OutputRodDia',    8.0, 'mm',   '输出杆直径'),
        ('TMP_TxHeadDia',      18.0, 'mm',   '治疗头直径'),
        ('TMP_FrameLen',       80.0, 'mm',   '机架长度'),
        ('TMP_FrameWid',       50.0, 'mm',   '机架宽度'),
        ('TMP_FrameHt',        35.0, 'mm',   '机架高度'),
        ('TMP_ShaftDia',        6.0, 'mm',   '驱动轴直径'),
        ('DRV_Speed',        3000.0, 'rpm',  '概念电机转速 (TBD)'),
        ('KIN_Freq',          50.0, 'Hz',   '输出频率 (TBD)'),
    ]
    
    for name, val, unit, desc in param_defs:
        p = params.itemByName(name)
        if not p:
            params.add(name, vi(val), unit, desc)
    
    log(f"✅ UserParameters: {params.count}")

    # === 3. 创建 7 个组件 ===
    occ = root.occurrences
    
    def new_comp(name):
        c = occ.addNewComponent(adsk.core.Matrix3D.create())
        c.component.name = name
        return c.component
    
    c_motor   = new_comp('DMS-100_Motor')
    c_ecc     = new_comp('DMS-200A_Eccentric')
    c_crank   = new_comp('DMS-200B_CrankSlider')
    c_guide   = new_comp('DMS-300_GuideOutput')
    c_head    = new_comp('DMS-400_TxHead')
    c_frame   = new_comp('DMS-500_Frame')
    c_house   = new_comp('DMS-600_Housing')
    
    log(f"✅ 组件创建: {root.allComponents.count - 1}")

    # === 4. 各组件创建几何 ===
    
    def make_cyl(comp, plane, dia, depth, name):
        pl = comp.xYConstructionPlane if plane == 'XY' else comp.xZConstructionPlane
        sk = comp.sketches.create(pl)
        sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), dia/2)
        f = comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(depth), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        f.name = name
        return f
    
    def make_box(comp, plane, w, h, d, name):
        pl = comp.xYConstructionPlane if plane == 'XY' else comp.xZConstructionPlane
        sk = comp.sketches.create(pl)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-w/2, -h/2, 0),
            adsk.core.Point3D.create(w/2, h/2, 0)
        )
        f = comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), vi(d), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        f.name = name
        return f

    # DMS-500 机架 (先做)
    make_box(c_frame, 'XY', 80, 50, 8, 'Frame_Bottom')
    make_box(c_frame, 'XZ', 8, 30, 50, 'Frame_Back')
    
    # DMS-100 电机
    make_cyl(c_motor, 'XY', 40, 50, 'MotorBody')
    make_cyl(c_motor, 'XY', 8, 15, 'DriveShaft')
    
    # DMS-200A 偏心机构 (圆盘 + 偏心孔)
    make_cyl(c_ecc, 'XY', 30, 6, 'EccentricWheel')
    
    # DMS-200B 曲柄连杆
    make_cyl(c_crank, 'XY', 16, 10, 'CrankDisc')
    make_box(c_crank, 'XY', 6, 40, 6, 'ConnectingRod')
    
    # DMS-300 导向输出
    make_cyl(c_guide, 'XY', 8, 60, 'OutputRod')
    make_box(c_guide, 'XY', 12, 12, 30, 'GuideBush')
    
    # DMS-400 治疗头
    make_cyl(c_head, 'XY', 18, 20, 'TreatmentHead')
    make_cyl(c_head, 'XY', 6, 10, 'HeadMount')
    
    # DMS-600 外壳包络
    make_box(c_house, 'XY', 100, 60, 70, 'HousingShell')
    
    # 统计
    total_bodies = sum(comp.bRepBodies.count for comp in root.allComponents)
    log(f"✅ 几何创建完成! 总组件: {root.allComponents.count - 1}, 实体体: {total_bodies}")
    log(f"   组件: Motor/Eccentric/Crank/Guide/TxHead/Frame/Housing")
    log(f"   参数: {params.count} 个 (TMP_临时 + DRV_驱动 + KIN_运动学)")
    
    # 保存
    doc.save()
    log(f"✅ 文档已保存: {doc.name}")
    
    # 最终统计
    all_comps = root.allComponents
    bodies = sum(c.bRepBodies.count for c in all_comps)
    joints = root.joints.count
    
    log(f"📊 FINAL: {all_comps.count - 1} components, {params.count} params, {bodies} bodies, {joints} joints")

except Exception as e:
    log(f"❌ ERROR: {traceback.format_exc()}")

# 输出所有日志
result = "|".join(out)
print(result)
'''

print("🚀 执行 Fusion 概念总装创建...")
result = c.execute_script(SCRIPT, read_only=False)
msg = result.get('message', str(result)) if isinstance(result, dict) else str(result)
print(f"\n📋 Fusion 返回:\n{msg[:2000]}")

print("\n📸 截图...")
shot = c.take_screenshot()
print(f"   截图结果: {shot}")

c.disconnect()
print("\n✅ DMS 概念总装创建完成!")
