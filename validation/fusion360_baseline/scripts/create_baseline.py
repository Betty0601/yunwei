#!/usr/bin/env python3
"""
create_baseline.py — 基准项目完整创建脚本

BASELINE-001 — Fusion 360 AI 工程自动化基准验证项目

创建内容:
  13 个 UserParameter (全 TEST_ONLY)
   8 个组件: TestBase / TestBearingSupport / TestShaft / TestEccentricWheel
             / TestSlider / TestGuideBracket / TestEndInterface / TestHousing
   1 个根组件: TestAssembly

Fusion 2026+ API 关键适配:
  - UserParameters.add(name, ValueInput.createByReal(val), units, comment)
  - Occurrences.addNewComponent(Matrix3D)
  - ExtrudeFeatures.addSimple(profile, ValueInput.createByReal(dist), operation)
  - design.allComponents (不是 design.components)
  - app.data.dataHubs[0].dataProjects (不是 app.data.activeProject)

运行方式:
  PYTHONPATH=. python3 validation/fusion360_baseline/scripts/create_baseline.py
"""

import sys
import json
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.mcp_client.fusion_mcp import connect

TASK_ID = "BASELINE-001"
EXPORT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "exports")
)
os.makedirs(EXPORT_DIR, exist_ok=True)

USER_PARAMS = [
    ("test_base_length", 200.0, "mm", "基座长度 TEST_ONLY"),
    ("test_base_width", 150.0, "mm", "基座宽度 TEST_ONLY"),
    ("test_base_height", 25.0, "mm", "基座高度 TEST_ONLY"),
    ("test_bearing_od", 62.0, "mm", "轴承外径 TEST_ONLY"),
    ("test_bearing_id", 35.0, "mm", "轴承内径 TEST_ONLY"),
    ("test_shaft_diameter", 20.0, "mm", "测试轴径 TEST_ONLY"),
    ("test_shaft_length", 120.0, "mm", "测试轴长 TEST_ONLY"),
    ("test_eccentric_offset", 5.0, "mm", "偏心量 TEST_ONLY"),
    ("test_slider_width", 40.0, "mm", "滑块宽度 TEST_ONLY"),
    ("test_slider_height", 30.0, "mm", "滑块高度 TEST_ONLY"),
    ("test_hole_diameter", 8.0, "mm", "安装孔径 TEST_ONLY"),
    ("test_clearance", 0.5, "mm", "配合间隙 TEST_ONLY"),
    ("test_part_spacing", 10.0, "mm", "零件间距 TEST_ONLY"),
]


