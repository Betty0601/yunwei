import adsk.core, adsk.fusion, traceback

try:
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent

    jkp = adsk.fusion.JointKeyPointTypes

    # Find shaft cylinder face
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

    # Inspect edges of cylinder face
    print(f'Cylinder face has {cyl_face.edges.count} edges:')
    for i in range(cyl_face.edges.count):
        edge = cyl_face.edges.item(i)
        print(f'  Edge[{i}]: type={edge.objectType}, valid={edge.isValid}')
        # Get the edge's curve
        curve = edge.geometry
        print(f'    curve type: {type(curve).__name__}')
        if hasattr(curve, 'center'):
            c = curve.center
            print(f'    center: ({c.x:.2f}, {c.y:.2f}, {c.z:.2f})')
        if hasattr(curve, 'axis'):
            a = curve.axis
            print(f'    axis: ({a.x:.2f}, {a.y:.2f}, {a.z:.2f})')
    
    # Try create JointGeometry from circular edges
    print('\n--- Testing createByCurve ---')
    for i in range(cyl_face.edges.count):
        edge = cyl_face.edges.item(i)
        jg = adsk.fusion.JointGeometry.createByCurve(edge, jkp.CenterKeyPoint)
        if jg:
            print(f'Edge[{i}] CenterKeyPoint: valid={jg.isValid}')
            print(f'  origin: ({jg.origin.x:.4f}, {jg.origin.y:.4f}, {jg.origin.z:.4f})')
            print(f'  primaryAxis: ({jg.primaryAxisVector.x:.4f}, {jg.primaryAxisVector.y:.4f}, {jg.primaryAxisVector.z:.4f})')
            print(f'  secondaryAxis: ({jg.secondaryAxisVector.x:.4f}, {jg.secondaryAxisVector.y:.4f}, {jg.secondaryAxisVector.z:.4f})')
        else:
            print(f'Edge[{i}] CenterKeyPoint: FAILED (None)')

    # Also try on bearing support
    print('\n--- BearingSupport edges ---')
    bearing_occ = None
    for occ in root.occurrences:
        if occ.name == 'TestBearingSupport:1':
            bearing_occ = occ
            break
    
    bearing_body = bearing_occ.component.bRepBodies.item(0)
    cyl_face2 = None
    for f in bearing_body.faces:
        if f.geometry.surfaceType == 1:
            cyl_face2 = f
            break
    
    for i in range(cyl_face2.edges.count):
        edge = cyl_face2.edges.item(i)
        jg = adsk.fusion.JointGeometry.createByCurve(edge, jkp.CenterKeyPoint)
        if jg:
            print(f'Bearing Edge[{i}] CenterKeyPoint:')
            print(f'  origin: ({jg.origin.x:.4f}, {jg.origin.y:.4f}, {jg.origin.z:.4f})')
            print(f'  primaryAxis: ({jg.primaryAxisVector.x:.4f}, {jg.primaryAxisVector.y:.4f}, {jg.primaryAxisVector.z:.4f})')

except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
