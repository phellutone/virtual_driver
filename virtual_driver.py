
import bpy
from . import property_tracer
from .properties import VirtualDriver, VirtualDriverIndex
from .panels import OBJECT_PT_VirtualDriver

def prop_trace_base_access_context(context: bpy.types.Context):
    if isinstance(context, bpy.types.Context):
        if hasattr(context, 'scene'):
            scene = getattr(context, 'scene')
            if isinstance(scene, bpy.types.Scene):
                if hasattr(scene, VirtualDriver.identifier):
                    return getattr(scene, VirtualDriver.identifier)

classes = (
    VirtualDriver,
    OBJECT_PT_VirtualDriver
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    setattr(bpy.types.Scene, VirtualDriver.identifier, bpy.props.PointerProperty(type=VirtualDriver))
    setattr(bpy.types.Scene, VirtualDriverIndex.identifier, bpy.props.IntProperty())

    property_tracer.preregister(
        VirtualDriver,
        prop_trace_base_access_context
    )
    property_tracer.register()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    delattr(bpy.types.Scene, VirtualDriver.identifier)
    delattr(bpy.types.Scene, VirtualDriverIndex.identifier)

    property_tracer.unregister()
