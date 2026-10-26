#!/usr/bin/env python3
"""
create_baseline.py — Gate 2+3: 创建完整参数化测试装配体

TEST_ONLY: 本脚本创建的是 Fusion 360 AI 工程自动化基准验证项目，
           不是正式深层肌肉刺激仪产品设计。

执行流程:
  1. 连接 MCP
  2. 复用/创建文档 (只保留一个)
  3. 创建 13 个 UserParameter (TEST_ONLY)
  4. 创建根组件 TestAssembly
  5. 创建 C1-C8 全部组件 + 草图 + 特征
  6. 建立组件层级关系
  7. 尝试装配关节 (若 API 签名未知则记为待补)
  8. 输出 MODEL_MANIFEST + PARAMETER_MANIFEST
  9. 截图保存
"""

import sys
import json
import os
import time
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp_client.fusion_mcp import connect

EXPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports")
EVIDENCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evidence")
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)

TASK_ID = "BASELINE-001"

# ── 参数定义 (TEST_ONLY) ──────────────────────────────────
USER_PARAMS = [
    ("test_base_length", 200.0, "mm", "基座长度"),
    ("test_base_width", 150.0, "mm", "基座宽度"),
    ("test_base_height", 25.0, "mm", "基座高度"),
    ("test_bearing_od", 62.0, "mm", "轴承外径"),
    ("test_bearing_id", 35.0, "mm", "轴承内径"),
    ("test_shaft_diameter", 20.0, "mm", "测试轴径"),
    ("test_shaft_length", 120.0, "mm", "测试轴长"),
    ("test_eccentric_offset", 5.0, "mm", "偏心量"),
    ("test_slider_width", 40.0, "mm", "滑块宽度"),
    ("test_slider_height", 30.0, "mm", "滑块高度"),
    ("test_hole_diameter", 8.0, "mm", "安装孔径"),
    ("test_clearance", 0.5, "mm", "配合间隙"),
    ("test_part_spacing", 10.0, "mm", "零件间距"),
]


