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

    # Test Cylinder axis access
    occ = get_occurrence('TestShaft:1')
    comp = occ.component
    body = comp.bRepBodies.item(0)
    cyl_face = body.faces.item(0)  # cylinder face
    geom = cyl_face.geometry
    print(f'Shaft cylinder geom type: {type(geom).__name__}')
    print(f'  origin: ({geom.origin.x:.4f}, {geom.origin.y:.4f}, {geom.origin.z:.4f})')
    print(f'  axis: ({geom.axis.x:.4f}, {geom.axis.y:.4f}, {geom.axis.z:.4f})')
    print(f'  radius: {geom.radius:.4f}')

    # BearingSupport
    occ2 = get_occurrence('TestBearingSupport:1')
    comp2 = occ2.component
    body2 = comp2.bRepBodies.item(0)
    cyl_face2 = body2.faces.item(0)
    geom2 = cyl_face2.geometry
    print(f'\nBearingSupport cylinder geom type: {type(geom2).__name__}')
    print(f'  origin: ({geom2.origin.x:.4f}, {geom2.origin.y:.4f}, {geom2.origin.z:.4f})')
    print(f'  axis: ({geom2.axis.x:.4f}, {geom2.axis.y:.4f}, {geom2.axis.z:.4f})')
    print(f'  radius: {geom2.radius:.4f}')

    # Also search for JointDirections enum
    print(f'\n=== JointDirections ===')
    jd = adsk.fusion.JointDirections
    attrs = [a for a in dir(jd) if not a.startswith('_')]
    for a in attrs:
        val = getattr(jd, a)
        if isinstance(val, int):
            print(f'  {a} = {val}')

    # Also check what JointGeometry.createByCylinderOrConeFace expects
    print(f'\n=== JointGeometry methods ===')
    jg = adsk.fusion.JointGeometry
    sm = [a for a in dir(jg) if not a.startswith('_')]
    for a in sm:
        val = getattr(jg, a)
        if callable(val):
            # Try to get signature
            print(f'  staticmethod: {a}')
        else:
            print(f'  attr: {a} = {val}')

except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
