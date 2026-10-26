import adsk.core, adsk.fusion, traceback

try:
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent

    print(f'=== All Joints ({root.joints.count}) ===')
    for i in range(root.joints.count):
        j = root.joints.item(i)
        print(f'\nJoint[{i}]: {j.name}')
        print(f'  occurrenceOne: {j.occurrenceOne.name}')
        print(f'  occurrenceTwo: {j.occurrenceTwo.name}')
        print(f'  isSuppressed: {j.isSuppressed}')
        print(f'  isVisible: {j.isVisible}')
        print(f'  geometryOrOriginOne: {type(j.geometryOrOriginOne).__name__}')
        print(f'  geometryOrOriginTwo: {type(j.geometryOrOriginTwo).__name__}')
        if j.geometryOrOriginOne:
            print(f'    geo1 origin: ({j.geometryOrOriginOne.origin.x:.2f},{j.geometryOrOriginOne.origin.y:.2f},{j.geometryOrOriginOne.origin.z:.2f})')
            print(f'    geo1 primaryAxis: ({j.geometryOrOriginOne.primaryAxisVector.x:.2f},{j.geometryOrOriginOne.primaryAxisVector.y:.2f},{j.geometryOrOriginOne.primaryAxisVector.z:.2f})')
        if j.geometryOrOriginTwo:
            print(f'    geo2 origin: ({j.geometryOrOriginTwo.origin.x:.2f},{j.geometryOrOriginTwo.origin.y:.2f},{j.geometryOrOriginTwo.origin.z:.2f})')
            print(f'    geo2 primaryAxis: ({j.geometryOrOriginTwo.primaryAxisVector.x:.2f},{j.geometryOrOriginTwo.primaryAxisVector.y:.2f},{j.geometryOrOriginTwo.primaryAxisVector.z:.2f})')
        
        motion = j.jointMotion
        print(f'  motion type: {type(motion).__name__}')
        if hasattr(motion, 'rotationAxisVector'):
            print(f'    rotationAxis: ({motion.rotationAxisVector.x:.2f},{motion.rotationAxisVector.y:.2f},{motion.rotationAxisVector.z:.2f})')
        if hasattr(motion, 'slideDirectionVector'):
            print(f'    slideDirection: ({motion.slideDirectionVector.x:.2f},{motion.slideDirectionVector.y:.2f},{motion.slideDirectionVector.z:.2f})')

except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