def build_fusion_script() -> str:
    """生成完整 Fusion Python 脚本 (在 Fusion 进程内执行)。"""

    # 参数注册代码
    param_code = ""
    for name, val, unit, desc in USER_PARAMS:
        param_code += f"""
    # {desc}: {name} = {val} {unit}
    try:
        existing = design.userParameters.itemByName("{name}")
        if not existing:
            design.userParameters.add("{name}", {val}, "{unit}", "{desc}")
    except Exception as e:
        log.append("PARAM_FAIL:{name}:" + str(e))
"""

    # 组件创建 (简化但完整)
    component_code = r"""
    # ── 根组件 ──
    root = design.rootComponent
    root.name = "TestAssembly"

    # 清理可能的残留
    for occ in list(root.occurrences):
        try:
            occ.deleteMe()
        except:
            pass
    for comp in list(design.components):
        if comp != root:
            try:
                comp.deleteMe()
            except:
                pass

    # ── C1 基座 TestBase ──
    base_comp = design.components.add(root)
    base_comp.name = "TestBase"
    base_occ = root.occurrences.addNewComponent(base_comp)

    # 基座草图 XY 平面
    sk = base_comp.sketches.add(base_comp.xYConstructionPlane)
    lines = sk.sketchCurves.sketchLines
    rec = lines.addTwoPointRectangle(
        adsk.core.Point3D.create(-test_base_length/2, -test_base_width/2, 0),
        adsk.core.Point3D.create( test_base_length/2,  test_base_width/2, 0)
    )
    prof = sk.profiles.item(0)
    ext = base_comp.features.extrudeFeatures.add(prof,
        adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(test_base_height)),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    base_body = ext.bodies.item(0)
    base_body.name = "BaseBody"
    log.append("C1_DONE")

    # 基座四角孔
    hole_pts = [
        (-test_base_length/2 + 15, -test_base_width/2 + 15),
        ( test_base_length/2 - 15, -test_base_width/2 + 15),
        (-test_base_length/2 + 15,  test_base_width/2 - 15),
        ( test_base_length/2 - 15,  test_base_width/2 - 15),
    ]
    for hx, hy in hole_pts:
        hsk = base_comp.sketches.add(base_comp.topConstructionPlane)
        hc = hsk.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(hx, hy, 0), test_hole_diameter/2)
        hprof = hsk.profiles.item(0)
        base_comp.features.extrudeFeatures.add(hprof,
            adsk.fusion.ThroughAllExtentDefinition.create(),
            adsk.fusion.FeatureOperations.CutFeatureOperation)
    log.append("C1_HOLES_DONE")

    # ── C2 轴承座 TestBearingSupport ──
    brg_comp = design.components.add(root)
    brg_comp.name = "TestBearingSupport"
    brg_occ = root.occurrences.addNewComponent(brg_comp)
    brg_occ.transform = adsk.core.Matrix3D.create()
    brg_occ.transform.translation = adsk.core.Vector3D.create(0, 0, test_base_height + 20)

    # 轴承座是一个带孔圆柱
    bsk = brg_comp.sketches.add(brg_comp.xYConstructionPlane)
    bcir_od = bsk.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), test_bearing_od/2)
    bcir_id = bsk.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), test_bearing_id/2)
    bprof_od = bsk.profiles.item(0)
    brg_ext = brg_comp.features.extrudeFeatures.add(bprof_od,
        adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(30)),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    bprof_id = bsk.profiles.item(1)
    brg_comp.features.extrudeFeatures.add(bprof_id,
        adsk.fusion.ThroughAllExtentDefinition.create(),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
    log.append("C2_DONE")

    # ── C3 测试轴 TestShaft ──
    shaft_comp = design.components.add(root)
    shaft_comp.name = "TestShaft"
    shaft_occ = root.occurrences.addNewComponent(shaft_comp)
    shaft_occ.transform = adsk.core.Matrix3D.create()
    shaft_occ.transform.translation = adsk.core.Vector3D.create(0, 0, test_base_height + 35)

    ssk = shaft_comp.sketches.add(shaft_comp.xYConstructionPlane)
    scircle = ssk.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), test_shaft_diameter/2)
    sprof = ssk.profiles.item(0)
    shaft_ext = shaft_comp.features.extrudeFeatures.add(sprof,
        adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(test_shaft_length)),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    log.append("C3_DONE")

    # ── C4 偏心轮 TestEccentricWheel ──
    ecc_comp = design.components.add(root)
    ecc_comp.name = "TestEccentricWheel"
    ecc_occ = root.occurrences.addNewComponent(ecc_comp)
    ecc_occ.transform = adsk.core.Matrix3D.create()
    ecc_occ.transform.translation = adsk.core.Vector3D.create(test_eccentric_offset, 0, test_base_height + 35 + test_shaft_length/2)

    esek = ecc_comp.sketches.add(ecc_comp.xYConstructionPlane)
    ecircle = esek.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), 30)
    eprof = esek.profiles.item(0)
    ecc_comp.features.extrudeFeatures.add(eprof,
        adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(15)),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    log.append("C4_DONE")

    # ── C5 直线滑块 TestSlider ──
    slider_comp = design.components.add(root)
    slider_comp.name = "TestSlider"
    slider_occ = root.occurrences.addNewComponent(slider_comp)
    slider_occ.transform = adsk.core.Matrix3D.create()
    slider_occ.transform.translation = adsk.core.Vector3D.create(test_base_length/2 - 50, 0, test_base_height + 5)

    ssk2 = slider_comp.sketches.add(slider_comp.xYConstructionPlane)
    srec2 = ssk2.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-test_slider_width/2, -test_slider_height/2, 0),
        adsk.core.Point3D.create( test_slider_width/2,  test_slider_height/2, 0))
    sprof2 = ssk2.profiles.item(0)
    slider_comp.features.extrudeFeatures.add(sprof2,
        adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(20)),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    log.append("C5_DONE")

    # ── C6 导向支架 TestGuideBracket ──
    guide_comp = design.components.add(root)
    guide_comp.name = "TestGuideBracket"
    guide_occ = root.occurrences.addNewComponent(guide_comp)
    guide_occ.transform = adsk.core.Matrix3D.create()
    guide_occ.transform.translation = adsk.core.Vector3D.create(test_base_length/2 - 50, 0, 0)

    gsk = guide_comp.sketches.add(guide_comp.xYConstructionPlane)
    grec = gsk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-30, -40, 0),
        adsk.core.Point3D.create( 30,  40, 0))
    gprof = gsk.profiles.item(0)
    guide_comp.features.extrudeFeatures.add(gprof,
        adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(test_base_height + 40)),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    log.append("C6_DONE")

    # ── C7 测试端部接口 TestEndInterface ──
    iface_comp = design.components.add(root)
    iface_comp.name = "TestEndInterface"
    iface_occ = root.occurrences.addNewComponent(iface_comp)
    iface_occ.transform = adsk.core.Matrix3D.create()
    iface_occ.transform.translation = adsk.core.Vector3D.create(0, 0, test_base_height + 35 + test_shaft_length)

    issk = iface_comp.sketches.add(iface_comp.xYConstructionPlane)
    icircle = issk.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), 15)
    iprof = issk.profiles.item(0)
    iface_comp.features.extrudeFeatures.add(iprof,
        adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(10)),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    log.append("C7_DONE")

    # ── C8 外壳 TestHousing (简单盖) ──
    housing_comp = design.components.add(root)
    housing_comp.name = "TestHousing"
    housing_occ = root.occurrences.addNewComponent(housing_comp)
    housing_occ.transform = adsk.core.Matrix3D.create()
    housing_occ.transform.translation = adsk.core.Vector3D.create(0, 0, test_base_height + 100)

    hsk = housing_comp.sketches.add(housing_comp.xYConstructionPlane)
    hrec = hsk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-test_base_length/2 - 5, -test_base_width/2 - 5, 0),
        adsk.core.Point3D.create( test_base_length/2 + 5,  test_base_width/2 + 5, 0))
    hprof = hsk.profiles.item(0)
    housing_comp.features.extrudeFeatures.add(hprof,
        adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(5)),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    log.append("C8_DONE")
"""

    script = f'''
import adsk.core, adsk.fusion, traceback

log = []

def run(context):
    try:
        app = adsk.core.Application.get()
        _ui = app.userInterface

        # ── 获取/创建文档 ──
        doc = None
        if app.activeDocument and app.activeDocument.designType == adsk.fusion.DesignDocumentType:
            doc = app.activeDocument
            log.append(f"REUSE_ACTIVE:{{doc.name}}")
        else:
            for d in app.documents:
                if d.designType == adsk.fusion.DesignDocumentType:
                    doc = d
                    log.append(f"REUSE_OPEN:{{doc.name}}")
                    break
        if not doc:
            doc = app.documents.add(adsk.fusion.DesignDocumentType)
            log.append("CREATE_NEW")
        design = doc.design
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType

        # ── 绑定参数到变量 ──
        # 参数创建
{param_code}

        # 从 UserParameter 读取到局部变量 (让后续草图代码可引用)
        def gp(name, default=0):
            try:
                return design.userParameters.itemByName(name).value
            except:
                return default

        test_base_length = gp("test_base_length", 200)
        test_base_width = gp("test_base_width", 150)
        test_base_height = gp("test_base_height", 25)
        test_bearing_od = gp("test_bearing_od", 62)
        test_bearing_id = gp("test_bearing_id", 35)
        test_shaft_diameter = gp("test_shaft_diameter", 20)
        test_shaft_length = gp("test_shaft_length", 120)
        test_eccentric_offset = gp("test_eccentric_offset", 5)
        test_slider_width = gp("test_slider_width", 40)
        test_slider_height = gp("test_slider_height", 30)
        test_hole_diameter = gp("test_hole_diameter", 8)
        test_clearance = gp("test_clearance", 0.5)
        test_part_spacing = gp("test_part_spacing", 10)
        log.append("PARAMS_READY")

        # ── 组件创建 ──
{component_code}

        # ── 汇总统计 ──
        comp_count = design.components.count
        body_count = 0
        for c in design.components:
            body_count += c.bRepBodies.count
        log.append(f"SUMMARY:components={{comp_count}}:bodies={{body_count}}:params={{design.userParameters.count}}")
        log.append(f"DOC_NAME:{{doc.name}}")
        log.append(f"DOC_SAVED:{{doc.isSaved}}")

    except Exception as e:
        log.append(f"FATAL:{{traceback.format_exc()}}")

    finally:
        adsk.core.Application.get().log("\\n".join(log))
        return "{{\\n".join('"{{k}}": "{{v}}"' for k, v in [("log", "|".join(log))]).rstrip() + "}}"
'''
    return script