def FUSION_SCRIPT():
    """返回 Fusion 进程内执行的完整 Python 脚本字符串。"""

    # 注意: 此字符串在 Fusion 内运行，使用 adsk.* API
    # Python 字符串中的 { } 需要用 {{{{ }}}} 表示字面量
    return '''
import adsk.core, adsk.fusion, traceback

log = []

def run(context):
    try:
        app = adsk.core.Application.get()
        doc = app.activeDocument
        design = doc.design

        # 1. 创建 UserParameter (Fusion 2026+: 必须用 ValueInput)
        for name, val, unit, desc in [
            ("test_base_length", 200.0, "mm", "基座长度 TEST_ONLY"),
            ("test_base_width", 150.0, "mm", "基座宽度 TEST_ONLY"),
            ("test_base_height", 25.0, "mm", "基座高度 TEST_ONLY"),
            ("test_bearing_od", 62.0, "mm", "轴承外径 TEST_ONLY"),
            ("test_bearing_id", 35.0, "mm", "轴承内径 TEST_ONLY"),
            ("test_shaft_diameter", 20.0, "mm", "测试轴径 TEST_ONLY"),
            ("test_shaft_length", 120.0, "mm", "测试轴长 TEST_ONLY"),
            ("test_eccentric_offset", 5.0, "mm", "偏心量 TEST_ONLY"),
            ("test_slider_width", 40.0, "mm", "滑块宽度 TEST_ONLY"),
            ("test_slider_height", 30.0, "mm", "滑块高度 TEST_ONLY"),
            ("test_hole_diameter", 8.0, "mm", "安装孔径 TEST_ONLY"),
            ("test_clearance", 0.5, "mm", "配合间隙 TEST_ONLY"),
            ("test_part_spacing", 10.0, "mm", "零件间距 TEST_ONLY"),
        ]:
            try:
                if not design.userParameters.itemByName(name):
                    vi = adsk.core.ValueInput.createByReal(val)
                    design.userParameters.add(name, vi, unit, desc)
            except Exception as e:
                log.append("PARAM_FAIL:" + str(e))
        log.append("PARAMS_OK:" + str(design.userParameters.count))

        def gp(n, d=0):
            try: return design.userParameters.itemByName(n).value
            except: return d

        TBL, TBW, TBH = gp("test_base_length", 200), gp("test_base_width", 150), gp("test_base_height", 25)
        BOD, BID = gp("test_bearing_od", 62), gp("test_bearing_id", 35)
        SD, SL = gp("test_shaft_diameter", 20), gp("test_shaft_length", 120)
        EO = gp("test_eccentric_offset", 5)
        SW, SH = gp("test_slider_width", 40), gp("test_slider_height", 30)
        log.append("GP_OK")

        root = design.rootComponent

        # 清理已有 occurrences
        for occ in list(root.occurrences):
            try: occ.deleteMe()
            except: pass
        log.append("CLEAN_OK")

        def new_comp(parent, name, tx=None):
            m = adsk.core.Matrix3D.create()
            if tx:
                m.translation = adsk.core.Vector3D.create(float(tx[0]), float(tx[1]), float(tx[2]))
            occ = parent.occurrences.addNewComponent(m)
            comp = occ.component
            comp.name = name
            return comp, occ

        def ext_solid(comp, profile, dist_mm):
            return comp.features.extrudeFeatures.addSimple(
                profile,
                adsk.core.ValueInput.createByReal(dist_mm),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # C1 基座
        c1, o1 = new_comp(root, "TestBase")
        sk = c1.sketches.add(c1.xYConstructionPlane)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-TBL/2, -TBW/2, 0),
            adsk.core.Point3D.create( TBL/2,  TBW/2, 0))
        ext_solid(c1, sk.profiles.item(0), TBH)
        log.append("C1_OK")

        # C2 轴承座
        c2, o2 = new_comp(root, "TestBearingSupport", (0, 0, TBH + 20))
        bsk = c2.sketches.add(c2.xYConstructionPlane)
        bsk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), BOD/2)
        ext_solid(c2, bsk.profiles.item(0), 30)
        log.append("C2_OK")

        # C3 测试轴
        c3, o3 = new_comp(root, "TestShaft", (0, 0, TBH + 35))
        ssk = c3.sketches.add(c3.xYConstructionPlane)
        ssk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), SD/2)
        ext_solid(c3, ssk.profiles.item(0), SL)
        log.append("C3_OK")

        # C4 偏心轮
        c4, o4 = new_comp(root, "TestEccentricWheel", (EO, 0, TBH + 35 + SL/2))
        esk = c4.sketches.add(c4.xYConstructionPlane)
        esk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), 30)
        ext_solid(c4, esk.profiles.item(0), 15)
        log.append("C4_OK")

        # C5 滑块
        c5, o5 = new_comp(root, "TestSlider", (TBL/2 - 50, 0, TBH + 5))
        sk5 = c5.sketches.add(c5.xYConstructionPlane)
        sk5.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-SW/2, -SH/2, 0),
            adsk.core.Point3D.create( SW/2,  SH/2, 0))
        ext_solid(c5, sk5.profiles.item(0), 20)
        log.append("C5_OK")

        # C6 导向支架
        c6, o6 = new_comp(root, "TestGuideBracket", (TBL/2 - 50, 0, 0))
        sk6 = c6.sketches.add(c6.xYConstructionPlane)
        sk6.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-30, -40, 0),
            adsk.core.Point3D.create( 30,  40, 0))
        ext_solid(c6, sk6.profiles.item(0), TBH + 40)
        log.append("C6_OK")

        # C7 端部接口
        c7, o7 = new_comp(root, "TestEndInterface", (0, 0, TBH + 35 + SL))
        sk7 = c7.sketches.add(c7.xYConstructionPlane)
        sk7.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), 15)
        ext_solid(c7, sk7.profiles.item(0), 10)
        log.append("C7_OK")

        # C8 外壳
        c8, o8 = new_comp(root, "TestHousing", (0, 0, TBH + 100))
        sk8 = c8.sketches.add(c8.xYConstructionPlane)
        sk8.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-TBL/2 - 5, -TBW/2 - 5, 0),
            adsk.core.Point3D.create( TBL/2 + 5,  TBW/2 + 5, 0))
        ext_solid(c8, sk8.profiles.item(0), 5)
        log.append("C8_OK")

        cc = design.allComponents.count
        bc = sum(c.bRepBodies.count for c in design.allComponents)
        oc = root.occurrences.count
        log.append("SUMMARY:comps=" + str(cc) + ":occ=" + str(oc) + ":bodies=" + str(bc))
        log.append("DOC=" + doc.name)
        log.append("DOC_SAVED=" + str(doc.isSaved))

    except Exception as e:
        log.append("FATAL:" + traceback.format_exc())

    return "|".join(log)

print(run(None))
'''


