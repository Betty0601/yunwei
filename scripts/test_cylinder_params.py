import adsk.core, adsk.fusion, traceback

try:
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent

    jqa = adsk.fusion.JointQuadrantAngleTypes
    jkp = adsk.fusion.JointKeyPointTypes

    shaft_occ = None
    for occ in root.occurrences:
        if occ.name == 'TestShaft:1':
            shaft_occ = occ
            break
    
    shaft_body = shaft_occ.component.bRepBodies.item(0)
    cyl_face = None
    for f in shaft_body.faces:
        if f.geometry.surfaceType == 1:
            cyl_face = f
            break

    # Try all 4 height values
    height_names = ['StartKeyPoint', 'MiddleKeyPoint', 'EndKeyPoint', 'CenterKeyPoint']
    height_vals = [0, 1, 2, 3]

    for i, (hname, hval) in enumerate(zip(height_names, height_vals)):
        jg = adsk.fusion.JointGeometry.createByCylinderOrConeFace(
            cyl_face, jqa.StartJointQuadrantAngleType, hval)
        if jg:
            print(f'  height={hname}({hval}): OK, origin=({jg.origin.x:.2f},{jg.origin.y:.2f},{jg.origin.z:.2f}), primaryAxis=({jg.primaryAxisVector.x:.2f},{jg.primaryAxisVector.y:.2f},{jg.primaryAxisVector.z:.2f})')
        else:
            print(f'  height={hname}({hval}): FAILED (returned None)')

except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
