import adsk.core, adsk.fusion, traceback

try:
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent

    print(f'=== FINAL VERIFICATION ===')
    print(f'Document: {app.activeDocument.name}')
    print(f'Saved: {app.activeDocument.isSaved}')
    print(f'Joints count: {root.joints.count}')
    
    for i in range(root.joints.count):
        j = root.joints.item(i)
        motion = j.jointMotion
        print(f'\n--- Joint[{i}]: {j.name} ---')
        print(f'  Type: {type(motion).__name__}')
        print(f'  OccurrenceOne: {j.occurrenceOne.name}')
        print(f'  OccurrenceTwo: {j.occurrenceTwo.name}')
        print(f'  isSuppressed: {j.isSuppressed}')
        
        # Inspect motion
        if isinstance(motion, adsk.fusion.RevoluteJointMotion):
            print(f'  rotationAxis: ({motion.rotationAxisVector.x:.2f}, {motion.rotationAxisVector.y:.2f}, {motion.rotationAxisVector.z:.2f})')
            print(f'  rotationLimits: {motion.rotationLimits.minimumValue} ~ {motion.rotationLimits.maximumValue}')
        elif isinstance(motion, adsk.fusion.SliderJointMotion):
            print(f'  slideDirection: ({motion.slideDirectionVector.x:.2f}, {motion.slideDirectionVector.y:.2f}, {motion.slideDirectionVector.z:.2f})')
            print(f'  slideLimits: {motion.slideLimits.minimumValue} ~ {motion.slideLimits.maximumValue}')

    # Check component transforms
    print(f'\n=== Occurrence Transforms ===')
    for occ in root.occurrences:
        # Extract translation from matrix
        t = occ.transform
        tx, ty, tz = t.translation.x, t.translation.y, t.translation.z
        print(f'  {occ.name}: translation=({tx:.1f}, {ty:.1f}, {tz:.1f})')

except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
