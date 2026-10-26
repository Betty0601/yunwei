import adsk.core, adsk.fusion, traceback

try:
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent

    print(f'Root component: {root.name}')
    print(f'Occurrences: {root.occurrences.count}')
    
    for occ in root.occurrences:
        is_fixed = False
        try:
            is_fixed = occ.isFrozen
        except:
            pass
        print(f'  {occ.name}: isFrozen={is_fixed}, visible={occ.isVisible}')
    
    print(f'\nJoints: {root.joints.count}')
    for i in range(root.joints.count):
        j = root.joints.item(i)
        print(f'  [{i}] {j.name}: motionType={j.jointMotion.objectType}')
        print(f'      occOne={j.occurrenceOne.name if j.occurrenceOne else "None"}, occTwo={j.occurrenceTwo.name if j.occurrenceTwo else "None"}')
    
    print(f'\nConstraints: {root.constraints.count}')
    for i in range(root.constraints.count):
        c = root.constraints.item(i)
        print(f'  [{i}] {c.name}: type={c.objectType}')
    
    print(f'\nAllOccurrences in design:')
    print(f'  count={design.allOccurrences.count}')

except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