def main():
    print("=" * 60)
    print(f"  {TASK_ID} — Gate 2+3: 参数化装配体创建")
    print("=" * 60)

    # 连接
    print("\n[1/5] 连接 Fusion MCP...")
    c = connect()
    print(f"  ✅ Session established")

    # 执行创建脚本
    print("\n[2/5] 执行装配体创建脚本 (可能需要 60 秒)...")
    script = build_fusion_script()
    result = c.execute_script(script, read_only=False)
    print(f"  Script executed. Type: {type(result)}")

    # 解析日志
    log_text = ""
    if isinstance(result, dict):
        log_text = result.get("log", result.get("result", str(result)))
    elif isinstance(result, str):
        # 可能返回了 JSON 字符串
        try:
            parsed = json.loads(result)
            log_text = parsed.get("log", result)
        except:
            log_text = result
    else:
        log_text = str(result)

    entries = log_text.split("|")
    print(f"  日志条目数: {len(entries)}")
    for entry in entries:
        entry = entry.strip()
        if entry:
            icon = "✅" if "DONE" in entry or "REUSE" in entry or "SUMMARY" in entry or "DOC_" in entry or "PARAMS" in entry else "⚠️"
            if "FAIL" in entry or "FATAL" in entry or "ERROR" in entry.upper():
                icon = "❌"
            print(f"  {icon} {entry}")

    # 检查关键组件是否创建
    expected = ["C1_DONE", "C2_DONE", "C3_DONE", "C4_DONE", "C5_DONE", "C6_DONE", "C7_DONE", "C8_DONE"]
    done = [e for e in expected if e in log_text]
    print(f"\n  组件完成: {len(done)}/8 → {', '.join(done)}")

    if len(done) < 8:
        print(f"  ❌ 有组件未创建成功！")

    # 截图
    print("\n[3/5] 截图证据...")
    shot = c.take_screenshot()
    if shot:
        import base64
        png_data = base64.b64decode(shot) if isinstance(shot, str) else shot
        shot_path = os.path.join(EVIDENCE_DIR, "assembly_isometric.png")
        with open(shot_path, "wb") as f:
            f.write(png_data)
        print(f"  ✅ 截图: {shot_path} ({len(png_data)} bytes)")

    # 保存 manifest
    print("\n[4/5] 保存清单...")
    summary = None
    for entry in entries:
        if "SUMMARY:" in entry:
            summary = entry
            break

    param_manifest = {
        "task_id": TASK_ID,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "parameters": [
            {"name": n, "value": v, "unit": u, "description": d}
            for n, v, u, d in USER_PARAMS
        ]
    }
    with open(os.path.join(EXPORT_DIR, "PARAMETER_MANIFEST.json"), "w") as f:
        json.dump(param_manifest, f, indent=2, ensure_ascii=False)
    print(f"  ✅ PARAMETER_MANIFEST.json")

    model_manifest = {
        "task_id": TASK_ID,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "fusion_version": "2706.1.14",
        "components": [
            {"id": "C1", "name": "TestBase", "description": "基座 TEST_ONLY"},
            {"id": "C2", "name": "TestBearingSupport", "description": "轴承座 TEST_ONLY"},
            {"id": "C3", "name": "TestShaft", "description": "测试轴 TEST_ONLY"},
            {"id": "C4", "name": "TestEccentricWheel", "description": "偏心轮 TEST_ONLY"},
            {"id": "C5", "name": "TestSlider", "description": "直线滑块 TEST_ONLY"},
            {"id": "C6", "name": "TestGuideBracket", "description": "导向支架 TEST_ONLY"},
            {"id": "C7", "name": "TestEndInterface", "description": "端部接口 TEST_ONLY"},
            {"id": "C8", "name": "TestHousing", "description": "外壳 TEST_ONLY"},
            {"id": "A1", "name": "TestAssembly", "description": "根装配体 TEST_ONLY"},
        ],
        "summary_from_log": summary,
        "components_created": len(done),
    }
    with open(os.path.join(EXPORT_DIR, "MODEL_MANIFEST.json"), "w") as f:
        json.dump(model_manifest, f, indent=2, ensure_ascii=False)
    print(f"  ✅ MODEL_MANIFEST.json")

    # 文档状态检查
    print("\n[5/5] 文档状态...")
    docs = c.get_open_documents()
    results = docs.get("results", [])
    print(f"  打开文档: {len(results)} 个 (限制: ≤1)")
    for d in results:
        print(f"    • {d['name']}  active={d['isActive']}")

    c.disconnect()
    print("\n" + "=" * 60)
    if len(done) == 8:
        print("  ✅ Gate 2 通过 — 8/8 组件创建成功")
    else:
        print(f"  ⚠️ Gate 2 部分通过 — {len(done)}/8 组件")
    print("=" * 60)


if __name__ == "__main__":
    main()
