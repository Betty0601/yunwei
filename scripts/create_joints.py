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
    joints = root.joints

    # ── 1. REVOLUTE JOINT: TestShaft ↔ TestBearingSupport ──
    print("=" * 60)
    print("CREATING REVOLUTE JOINT: TestShaft:1 ↔ TestBearingSupport:1")
    print("=" * 60)

    shaft_occ = get_occurrence('TestShaft:1')
    bearing_occ = get_occurrence('TestBearingSupport:1')

    # Find cylinder face edge (circular) from each
    shaft_body = shaft_occ.component.bRepBodies.item(0)
    bearing_body = bearing_occ.component.bRepBodies.item(0)

    shaft_cyl_edge = None
    for f in shaft_body.faces:
        if f.geometry.surfaceType == 1:
            # Edge[1] has center at z=0, both components align there
            shaft_cyl_edge = f.edges.item(1)
            break

    bearing_cyl_edge = None
    for f in bearing_body.faces:
        if f.geometry.surfaceType == 1:
            bearing_cyl_edge = f.edges.item(1)
            break

    jg1 = adsk.fusion.JointGeometry.createByCurve(shaft_cyl_edge, jkp.CenterKeyPoint)
    jg2 = adsk.fusion.JointGeometry.createByCurve(bearing_cyl_edge, jkp.CenterKeyPoint)

    print(f'  JG1 origin: ({jg1.origin.x:.2f},{jg1.origin.y:.2f},{jg1.origin.z:.2f})')
    print(f'  JG1 axis:   ({jg1.primaryAxisVector.x:.2f},{jg1.primaryAxisVector.y:.2f},{jg1.primaryAxisVector.z:.2f})')
    print(f'  JG2 origin: ({jg2.origin.x:.2f},{jg2.origin.y:.2f},{jg2.origin.z:.2f})')
    print(f'  JG2 axis:   ({jg2.primaryAxisVector.x:.2f},{jg2.primaryAxisVector.y:.2f},{jg2.primaryAxisVector.z:.2f})')

    revolute_input = joints.createInput(jg1, jg2)
    revolute_input.setAsRevoluteJointMotion(jd.ZAxisJointDirection)
    revolute_joint = joints.add(revolute_input)
    print(f'\n  ✅ CREATED: "{revolute_joint.name}"')
    print(f'     Motion: RevoluteJointMotion (rotation around Z axis)')

    # ── 2. SLIDER JOINT: TestSlider ↔ TestGuideBracket ──
    print("\n" + "=" * 60)
    print("CREATING SLIDER JOINT: TestSlider:1 ↔ TestGuideBracket:1")
    print("=" * 60)

    slider_occ = get_occurrence('TestSlider:1')
    guide_occ = get_occurrence('TestGuideBracket:1')

    slider_body = slider_occ.component.bRepBodies.item(0)
    guide_body = guide_occ.component.bRepBodies.item(0)

    # Use planar faces - pick the face with +Z normal (top face) for both
    slider_top_face = None
    for f in slider_body.faces:
        n = f.geometry.normal
        if abs(n.z - 1.0) < 0.01:
            slider_top_face = f
            break

    guide_top_face = None
    for f in guide_body.faces:
        n = f.geometry.normal
        if abs(n.z - 1.0) < 0.01:
            guide_top_face = f
            break

    print(f'  Slider top face origin: ({slider_top_face.geometry.origin.x:.2f},{slider_top_face.geometry.origin.y:.2f},{slider_top_face.geometry.origin.z:.2f})')
    print(f'  Guide top face origin:  ({guide_top_face.geometry.origin.x:.2f},{guide_top_face.geometry.origin.y:.2f},{guide_top_face.geometry.origin.z:.2f})')

    jg3 = adsk.fusion.JointGeometry.createByPlanarFace(slider_top_face, None, jkp.CenterKeyPoint)
    jg4 = adsk.fusion.JointGeometry.createByPlanarFace(guide_top_face, None, jkp.CenterKeyPoint)

    print(f'  JG3 origin: ({jg3.origin.x:.2f},{jg3.origin.y:.2f},{jg3.origin.z:.2f})')
    print(f'  JG3 axis:   ({jg3.primaryAxisVector.x:.2f},{jg3.primaryAxisVector.y:.2f},{jg3.primaryAxisVector.z:.2f})')
    print(f'  JG4 origin: ({jg4.origin.x:.2f},{jg4.origin.y:.2f},{jg4.origin.z:.2f})')
    print(f'  JG4 axis:   ({jg4.primaryAxisVector.x:.2f},{jg4.primaryAxisVector.y:.2f},{jg4.primaryAxisVector.z:.2f})')

    slider_input = joints.createInput(jg3, jg4)
    slider_input.setAsSliderJointMotion(jd.XAxisJointDirection)
    slider_joint = joints.add(slider_input)
    print(f'\n  ✅ CREATED: "{slider_joint.name}"')
    print(f'     Motion: SliderJointMotion (slide along X axis)')

    # ── Summary ──
    print("\n" + "=" * 60)
    print(f"TOTAL JOINTS NOW: {joints.count}")
    for i in range(joints.count):
        j = joints.item(i)
        print(f'  [{i}] {j.name}: {j.jointMotion.objectType}')
        print(f'      {j.occurrenceOne.name} ↔ {j.occurrenceTwo.name}')
    print("=" * 60)

except Exception as e:
    print(f'\n❌ ERROR: {e}')
    traceback.print_exc()
