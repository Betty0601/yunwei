"""
Fusion 360 基本几何体创建函数库 (Fusion Python API 脚本)

这些函数通过 Fusion MCP 的 script featureType 在 Fusion 内执行。
兼容 Fusion 2026+ (使用 DistanceExtentDefinition 新 API)。

使用方式:
    from fusion_primitives import create_cube_script
    client.execute_script(create_cube_script(10, 20, 30))
"""

# ── 基本包装器 ──────────────────────────────────────

FUSION_HEADER = """import adsk.core, adsk.fusion, adsk.cam, traceback

_app = None
_ui = None
_design = None
_root = None

def _init():
    global _app, _ui, _design, _root
    _app = adsk.core.Application.get()
    _ui = _app.userInterface
    # 获取或创建文档
    doc = _app.activeDocument
    if not doc or not hasattr(doc, 'products') or doc.products.count == 0:
        doc = _app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    product = doc.products.item(0)
    _design = adsk.fusion.Design.cast(product)
    _root = _design.rootComponent

def _make_point(x, y, z=0):
    return adsk.core.Point3D.create(float(x), float(y), float(z))

_init()
"""

# ── 1. 立方体 ───────────────────────────────────────

def create_cube(width: float = 10, depth: float = 10, height: float = 10,
                name: str = "Cube", origin=(0, 0)) -> str:
    """创建一个立方体 (cm)"""
    x, y = origin
    return FUSION_HEADER + f"""
try:
    # 矩形草图
    sketch = _root.sketches.add(_root.xYConstructionPlane)
    lines = sketch.sketchCurves.sketchLines
    p0 = adsk.core.Point3D.create({x}, {y}, 0)
    p1 = adsk.core.Point3D.create({x + width}, {y + depth}, 0)
    lines.addTwoPointRectangle(p0, p1)
    
    # 拉伸
    profile = sketch.profiles.item(0)
    extInput = _root.features.extrudeFeatures.createInput(
        profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    dist = adsk.core.ValueInput.createByReal({height})
    extent = adsk.fusion.DistanceExtentDefinition.create(dist)
    extInput.setOneSideExtent(extent, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    ext = _root.features.extrudeFeatures.add(extInput)
    
    body = ext.bodies.item(0)
    body.name = "{name}"
    print(f"CREATED_CUBE name={{body.name}} volume={{body.volume:.4f}}")
except:
    print("ERROR: " + traceback.format_exc())
"""

# ── 2. 圆柱体 ───────────────────────────────────────

def create_cylinder(radius: float = 10, height: float = 20,
                    name: str = "Cylinder", origin=(0, 0, 0)) -> str:
    """创建一个圆柱体"""
    x, y = origin
    return FUSION_HEADER + f"""
try:
    sketch = _root.sketches.add(_root.xYConstructionPlane)
    circles = sketch.sketchCurves.sketchCircles
    center = adsk.core.Point3D.create({x}, {y}, 0)
    circles.addByCenterRadius(center, {radius})
    
    profile = sketch.profiles.item(0)
    extInput = _root.features.extrudeFeatures.createInput(
        profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    dist = adsk.core.ValueInput.createByReal({height})
    extent = adsk.fusion.DistanceExtentDefinition.create(dist)
    extInput.setOneSideExtent(extent, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    ext = _root.features.extrudeFeatures.add(extInput)
    
    body = ext.bodies.item(0)
    body.name = "{name}"
    print(f"CREATED_CYLINDER name={{body.name}} volume={{body.volume:.4f}}")
except:
    print("ERROR: " + traceback.format_exc())
"""

# ── 3. 球体 ──────────────────────────────────────────

def create_sphere(radius: float = 10, name: str = "Sphere", origin=(0, 0, 0)) -> str:
    """创建一个球体 (通过旋转半圆)"""
    x, y = origin
    return FUSION_HEADER + f"""
try:
    # 在前视面上画半圆
    sketch = _root.sketches.add(_root.xZConstructionPlane)
    arcs = sketch.sketchCurves.sketchArcs
    lines = sketch.sketchCurves.sketchLines
    
    # 半圆：圆心在 origin，从 (-r, 0) 到 (r, 0)，弧顶在 (0, r)
    center = adsk.core.Point3D.create({x}, 0, {y})
    start = adsk.core.Point3D.create({x - radius}, 0, {y})
    end = adsk.core.Point3D.create({x + radius}, 0, {y + radius})  # 右上象限
    arcs.addByThreePoints(start, adsk.core.Point3D.create({x}, 0, {y + radius}), end)
    # 直径线
    lines.addByTwoPoints(start, adsk.core.Point3D.create({x + radius}, 0, {y}))
    
    profile = sketch.profiles.item(0)
    
    # 旋转 360 度
    revolves = _root.features.revolveFeatures
    axis = _root.yConstructionAxis
    revInput = revolves.createInput(profile, axis, 
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    angle = adsk.core.ValueInput.createByString("360 deg")
    revInput.setAngleExtent(angle, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    rev = revolves.add(revInput)
    
    body = rev.bodies.item(0)
    body.name = "{name}"
    print(f"CREATED_SPHERE name={{body.name}} volume={{body.volume:.4f}}")
except:
    print("ERROR: " + traceback.format_exc())
"""

