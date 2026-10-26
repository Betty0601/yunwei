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

    occ = get_occurrence('TestShaft:1')
    comp = occ.component
    body = comp.bRepBodies.item(0)

    for j in range(body.faces.count):
        face = body.faces.item(j)
        geom = face.geometry
        print(f'Face[{j}]: surfaceType={geom.surfaceType}, area={face.area:.4f}')
        print(f'  geom type: {type(geom).__name__}')
        attrs = [a for a in dir(geom) if not a.startswith('_')]
        print(f'  attrs: {attrs}')

except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
