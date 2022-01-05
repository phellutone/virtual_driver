from typing import Union
import bpy
from .properties import PropertyTracer, InternalPropTrace, InternalPropTraceIndex
from .base import _PROPTRACE_BASE_ACCESSES

class PROPTRACE_OT_add(bpy.types.Operator):
    bl_idname = 'prop_trace.add'
    bl_label = 'add'
    bl_description = ''
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        base = _PROPTRACE_BASE_ACCESSES[bpy.types.Context.__name__](context)
        if (
            not hasattr(base, PropertyTracer.identifier) or
            not hasattr(base, InternalPropTrace.identifier) or
            not hasattr(base, InternalPropTraceIndex.identifier)
        ):
            return {'CANCELLED'}
        pt: Union[PropertyTracer, None] = getattr(base, PropertyTracer.identifier, None)
        ipt: Union[list[InternalPropTrace], None] = getattr(base, InternalPropTrace.identifier, None)
        index: Union[int, None] = getattr(base, InternalPropTraceIndex.identifier, None)
        if pt is None or ipt is None or index is None:
            return {'CANCELLED'}

        length = len(ipt)
        block: InternalPropTrace = ipt.add()
        block.name = 'Property '+str(length)
        block.index = length-1
        block.is_valid = False
        block.id_data = 'OBJECT'

        setattr(base, InternalPropTraceIndex.identifier, length-1)
        return {'FINISHED'}

class PROPTRACE_OT_remove(bpy.types.Operator):
    bl_idname = 'prop_trace.remove'
    bl_label = 'remove'
    bl_description = ''
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        base = _PROPTRACE_BASE_ACCESSES[bpy.types.Context.__name__](context)
        if (
            not hasattr(base, PropertyTracer.identifier) or
            not hasattr(base, InternalPropTrace.identifier) or
            not hasattr(base, InternalPropTraceIndex.identifier)
        ):
            return {'CANCELLED'}
        pt: Union[PropertyTracer, None] = getattr(base, PropertyTracer.identifier, None)
        ipt: Union[list[InternalPropTrace], None] = getattr(base, InternalPropTrace.identifier, None)
        index: Union[int, None] = getattr(base, InternalPropTraceIndex.identifier, None)
        if pt is None or ipt is None or index is None:
            return {'CANCELLED'}
        if not ipt or index < 0:
            return {'CANCELLED'}

        block = ipt[index]
        ipt.remove(index)

        for b in ipt:
            if b.index < index:
                continue
            b.index -= 1
        setattr(base, InternalPropTraceIndex.identifier, min(max(0, index), len(ipt)-1))
        return {'FINISHED'}
