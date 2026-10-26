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

    def describe_component(name):
        occ = get_occurrence(name)
        if not occ:
            print(f'NOT FOUND: {name}')
            return
        comp = occ.component
        body = comp.bRepBodies.item(0)
        print(f'\n=== {name} ===')
        print(f'  transform: {occ.transform}')
        for j in range(body.faces.count):
            face = body.faces.item(j)
            geom = face.geometry
            stype = geom.surfaceType
            normal = face.normal if hasattr(face, 'normal') else None
            print(f'  Face[{j}]: surfaceType={stype}')
            print(f'    area={face.area:.4f}')
            print(f'    valid={face.isValid}')
            if stype == 1:  # cylinder
                axis_pt = geom.axisPoint
                axis_vec = geom.axisVector
                print(f'    CYLINDER: axisPoint=({axis_pt.x:.2f},{axis_pt.y:.2f},{axis_pt.z:.2f})')
                print(f'    CYLINDER: axisVector=({axis_vec.x:.4f},{axis_vec.y:.4f},{axis_vec.z:.4f})')
                print(f'    CYLINDER: radius={geom.radius:.4f}')
            elif stype == 0:  # plane
                origin = geom.origin
                normal = geom.normal
                print(f'    PLANE: origin=({origin.x:.2f},{origin.y:.2f},{origin.z:.2f})')
                print(f'    PLANE: normal=({normal.x:.4f},{normal.y:.4f},{normal.z:.4f})')

    describe_component('TestShaft:1')
    describe_component('TestBearingSupport:1')
    describe_component('TestSlider:1')
    describe_component('TestGuideBracket:1')

except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
