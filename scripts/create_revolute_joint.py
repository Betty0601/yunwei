import adsk.core, adsk.fusion, traceback

try:
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent

    def get_occurrence(name):
        for occ in root.occurrences:
            if occ.name == name:
                return occ
        return None

    jkp = adsk.fusion.JointKeyPointTypes
    jd = adsk.fusion.JointDirections

    # ── Create revolute joint: TestShaft ↔ TestBearingSupport ──
    print("=== Creating Revolute Joint ===")

    shaft_occ = get_occurrence('TestShaft:1')
    bearing_occ = get_occurrence('TestBearingSupport:1')

    shaft_body = shaft_occ.component.bRepBodies.item(0)
    bearing_body = bearing_occ.component.bRepBodies.item(0)

    # Find cylinder edges (circular) from each body
    shaft_cyl_face = None
    for f in shaft_body.faces:
        if f.geometry.surfaceType == 1:
            shaft_cyl_face = f
            break

    bearing_cyl_face = None
    for f in bearing_body.faces:
        if f.geometry.surfaceType == 1:
            bearing_cyl_face = f
            break

    # Use Edge[1] from both - they both have origin at z=45
    jg_shaft = adsk.fusion.JointGeometry.createByCurve(
        shaft_cyl_face.edges.item(1), jkp.CenterKeyPoint)
    jg_bearing = adsk.fusion.JointGeometry.createByCurve(
        bearing_cyl_face.edges.item(1), jkp.CenterKeyPoint)

    print(f'JG shaft: origin=({jg_shaft.origin.x:.2f},{jg_shaft.origin.y:.2f},{jg_shaft.origin.z:.2f}), axis=({jg_shaft.primaryAxisVector.x:.2f},{jg_shaft.primaryAxisVector.y:.2f},{jg_shaft.primaryAxisVector.z:.2f})')
    print(f'JG bearing: origin=({jg_bearing.origin.x:.2f},{jg_bearing.origin.y:.2f},{jg_bearing.origin.z:.2f}), axis=({jg_bearing.primaryAxisVector.x:.2f},{jg_bearing.primaryAxisVector.y:.2f},{jg_bearing.primaryAxisVector.z:.2f})')

    joints = root.joints
    revolute_input = joints.createInput(jg_shaft, jg_bearing)
    revolute_input.setAsRevoluteJointMotion(jd.ZAxisJointDirection)
    revolute_joint = joints.add(revolute_input)
    print(f'✅ REVOLUTE JOINT CREATED: "{revolute_joint.name}"')

except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