# ── 4. 带孔方块 ──────────────────────────────────────

def create_bracket(width=40, height=30, thickness=5, hole_diameter=8,
                   name="Bracket") -> str:
    """创建一个简单带孔支架"""
    return FUSION_HEADER + f"""
try:
    # 底板
    sketch1 = _root.sketches.add(_root.xYConstructionPlane)
    lines1 = sketch1.sketchCurves.sketchLines
    lines1.addTwoPointRectangle(
        adsk.core.Point3D.create(0, 0, 0),
        adsk.core.Point3D.create({width}, {height}, 0))
    extInput = _root.features.extrudeFeatures.createInput(
        sketch1.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    dist = adsk.core.ValueInput.createByReal({thickness})
    extent = adsk.fusion.DistanceExtentDefinition.create(dist)
    extInput.setOneSideExtent(extent, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    base = _root.features.extrudeFeatures.add(extInput).bodies.item(0)
    
    # 四个角的孔
    half_d = {hole_diameter} / 2
    holes = [
        ({half_d + 3}, {half_d + 3}),
        ({width - half_d - 3}, {half_d + 3}),
        ({half_d + 3}, {height - half_d - 3}),
        ({width - half_d - 3}, {height - half_d - 3}),
    ]
    
    for hx, hy in holes:
        hole_sketch = _root.sketches.add(_root.xYConstructionPlane)
        hole_sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(hx, hy, 0), half_d)
        hInput = _root.features.extrudeFeatures.createInput(
            hole_sketch.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        hInput.setOneSideExtent(
            adsk.fusion.AllExtentDefinition.create(
                adsk.fusion.ExtentDirections.PositiveExtentDirection),
            adsk.fusion.ExtentDirections.PositiveExtentDirection)
        _root.features.extrudeFeatures.add(hInput)
    
    base.name = "{name}"
    print(f"CREATED_BRACKET name={{base.name}}")
except:
    print("ERROR: " + traceback.format_exc())
"""

# ── 5. 扫掠 (弹簧) ───────────────────────────────────

def create_spring(wire_diameter=2, coil_diameter=20, coils=5, height=50,
                  name="Spring") -> str:
    """创建一个简化的弹簧（用 sweep 做单圈）"""
    # 注意：真正的弹簧需要螺旋曲线，这里简化为圆形扫掠
    mid_z = height / 2
    return FUSION_HEADER + f"""
try:
    # 路径：在 XZ 平面画一个圆（螺旋简化版）
    path_sketch = _root.sketches.add(_root.xZConstructionPlane)
    path_center = adsk.core.Point3D.create(0, {mid_z}, 0)
    path_sketch.sketchCurves.sketchCircles.addByCenterRadius(path_center, {coil_diameter / 2})
    path = path_sketch.profiles.item(0)
    
    # 轮廓：在 XY 平面画小圆
    profile_sketch = _root.sketches.add(_root.xYConstructionPlane)
    prof_center = adsk.core.Point3D.create({coil_diameter / 2}, 0, {mid_z})
    profile_sketch.sketchCurves.sketchCircles.addByCenterRadius(prof_center, {wire_diameter / 2})
    
    # 扫掠
    sweeps = _root.features.sweepFeatures
    sweepInput = sweeps.createInput(
        profile_sketch.profiles.item(0),
        path,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    sweepInput.pathOptions.profileScaling = adsk.fusion.SweepProfileScalingOptions.NoScalingProfileScalingOption
    sweep = sweeps.add(sweepInput)
    
    body = sweep.bodies.item(0)
    body.name = "{name}"
    print(f"CREATED_SPRING name={{body.name}} volume={{body.volume:.4f}}")
except:
    print("ERROR: " + traceback.format_exc())
"""


# ── 通用执行器 ────────────────────────────────────────

def execute_fusion(script: str, client) -> str:
    """执行脚本并提取有意义的输出"""
    try:
        result = client.execute_script(script)
        if isinstance(result, dict):
            msg = result.get("message", "")
            if "SUCCESS" in msg or "CREATED" in msg:
                return msg
            elif "ERROR" in msg:
                return f"❌ {msg}"
            return msg
        return str(result)
    except Exception as e:
        return f"❌ Exception: {e}"


if __name__ == "__main__":
    # 快速测试
    print("Testing Fusion primitives...")
    from mcp_client.fusion_mcp import connect
    
    client = connect()
    print(f"Connected OK, Session: {client.session_id[:8]}...")
    
    result = client.execute_script(create_cube(15, 15, 15))
    print(result)
    
    client.disconnect()