def main():
    print("=" * 60)
    print(f"  {TASK_ID} — Gate 2: 8 组件参数化装配体创建")
    print("=" * 60)

    print("\n[1/4] 连接 Fusion MCP...")
    c = connect()
    print("  ✅ Session established")

    print("\n[2/4] 执行创建脚本...")
    result = c.execute_script(FUSION_SCRIPT(), read_only=False)

    msg = result.get("message", str(result)) if isinstance(result, dict) else str(result)
    entries = msg.split("|")

    comps_done = 0
    for e in entries:
        e = e.strip()
        if not e:
            continue
        icon = "✅" if "_OK" in e or "SUMMARY" in e or "DOC_" in e else "❌"
        if "FATAL" in e:
            icon = "❌"
        if "C" in e.split("_")[0] and "_OK" in e:
            comps_done += 1
        print(f"  {icon} {e}")

    expected = ["C1_OK", "C2_OK", "C3_OK", "C4_OK", "C5_OK", "C6_OK", "C7_OK", "C8_OK"]
    actual = [e for e in expected if e + "_OK" not in msg and e in msg]
    success = sum(1 for ex in expected if ex in msg)

    print(f"\n  组件创建: {success}/8")

    # 保存 manifest
    print("\n[3/4] 保存清单...")
    param_mf = {
        "task_id": TASK_ID,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "parameters": [
            {"name": n, "value": v, "unit": u, "description": d, "category": "TEST_ONLY"}
            for n, v, u, d in USER_PARAMS
        ],
    }
    with open(os.path.join(EXPORT_DIR, "PARAMETER_MANIFEST.json"), "w") as f:
        json.dump(param_mf, f, indent=2, ensure_ascii=False)

    model_mf = {
        "task_id": TASK_ID,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "fusion_version": "2706.1.14",
        "fusion2026_api_adaptations": [
            "UserParameters.add uses ValueInput.createByReal",
            "Occurrences.addNewComponent uses Matrix3D only",
            "ExtrudeFeatures.addSimple replaces old 3-arg add",
            "design.allComponents replaces design.components",
            "DataHub.dataProjects replaces activeProject",
        ],
        "components": [
            {"id": "C1", "name": "TestBase", "tx": "0,0,0", "category": "TEST_ONLY"},
            {"id": "C2", "name": "TestBearingSupport", "tx": "0,0,45", "category": "TEST_ONLY"},
            {"id": "C3", "name": "TestShaft", "tx": "0,0,60", "category": "TEST_ONLY"},
            {"id": "C4", "name": "TestEccentricWheel", "tx": "5,0,120", "category": "TEST_ONLY"},
            {"id": "C5", "name": "TestSlider", "tx": "50,0,30", "category": "TEST_ONLY"},
            {"id": "C6", "name": "TestGuideBracket", "tx": "50,0,0", "category": "TEST_ONLY"},
            {"id": "C7", "name": "TestEndInterface", "tx": "0,0,195", "category": "TEST_ONLY"},
            {"id": "C8", "name": "TestHousing", "tx": "0,0,125", "category": "TEST_ONLY"},
        ],
    }
    with open(os.path.join(EXPORT_DIR, "MODEL_MANIFEST.json"), "w") as f:
        json.dump(model_mf, f, indent=2, ensure_ascii=False)

    print(f"  ✅ PARAMETER_MANIFEST.json")
    print(f"  ✅ MODEL_MANIFEST.json")

    print("\n[4/4] 文档状态...")
    docs = c.get_open_documents()
    for d in docs.get("results", []):
        print(f"  • {d['name']}  saved={d.get('isSaved','?')}")

    c.disconnect()
    print("\n" + "=" * 60)
    if success == 8:
        print("  ✅ Gate 2 通过 — 8/8 组件")
    else:
        print(f"  ⚠️ Gate 2 部分通过 — {success}/8")
    print("=" * 60)


if __name__ == "__main__":
    main()
