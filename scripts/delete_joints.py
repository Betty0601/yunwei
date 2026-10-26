import adsk.core, adsk.fusion, traceback

try:
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent

    # Delete existing joints first
    joints = root.joints
    print(f'Before: {joints.count} joints')

    # Collect names to delete
    joint_names = [joints.item(i).name for i in range(joints.count)]
    for name in joint_names:
        j = joints.itemByName(name)
        if j:
            j.deleteMe()
            print(f'  Deleted: {name}')

    print(f'After delete: {joints.count} joints')

except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
