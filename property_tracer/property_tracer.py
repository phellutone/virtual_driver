from typing import Callable
import bpy
from .properties import PropertyTracer, InternalPropTrace, InternalPropTraceIndex
from .operators import PROPTRACE_OT_add, PROPTRACE_OT_remove
from .base import _PROPTRACE_BASE_TYPE, _PROPTRACE_BASE_PATHS, _PROPTRACE_BASE_ACCESSES

def property_tracer_context(context):
    if isinstance(context, bpy.types.Context):
        if hasattr(context, 'scene'):
            return getattr(context, 'scene')

base_type = bpy.types.Scene
base_paths = {
    PropertyTracer.identifier: bpy.props.PointerProperty(type=PropertyTracer),
    InternalPropTrace.identifier: bpy.props.CollectionProperty(type=InternalPropTrace)
}
base_accesses = {
    bpy.types.Context.__name__: property_tracer_context
}



classes = (
    PropertyTracer,
    InternalPropTrace,
    PROPTRACE_OT_add,
    PROPTRACE_OT_remove
)

def preregister(
    base_type: bpy.types.bpy_struct=base_type,
    base_paths: dict[str, bpy.props._PropertyDeferred]=base_paths,
    base_accesses: dict[str, Callable[[bpy.types.bpy_struct], bpy.types.bpy_struct]]=base_accesses
) -> None:
    global _PROPTRACE_BASE_TYPE, _PROPTRACE_BASE_PATHS, _PROPTRACE_BASE_ACCESSES
    _PROPTRACE_BASE_TYPE = base_type
    _PROPTRACE_BASE_PATHS = base_paths
    _PROPTRACE_BASE_ACCESSES = base_accesses

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    for identifier in _PROPTRACE_BASE_PATHS:
        setattr(_PROPTRACE_BASE_TYPE, identifier, _PROPTRACE_BASE_PATHS[identifier])
    setattr(_PROPTRACE_BASE_TYPE, InternalPropTraceIndex.identifier, bpy.props.IntProperty())

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for identifier in _PROPTRACE_BASE_PATHS:
        delattr(_PROPTRACE_BASE_TYPE, identifier)
    delattr(_PROPTRACE_BASE_TYPE, InternalPropTraceIndex.identifier)
