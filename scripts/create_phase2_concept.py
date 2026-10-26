#!/usr/bin/env python3
"""
阶段 2：DMS 概念总装创建脚本
创建偏心机构 + 曲柄连杆两套候选架构的参数化概念模型

Fusion 2026+ API 适配:
  - UserParameters.add(name, ValueInput.createByReal(val), units, comment)
  - addNewComponent(Matrix3D)
  - ExtrudeFeatures.addSimple(profile, ValueInput, op)
  - JointGeometry.createByCurve(edge, CenterKeyPoint)
"""

import sys
sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import connect

c = connect()

# === 脚本代码 (发送到 Fusion 执行) ===
SCRIPT = r'''
import adsk.core, adsk.fusion, adsk.cam, traceback

app = adsk.core.Application.get()
ui = app.userInterface

def vi(val):
    return adsk.core.ValueInput.createByReal(val)

def log(msg):
    print(f"[DMS-P2] {msg}")

try:
    # === 1. 检查/创建文档 ===
    doc = app.activeDocument
    if doc and 'Concept' in doc.name:
        design = doc.design
        log(f"使用现有文档: {doc.name}")
    else:
        # 新建概念设计
        des = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType, True)
        design = des.design
        doc = des
        log(f"新建概念设计文档: {doc.name}")

    root = design.rootComponent
    units = design.unitsManager
    
    # 清理默认组件命名
    root.name = 'DMS-000_TopAssembly'

    # === 2. 创建 UserParameters ===
    params = design.userParameters
    log("创建参数...")
    
    # 临时概念参数 (TMP_ 前缀, 后续阶段需冻结)
    p_list = [
        ('TMP_MotorDia',       40.0, 'mm',   '概念电机占位直径'),
        ('TMP_MotorLen',       50.0, 'mm',   '概念电机占位长度'),
        ('TMP_Eccentricity',    8.0, 'mm',   '偏心距 (2×=行程)'),
        ('TMP_CrankLen',       10.0, 'mm',   '曲柄半径'),
        ('TMP_RodLen',         40.0, 'mm',   '连杆长度'),
        ('TMP_Stroke',         16.0, 'mm',   '输出行程 (=2×偏心距)'),
        ('TMP_GuideLen',       60.0, 'mm',   '导向杆长度'),
        ('TMP_OutputRodDia',    8.0, 'mm',   '输出杆直径'),
        ('TMP_TxHeadDia',      18.0, 'mm',   '治疗头直径'),
        ('TMP_FrameLen',       80.0, 'mm',   '机架长度'),
        ('TMP_FrameWid',       50.0, 'mm',   '机架宽度'),
        ('TMP_FrameHt',        35.0, 'mm',   '机架高度'),
        ('TMP_ShaftDia',        6.0, 'mm',   '驱动轴直径'),
        ('DRV_Speed',        3000.0, 'rpm',  '概念电机转速 (TBD)'),
        ('KIN_Freq',          50.0, 'Hz',   '输出频率 = DRV_Speed/60'),
    ]
    
    for name, val, unit, desc in p_list:
        if not params.itemByName(name):
            params.add(name, vi(val), unit, desc)
    
    log(f"参数总数: {params.count}")

    # === 3. 创建组件树 ===
    def new_comp(parent, name):
        comp = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp.component.name = name
        return comp
    
    log("创建组件树...")
    
    # 顶层组件
    occ_root = root.occurrences
    comp_motor    = new_comp(root, 'DMS-100_Motor')
    comp_ecc      = new_comp(root, 'DMS-200A_Eccentric')
    comp_crank    = new_comp(root, 'DMS-200B_CrankSlider')  
    comp_guide    = new_comp(root, 'DMS-300_GuideAndOutput')
    comp_head     = new_comp(root, 'DMS-400_TxHead')
    comp_frame    = new_comp(root, 'DMS-500_Frame')
    comp_housing  = new_comp(root, 'DMS-600_Housing')
    
    log(f"组件数: {root.allComponents.count - 1}")

    # === 4. 在组件里创建几何 ===
    def extrude_circle(comp, plane_name, dia, depth, name, op='NewBodyFeatureOperation'):
        """在指定组件的指定平面上画圆然后拉伸"""
        planes = comp.component.constructionPlanes
        sketches = comp.component.sketches
        feats = comp.component.features
        
        # 找或建平面
        plane = None
        if plane_name == 'XY':
            plane = comp.component.xYConstructionPlane
        elif plane_name == 'XZ':
            plane = comp.component.xZConstructionPlane
        elif plane_name == 'YZ':
            plane = comp.component.yZConstructionPlane
        
        sk = sketches.create(plane)
        circles = sk.sketchCurves.sketchCircles
        cc = circles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0),
            dia / 2
        )
        
        extrudes = feats.extrudeFeatures
        prof = sk.profiles.item(0)
        extDef = adsk.fusion.DistanceExtentDefinition.create(vi(depth))
        op_enum = adsk.fusion.FeatureOperations.CutFeatureOperation if op == 'Cut' else adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        
        feat = extrudes.addSimple(prof, vi(depth), op_enum)
        feat.name = name
        return feat
    
    def extrude_rect(comp, plane_name, w, h, depth, name, op='NewBodyFeatureOperation'):
        planes = comp.component.constructionPlanes
        sketches = comp.component.sketches
        feats = comp.component.features
        
        if plane_name == 'XY':
            plane = comp.component.xYConstructionPlane
        elif plane_name == 'XZ':
            plane = comp.component.xZConstructionPlane
        
        sk = sketches.create(plane)
        lines = sk.sketchCurves.sketchLines
        ll = lines.addTwoPointRectangle(
            adsk.core.Point3D.create(-w/2, -h/2, 0),
            adsk.core.Point3D.create(w/2, h/2, 0)
        )
        
        extrudes = feats.extrudeFeatures
        prof = sk.profiles.item(0)
        op_enum = adsk.fusion.FeatureOperations.CutFeatureOperation if op == 'Cut' else adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        feat = extrudes.addSimple(prof, vi(depth), op_enum)
        feat.name = name
        return feat

    # --- DMS-500 机架 (先做，作为基准) ---
    log("创建机架 DMS-500...")
    c5 = comp_frame.component
    f_bottom = extrude_rect(c5, 'XY', 80, 50, 8, 'Frame_Bottom')
    # 立板
    sk2 = c5.sketches.create(c5.xZConstructionPlane)
    l2 = sk2.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-25, 0, 0),
        adsk.core.Point3D.create(25, 30, 42)
    )
    fe = c5.features.extrudeFeatures
    prof = sk2.profiles.item(0)
    f_back = fe.addSimple(prof, vi(8), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    f_back.name = 'Frame_BackPlate'

    # --- DMS-100 电机占位 ---
    log("创建电机占位 DMS-100...")
    c1 = comp_motor.component
    f_motor = extrude_circle(c1, 'XY', 40, 50, 'MotorBody')

    # --- DMS-200A 偏心机构 ---
    log("创建偏心机构 DMS-200A...")
    c2a = comp_ecc.component
    # 偏心轮 (圆盘 + 偏心孔)
    sk_e = c2a.sketches.create(c2a.xYConstructionPlane)
    c_e = sk_e.sketchCurves.sketchCircles
    c_e.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 15)      # 外圆
    c_e.addByCenterRadius(adsk.core.Point3D.create(8, 0, 0), 4)        # 偏心孔
    fe_e = c2a.features.extrudeFeatures
    # 先拉外圆
    prof_outer = None
    for p in sk_e.profiles:
        if p.boundingBox.maxPoint.distanceTo(adsk.core.Point3D.create(0,0,0)) > 10:
            prof_outer = p
            break
    if not prof_outer:
        prof_outer = sk_e.profiles.item(0)
    f_ecc = fe_e.addSimple(prof_outer, vi(6), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    f_ecc.name = 'EccentricWheel'

    # --- DMS-200B 曲柄连杆 (用简单 box 表示曲柄 + 连杆) ---
    log("创建曲柄连杆 DMS-200B...")
    c2b = comp_crank.component
    # 曲柄 (短圆柱)
    f_crank = extrude_circle(c2b, 'XY', 8, 12, 'CrankDisc')
    # 连杆 (box)
    f_rod = extrude_rect(c2b, 'XY', 6, 40, 6, 'ConnectingRod')

    # --- DMS-300 导向与输出 ---
    log("创建导向与输出 DMS-300...")
    c3 = comp_guide.component
    f_rod = extrude_circle(c3, 'XY', 8, 60, 'OutputRod')
    f_guide = extrude_rect(c3, 'XY', 10, 10, 30, 'GuideBlock')

    # --- DMS-400 治疗头 ---
    log("创建治疗头 DMS-400...")
    c4 = comp_head.component
    f_tx = extrude_circle(c4, 'XY', 18, 20, 'TxHead')
    f_tx.name = 'TreatmentHead'

    # --- DMS-600 外壳包络 (概念 box) ---
    log("创建外壳包络 DMS-600...")
    c6 = comp_housing.component
    f_house = extrude_rect(c6, 'XY', 100, 60, 70, 'HousingShell')

    log(f"所有组件创建完成! 总组件: {root.allComponents.count - 1}")
    log(f"UserParameters: {params.count}")
    
    # 返回统计
    return f"DMS Concept Created: {root.allComponents.count - 1} comps, {params.count} params"

except Exception as e:
    log(f"ERROR: {str(e)}")
    return f"ERROR: {str(e)}"
'''

result = c.execute_script(SCRIPT, read_only=False)
print("=== Fusion 执行结果 ===")
if isinstance(result, dict):
    print(result.get('message', str(result))[:500])
else:
    print(str(result)[:500])

# 截图
print("\n=== 截图 ===")
shot = c.take_screenshot()
print(f"截图: {shot}")

c.disconnect()
print("\n✅ 概念总装创建完成!")
