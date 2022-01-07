
import bpy
from . import property_tracer
from .properties import VirtualDriver, InternalVirtualDriver, VirtualDriverIndex
from .panels import OBJECT_PT_VirtualDriver, OBJECT_UL_VirtualDriver

property_tracer.PropertyTracer.identifier = VirtualDriver.identifier
property_tracer.InternalPropTrace.identifier = InternalVirtualDriver.identifier
property_tracer.InternalPropTraceIndex.identifier = VirtualDriverIndex.identifier

def virtual_driver_base_access_context(context: bpy.types.Context):
    if isinstance(context, bpy.types.Context):
        if hasattr(context, 'scene'):
            scene = getattr(context, 'scene')
            return scene

_VIRTUALDRIVER_BASE_TYPE = bpy.types.Scene
_VIRTUALDRIVER_BASE_ACCESS_CONTEXT = virtual_driver_base_access_context
_VIRTUALDRIVER_BASE_PATHS = {
    VirtualDriver.identifier: bpy.props.PointerProperty(type=VirtualDriver),
    InternalVirtualDriver.identifier: bpy.props.CollectionProperty(type=InternalVirtualDriver),
    VirtualDriverIndex.identifier: bpy.props.IntProperty(update=property_tracer.internal_prop_trace_index_update)
}

classes = (
    VirtualDriver,
    InternalVirtualDriver,
    property_tracer.PROPTRACE_OT_add,
    property_tracer.PROPTRACE_OT_remove,
    OBJECT_UL_VirtualDriver,
    OBJECT_PT_VirtualDriver
)

def register():
    property_tracer.preregister(_VIRTUALDRIVER_BASE_TYPE, _VIRTUALDRIVER_BASE_ACCESS_CONTEXT)

    for cls in classes:
        bpy.utils.register_class(cls)

    for identifier in _VIRTUALDRIVER_BASE_PATHS:
        setattr(property_tracer._PROPTRACE_BASE_TYPE, identifier, _VIRTUALDRIVER_BASE_PATHS[identifier])

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for identifier in _VIRTUALDRIVER_BASE_PATHS:
        delattr(property_tracer._PROPTRACE_BASE_TYPE, identifier)
