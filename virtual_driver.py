
from typing import Literal, Union
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


class VIRTUALDRIVER_OT_add(property_tracer.PROPTRACE_OT_add):
    bl_idname = 'virtual_driver.add'

class VIRTUALDRIVER_OT_remove(property_tracer.PROPTRACE_OT_remove):
    bl_idname = 'virtual_driver.remove'


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
        base = property_tracer.prop_trace_base_access_check(_VIRTUALDRIVER_BASE_ACCESS_CONTEXT(context))
        if base is None:
            return
        vd: VirtualDriver = getattr(base, VirtualDriver.identifier)
        ivd: list[InternalVirtualDriver] = getattr(base, InternalVirtualDriver.identifier)
        index: int = getattr(base, VirtualDriverIndex.identifier)

        row = layout.row()
        row.template_list(
            OBJECT_UL_VirtualDriver.__name__,
            '',
            base,
            InternalVirtualDriver.identifier,
            base,
            VirtualDriverIndex.identifier,
            rows=3
        )
        col = row.column(align=True)
        col.operator(VIRTUALDRIVER_OT_add.bl_idname, icon='ADD', text='')
        col.operator(VIRTUALDRIVER_OT_remove.bl_idname, icon='REMOVE', text='')

        if not ivd or index < 0:
            return

        block = ivd[index]

        box = layout.box().column()
        box.template_any_ID(vd, 'id', 'id_type', text='Prop:')
        box.template_path_builder(vd, 'data_path', vd.id, text='Path')

        if vd.is_valid:
            box.prop(vd, 'prop')



def virtual_driver_base_access_context(context: bpy.types.Context) -> Union[bpy.types.bpy_struct, None]:
    if isinstance(context, bpy.types.Context):
        if hasattr(context, 'scene'):
            return getattr(context, 'scene')

def virtual_driver_base_access_id(id: bpy.types.ID):
    if isinstance(id, _VIRTUALDRIVER_BASE_TYPE_ID):
        return id

_VIRTUALDRIVER_BASE_TYPE_ID = bpy.types.Scene
_VIRTUALDRIVER_BASE_TYPE_PARENT = bpy.types.Scene
_VIRTUALDRIVER_BASE_ACCESS_CONTEXT = virtual_driver_base_access_context
_VIRTUALDRIVER_BASE_ACCESS_ID = virtual_driver_base_access_id
_VIRTUALDRIVER_BASE_PATHS = {
    VirtualDriver.identifier: bpy.props.PointerProperty(type=VirtualDriver),
    InternalVirtualDriver.identifier: bpy.props.CollectionProperty(type=InternalVirtualDriver),
    VirtualDriverIndex.identifier: bpy.props.IntProperty(update=property_tracer.internal_prop_trace_index_update)
}

classes = (
    VirtualDriver,
    InternalVirtualDriver,
    VIRTUALDRIVER_OT_add,
    VIRTUALDRIVER_OT_remove,
    OBJECT_UL_VirtualDriver,
    OBJECT_PT_VirtualDriver
)

_VIRTUALDRIVER_UPDATE_LOCK = False
def virtual_driver_update(scene: bpy.types.Scene, depsgraph: bpy.types.Depsgraph):
    global _VIRTUALDRIVER_UPDATE_LOCK
    if _VIRTUALDRIVER_UPDATE_LOCK:
        return

    ids = [u.id for u in depsgraph.updates if isinstance(u.id, _VIRTUALDRIVER_BASE_TYPE_ID)]
    if not ids:
        return
    base_id = ids[0]
    base = property_tracer.prop_trace_base_access_check(_VIRTUALDRIVER_BASE_ACCESS_ID(base_id))
    if base is None:
        return
    vd: VirtualDriver = getattr(base, VirtualDriver.identifier)
    ivd: list[InternalVirtualDriver] = getattr(base, InternalVirtualDriver.identifier)
    index: int = getattr(base, VirtualDriverIndex.identifier)
    if not ivd or index < 0:
        return

    _VIRTUALDRIVER_UPDATE_LOCK = True

    for block in ivd:
        if not block.is_valid:
            continue

        anim = property_tracer.animatable(block.id, block.data_path)
        if anim is None:
            block.is_valid = False
            return
        if anim.array_index is None:
            setattr(anim.id.original.path_resolve(anim.rna_path) if anim.rna_path else anim.id.original, anim.prop_path, block.prop)
        else:
            getattr(anim.id.original.path_resolve(anim.rna_path) if anim.rna_path else anim.id.original, anim.prop_path)[anim.array_index] = block.prop

    _VIRTUALDRIVER_UPDATE_LOCK = False

def register():
    property_tracer.preregister(_VIRTUALDRIVER_BASE_TYPE_PARENT, _VIRTUALDRIVER_BASE_ACCESS_CONTEXT)

    for cls in classes:
        bpy.utils.register_class(cls)

    for identifier in _VIRTUALDRIVER_BASE_PATHS:
        setattr(_VIRTUALDRIVER_BASE_TYPE_PARENT, identifier, _VIRTUALDRIVER_BASE_PATHS[identifier])

    if not virtual_driver_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(virtual_driver_update)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for identifier in _VIRTUALDRIVER_BASE_PATHS:
        delattr(_VIRTUALDRIVER_BASE_TYPE_PARENT, identifier)

    if virtual_driver_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(virtual_driver_update)
