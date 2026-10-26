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

    # Inspect slider and guide bracket faces
    for occ_name in ['TestSlider:1', 'TestGuideBracket:1']:
        occ = get_occurrence(occ_name)
        body = occ.component.bRepBodies.item(0)
        print(f'\n=== {occ_name} ===')
        print(f'  transform valid: {occ.transform}')
        for j in range(body.faces.count):
            face = body.faces.item(j)
            geom = face.geometry
            if geom.surfaceType == 0:  # planar
                origin = geom.origin
                normal = geom.normal
                print(f'  Face[{j}]: area={face.area:.1f}')
                print(f'    origin=({origin.x:.1f},{origin.y:.1f},{origin.z:.1f})')
                print(f'    normal=({normal.x:.3f},{normal.y:.3f},{normal.z:.3f})')

except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
