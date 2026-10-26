import adsk.core, adsk.fusion, traceback

try:
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent

    print(f'Root component: {root.name}')
    print(f'Occurrences count: {root.occurrences.count}')

    for occ in root.occurrences:
        comp = occ.component
        print(f'\nOccurrence: {occ.name}')
        print(f'  Component: {comp.name}')

        bodies = comp.bRepBodies
        print(f'  BRepBodies count: {bodies.count}')

        for i in range(min(bodies.count, 3)):
            body = bodies.item(i)
            face_count = body.faces.count
            print(f'  Body[{i}]: {body.name} (faces: {face_count})')
            for j in range(min(body.faces.count, 5)):
                face = body.faces.item(j)
                surf_type = face.geometry.surfaceType
                area = face.area
                valid = face.isValid
                print(f'    Face[{j}]: surfaceType={surf_type}, area={area:.2f}, valid={valid}')

except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
