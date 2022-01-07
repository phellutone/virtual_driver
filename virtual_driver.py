
from typing import Literal
import bpy
from . import property_tracer


class VirtualDriver(property_tracer.PropertyTracer):
    identifier: Literal['virtual_driver'] = 'virtual_driver'
    mute: bpy.props.BoolProperty()

class InternalVirtualDriver(property_tracer.InternalPropTrace):
    identifier: Literal['internal_virtual_driver'] = 'internal_virtual_driver'
    mute: bpy.props.BoolProperty()

class VirtualDriverIndex(property_tracer.InternalPropTraceIndex):
    identifier: Literal['active_virtual_driver_index'] = 'active_virtual_driver_index'


property_tracer.PropertyTracer.identifier = VirtualDriver.identifier
property_tracer.InternalPropTrace.identifier = InternalVirtualDriver.identifier
property_tracer.InternalPropTraceIndex.identifier = VirtualDriverIndex.identifier



class OBJECT_UL_VirtualDriver(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, 'name', icon='ANIM', text='', emboss=False)
            row.prop(item, 'mute', icon='CHECKBOX_HLT' if not item.mute else 'CHECKBOX_DEHLT', text='', emboss=False)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='', icon=icon)

class OBJECT_PT_VirtualDriver(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_idname = 'VIEW3D_PT_virtual_driever'
    bl_label = 'Virtual Driver'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        base = property_tracer.prop_trace_base_access_context_check(context)
        if base is None:
            return
        pt: VirtualDriver = getattr(base, VirtualDriver.identifier)
        ipt: list[InternalVirtualDriver] = getattr(base, InternalVirtualDriver.identifier)
        index: int = getattr(base, VirtualDriverIndex.identifier)

        layout.template_list(
            OBJECT_UL_VirtualDriver.__name__,
            '',
            base,
            InternalVirtualDriver.identifier,
            base,
            VirtualDriverIndex.identifier,
            rows=3
        )

        if not ipt or index < 0:
            return

        block = ipt[index]

        box = layout.box().column()
        box.template_any_ID(pt, 'id', 'id_type', text='Prop:')
        box.template_path_builder(pt, 'data_path', pt.id, text='Path')

        if pt.is_valid:
            box.prop(pt, 'prop')



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
