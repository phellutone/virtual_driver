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
from .properties import VirtualDriver
from .panels import OBJECT_PT_VirtualDriver

classes = (
    VirtualDriver,
    OBJECT_PT_VirtualDriver
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.virtual_driver = bpy.props.PointerProperty(type=VirtualDriver)
    bpy.types.Scene.active_virtual_driver_index = bpy.props.IntProperty()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.virtual_driver
    del bpy.types.Scene.active_virtual_driver_index
