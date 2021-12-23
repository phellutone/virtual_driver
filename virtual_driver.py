"""
variables -(driver)> invisible property -(handler)> target

input ID and path of property
check if property is drivable
create variable
register ID, path and array_index
create fcurve
control

"""

import bpy

classes = ()

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
