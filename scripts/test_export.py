#!/usr/bin/env python3
"""
Fusion 360 STEP/STL 导出 + Document Save 真实验证 (最终版)

完整链路: 复用已有/创建新 Fusion 设计 → 创建立方体 → 导出 STEP → 导出 STL → 验证文件存在 → 报告结果

已验证:
  ✅ STEP 导出 (ASCII ISO-10303-21, ~24KB for 20³ cube)
  ✅ STL 导出 (Binary STLB, 684B for 20³ cube)
  ⚠️ Document.saveAs 需要 Fusion Team DataFolder 权限
  ⚠️ DOC_IS_SAVED=False 正常（首次 saveAs 需云端）

2026 Fusion API 兼容性:
  - DistanceExtentDefinition.create(dist) 替代旧 ValueInput 直接传
  - ThroughAllExtentDefinition.create() 替代 AllExtentDefinition
  - MeshRefinementMedium 替代 MeshRefinementMediumSided
  - createSTLExportOptions(body, filename) 参数顺序: body 在前
  - Component.meshBodies 是集合属性（空）；从 feature.bodies 取 body

用法: python3 scripts/test_export.py
"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.mcp_client.fusion_mcp import connect

MODEL_DIR = "/Users/betty/Documents/trae_projects/yunwei/models"

EXPORT_SCRIPT = f"""
import adsk.core, adsk.fusion, traceback, os, json

def run(context):
    ui = None
    results = {{}}
    try:
        app = adsk.core.Application.get()

        # 1) 找到 Fusion 设计文档 (复用已有避免多余 Untitled)
        design_doc = None
        for i in range(app.documents.count):
            d = app.documents.item(i)
            for j in range(d.products.count):
                if adsk.fusion.Design.cast(d.products.item(j)):
                    design_doc = d
                    break
            if design_doc:
                break
        if not design_doc:
            design_doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        if design_doc != app.activeDocument:
            design_doc.activate()

        product = design_doc.products.item(0)
        design = adsk.fusion.Design.cast(product)
        root = design.rootComponent
        results['doc_name'] = design_doc.name

        # 2) 找到或创建几何体 (从 feature.bodies 获取)
        body = None
        if root.features.extrudeFeatures.count > 0:
            for idx in range(root.features.extrudeFeatures.count):
                ef = root.features.extrudeFeatures.item(idx)
                if ef.bodies.count > 0:
                    body = ef.bodies.item(0)
                    results['reused'] = True
                    break

        if not body:
            sketch = root.sketches.add(root.xYConstructionPlane)
            sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(0, 0, 0),
                adsk.core.Point3D.create(20, 20, 0))
            extInput = root.features.extrudeFeatures.createInput(
                sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            dist = adsk.core.ValueInput.createByReal(20)
            extInput.setOneSideExtent(
                adsk.fusion.DistanceExtentDefinition.create(dist),
                adsk.fusion.ExtentDirections.PositiveExtentDirection)
            cube = root.features.extrudeFeatures.add(extInput)
            body = cube.bodies.item(0)
            results['reused'] = False

        results['body_name'] = body.name
        results['body_volume'] = round(body.volume, 4)

        # 3) 导出 STEP (ASCII ISO-10303-21)
        os.makedirs('{MODEL_DIR}', exist_ok=True)
        step_path = os.path.join('{MODEL_DIR}', 'test_cube.step')
        exportMgr = design.exportManager
        stepOpts = exportMgr.createSTEPExportOptions(step_path, root)
        results['step_ok'] = exportMgr.execute(stepOpts)
        results['step_path'] = step_path
        results['step_exists'] = os.path.exists(step_path)
        results['step_size'] = os.path.getsize(step_path) if os.path.exists(step_path) else 0

        # 4) 导出 STL (Binary STLB)
        stl_path = os.path.join('{MODEL_DIR}', 'test_cube.stl')
        stlOpts = exportMgr.createSTLExportOptions(body, stl_path)
        stlOpts.sendToPrintUtility = False
        stlOpts.refinement = adsk.fusion.MeshRefinementSettings.MeshRefinementMedium
        results['stl_ok'] = exportMgr.execute(stlOpts)
        results['stl_path'] = stl_path
        results['stl_exists'] = os.path.exists(stl_path)
        results['stl_size'] = os.path.getsize(stl_path) if os.path.exists(stl_path) else 0

        # 5) Document save 状态
        results['doc_is_saved'] = design_doc.isSaved

        print('EXPORT_RESULT=' + json.dumps(results))

    except:
        print('EXPORT_ERROR=' + traceback.format_exc())

run(None)
"""


def main():
    print("=" * 60)
    print("🔬 Fusion 360 STEP/STL 导出 + Document Save 验证")
    print("=" * 60)

    print("\n[1/4] 连接 Fusion MCP...")
    try:
        c = connect()
        print(f"    ✅ OK (session: {c.session_id[:8]}...)")
    except Exception as e:
        print(f"    ❌ 连接失败: {e}")
        return 1

    print("\n[2/4] 执行创建+导出脚本...")
    try:
        result = c.execute_script(EXPORT_SCRIPT)
        raw = result.get("message", str(result)) if isinstance(result, dict) else str(result)
    except Exception as e:
        print(f"    ❌ 脚本执行失败: {e}")
        c.disconnect()
        return 1

    print("\n[3/4] 解析结果...")
    export_json = None
    for line in raw.splitlines():
        if line.startswith("EXPORT_RESULT="):
            try:
                export_json = json.loads(line[len("EXPORT_RESULT="):])
            except Exception:
                pass
        elif line.startswith("EXPORT_ERROR="):
            print(f"    ❌ Fusion 内部错误: {line[13:]}")
            c.disconnect()
            return 1

    if not export_json:
        print(f"    ❌ 未找到 EXPORT_RESULT")
        print(f"    Raw: {raw[:500]}")
        c.disconnect()
        return 1

    r = export_json
    print("\n[4/4] 验证结果")
    print("-" * 60)
    print(f"  文档:         {r.get('doc_name')}")
    print(f"  复用已有体:   {'是' if r.get('reused') else '否 (新创建)'}")
    print(f"  几何体:       {r.get('body_name')} (volume={r.get('body_volume')} cm³)")
    print(f"  STEP 导出:    {'✅ OK' if r.get('step_ok') else '❌ 失败'}")
    print(f"    路径:       {r.get('step_path')}")
    print(f"    文件:       {'✅ 存在' if r.get('step_exists') else '❌ 不存在'} ({r.get('step_size')} bytes)")
    print(f"  STL 导出:     {'✅ OK' if r.get('stl_ok') else '❌ 失败'}")
    print(f"    路径:       {r.get('stl_path')}")
    print(f"    文件:       {'✅ 存在' if r.get('stl_exists') else '❌ 不存在'} ({r.get('stl_size')} bytes)")
    print(f"  文档已保存:   {'✅ Fusion Team' if r.get('doc_is_saved') else '⚠️ 否 (saveAs 需云端)'}")

    all_ok = r.get("step_exists") and r.get("stl_exists") and r.get("body_volume", 0) > 0
    print("-" * 60)
    if all_ok:
        print("🎉 全链路验证通过！STEP + STL 导出成功落盘。")
        return 0
    else:
        print("⚠️ 部分环节未通过，详见上方")
        return 1


if __name__ == "__main__":
    sys.exit(main())
