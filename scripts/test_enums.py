import adsk.core, adsk.fusion, traceback

try:
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent

    # Find enum values
    print('=== JointQuadrantAngleTypes ===')
    try:
        jqa = adsk.fusion.JointQuadrantAngleTypes
        for a in dir(jqa):
            if not a.startswith('_'):
                print(f'  {a} = {getattr(jqa, a)}')
    except Exception as e:
        print(f'  Error: {e}')

    print('\n=== JointKeyPointTypes ===')
    try:
        jkp = adsk.fusion.JointKeyPointTypes
        for a in dir(jkp):
            if not a.startswith('_'):
                print(f'  {a} = {getattr(jkp, a)}')
    except Exception as e:
        print(f'  Error: {e}')

    # Also try simpler approach: just use createByCurve with a full circular edge from the cylinder face
    print('\n=== Test cylinder edge approach ===')
    shaft_occ = None
    for occ in root.occurrences:
        if occ.name == 'TestShaft:1':
            shaft_occ = occ
            break
    
    if shaft_occ:
        shaft_body = shaft_occ.component.bRepBodies.item(0)
        # Find cylinder face
        cyl_face = None
        for f in shaft_body.faces:
            if f.geometry.surfaceType == 1:
                cyl_face = f
                break
        
        if cyl_face:
            print(f'Cylinder face edges count: {cyl_face.edges.count}')
            for i in range(cyl_face.edges.count):
                edge = cyl_face.edges.item(i)
                print(f'  Edge[{i}]: curveType={edge.geometryType}')
            
            # Try createByCurve with the edge
            if cyl_face.edges.count > 0:
                edge = cyl_face.edges.item(0)
                jg = adsk.fusion.JointGeometry.createByCurve(edge, None)
                if jg:
                    print(f'  createByCurve result valid: {jg.isValid}')
                    print(f'  origin: ({jg.origin.x:.4f}, {jg.origin.y:.4f}, {jg.origin.z:.4f})')
                    print(f'  primaryAxis: ({jg.primaryAxisVector.x:.4f}, {jg.primaryAxisVector.y:.4f}, {jg.primaryAxisVector.z:.4f})')
                else:
                    print('  createByCurve returned None')

except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
