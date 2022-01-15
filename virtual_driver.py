
import enum
from typing import Any, Callable, Literal, Union
import bpy
from . import utils
from . import property_tracer
from . import fcurve_observer



_VIRTUALDRIVER_BASE_TYPE_ID: bpy.types.ID = None
_VIRTUALDRIVER_BASE_TYPE_PARENT: bpy.types.bpy_struct = None
_VIRTUALDRIVER_BASE_ACCESS_CONTEXT: Callable[[bpy.types.Context], bpy.types.bpy_struct] = None
_VIRTUALDRIVER_BASE_ACCESS_ID: Callable[[bpy.types.ID], bpy.types.bpy_struct] = None
_VIRTUALDRIVER_BASE_PATHS: dict[str, bpy.props._PropertyDeferred] = dict()


class VirtualDriver(property_tracer.PropertyTracer, fcurve_observer.FCurveObserver):
    identifier: Literal['virtual_driver'] = 'virtual_driver'
    mute: bpy.props.BoolProperty(
        update=lambda self, context: virtual_driver_update(self, context, 'mute')
    )

class InternalVirtualDriver(property_tracer.InternalPropTrace, fcurve_observer.FCurveObserver):
    identifier: Literal['internal_virtual_driver'] = 'internal_virtual_driver'
    mute: bpy.props.BoolProperty(
        update=lambda self, context: internal_virtual_driver_update(self, context, 'mute')
    )

class VirtualDriverIndex(property_tracer.InternalPropTraceIndex):
    identifier: Literal['active_virtual_driver_index'] = 'active_virtual_driver_index'

class TraceMode(enum.Enum):
    direct = property_tracer.TraceMode.direct
    panel = property_tracer.TraceMode.panel
    none = property_tracer.TraceMode.none

property_tracer.PropertyTracer.identifier = VirtualDriver.identifier
property_tracer.InternalPropTrace.identifier = InternalVirtualDriver.identifier
property_tracer.InternalPropTraceIndex.identifier = VirtualDriverIndex.identifier

_VIRTUALDRIVER_TRACE_MODE: TraceMode = TraceMode.none


def virtual_driver_update(self: VirtualDriver, context: bpy.types.Context, identifier: str):
    global _VIRTUALDRIVER_TRACE_MODE
    if _VIRTUALDRIVER_TRACE_MODE is TraceMode.direct:
        return

    base, vd, ivd, index, block = get_context_props(context)
    if block is None:
        return

    _VIRTUALDRIVER_TRACE_MODE = TraceMode.panel
    setattr(block, identifier, getattr(vd, identifier))
    _VIRTUALDRIVER_TRACE_MODE = TraceMode.none

def internal_virtual_driver_update(self: InternalVirtualDriver, context: bpy.types.Context, identifier: str):
    global _VIRTUALDRIVER_TRACE_MODE
    if _VIRTUALDRIVER_TRACE_MODE is TraceMode.panel:
        return

    base, vd, ivd, index, block = get_context_props(context)
    if block is None:
        return

    _VIRTUALDRIVER_TRACE_MODE = TraceMode.direct
    setattr(vd, identifier, getattr(block, identifier))
    _VIRTUALDRIVER_TRACE_MODE = TraceMode.none

def virtual_driver_index_update(self: bpy.types.bpy_struct, context: bpy.types.Context):
    global _VIRTUALDRIVER_TRACE_MODE
    if _VIRTUALDRIVER_TRACE_MODE is TraceMode.panel:
        return

    base, vd, ivd, index, block = get_context_props(context)
    if block is None:
        return

    _VIRTUALDRIVER_TRACE_MODE = TraceMode.direct
    property_tracer.internal_prop_trace_index_update(self, context)
    setattr(vd, 'mute', getattr(block, 'mute'))
    sync_fcurve(block, vd)
    _VIRTUALDRIVER_TRACE_MODE = TraceMode.none


class VIRTUALDRIVER_OT_add(property_tracer.PROPTRACE_OT_add):
    bl_idname = 'virtual_driver.add'

class VIRTUALDRIVER_OT_remove(property_tracer.PROPTRACE_OT_remove):
    bl_idname = 'virtual_driver.remove'

    def execute(self, context: bpy.types.Context) -> set[str]:
        base, vd, ivd, index, block = get_context_props(context)
        if vd is None or block is None:
            return {'CANCELLED'}
        vd.fcurve = False
        block.fcurve = False
        return super().execute(context)


class OBJECT_UL_VirtualDriver(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index) -> None:
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

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        base, vd, ivd, index, block = get_context_props(context)
        if base is None:
            return

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


def get_context_props(
    data: Union[bpy.types.Context, bpy.types.ID]
) -> tuple[
    Union[bpy.types.bpy_struct, None],
    Union[VirtualDriver, None],
    Union[list[InternalVirtualDriver], None],
    Union[int, None],
    Union[InternalVirtualDriver, None]
]:
    base = _VIRTUALDRIVER_BASE_ACCESS_CONTEXT(data) if isinstance(data, bpy.types.Context) else _VIRTUALDRIVER_BASE_ACCESS_ID(data)
    if not isinstance(base, _VIRTUALDRIVER_BASE_TYPE_PARENT):
        return None, None, None, None, None
    vd: Union[VirtualDriver, None] = getattr(base, VirtualDriver.identifier, None)
    ivd: Union[list[InternalVirtualDriver], None] = getattr(base, InternalVirtualDriver.identifier, None)
    index: Union[int, None] = getattr(base, VirtualDriverIndex.identifier, None)
    if ivd is None or index is None:
        return base, vd, ivd, index, None
    block: Union[InternalVirtualDriver, None] = ivd[index] if ivd and index >= 0 else None
    return base, vd, ivd, index, block

def virtual_driver_base_access_context(context: bpy.types.Context) -> Union[bpy.types.bpy_struct, None]:
    if isinstance(context, bpy.types.Context):
        if hasattr(context, 'scene'):
            return getattr(context, 'scene')

def virtual_driver_base_access_id(id: bpy.types.ID) -> Union[bpy.types.bpy_struct, None]:
    if isinstance(id, _VIRTUALDRIVER_BASE_TYPE_ID):
        return id

def sync_fcurve(pfrom: Union[VirtualDriver, InternalVirtualDriver], pto: Union[VirtualDriver, InternalVirtualDriver]) -> None:
    if not pfrom.fcurve and not pto.fcurve:
        return
    fcurve_observer.delete(pto.id_data, pto.path_from_id('prop'), 0)
    fcurves = fcurve_observer.get(pfrom.id_data, pfrom.path_from_id('prop'), 0)
    if fcurves is None:
        pfrom.fcurve = False
        return
    if isinstance(fcurves, list):
        return
    anim_data: bpy.types.AnimData = getattr(pto.id_data, 'animation_data')
    anim_data_drivers: bpy.types.AnimDataDrivers = anim_data.drivers
    fcopy = anim_data_drivers.from_existing(src_driver=fcurves)
    fcopy.data_path = pto.path_from_id('prop')
    pto.fcurve = True

def back_tracer(obj: bpy.types.bpy_struct, name: str, value: Any, array_index: Union[int, None]) -> None:
    if array_index is None:
        setattr(obj, name, value)
    else:
        getattr(obj, name)[array_index] = value


_VIRTUALDRIVER_UPDATE_LOCK: bool = False

@bpy.app.handlers.persistent
def virtual_driver_depsgraph_update(scene: bpy.types.Scene, depsgraph: bpy.types.Depsgraph) -> None:
    global _VIRTUALDRIVER_UPDATE_LOCK
    if _VIRTUALDRIVER_UPDATE_LOCK:
        return

    _VIRTUALDRIVER_UPDATE_LOCK = True
    ids: list[bpy.types.ID] = depsgraph.ids
    ids = [id.original for id in ids if isinstance(id, _VIRTUALDRIVER_BASE_TYPE_ID)]
    for base_id in ids:
        base, vd, ivd, index, block = get_context_props(base_id)
        if not ivd is None:
            for b in ivd:
                if b.is_valid:
                    b.fcurve = True
        if not vd is None:
            if vd.is_valid:
                vd.fcurve = True

        if not vd is None and not block is None:
            if vd.is_valid and block.is_valid:
                sync_fcurve(vd, block)

        if not ivd is None:
            for b in ivd:
                anim = utils.animatable(b.id, b.data_path)
                if anim is None or b.mute:
                    continue
                back_tracer(anim.id.path_resolve(anim.rna_path) if anim.rna_path else anim.id, anim.prop_path, b.prop, anim.array_index)
    _VIRTUALDRIVER_UPDATE_LOCK = False

base_type_id = bpy.types.Scene
base_type_parent = bpy.types.Scene
base_access_context = virtual_driver_base_access_context
base_access_id = virtual_driver_base_access_id
base_paths = {
    VirtualDriver.identifier: bpy.props.PointerProperty(type=VirtualDriver),
    InternalVirtualDriver.identifier: bpy.props.CollectionProperty(type=InternalVirtualDriver),
    VirtualDriverIndex.identifier: bpy.props.IntProperty(
        name='Active Virtual Driver Index',
        update=virtual_driver_index_update
    )
}

def preregister(
    base_type_id: bpy.types.ID = base_type_id,
    base_type_parent: bpy.types.bpy_struct = base_type_parent,
    base_access_context: Callable[[bpy.types.Context], bpy.types.bpy_struct] = base_access_context,
    base_access_id: Callable[[bpy.types.ID], bpy.types.bpy_struct] = base_access_id
) -> None:
    global _VIRTUALDRIVER_BASE_TYPE_ID, _VIRTUALDRIVER_BASE_TYPE_PARENT, _VIRTUALDRIVER_BASE_ACCESS_CONTEXT, _VIRTUALDRIVER_BASE_ACCESS_ID, _VIRTUALDRIVER_BASE_PATHS
    _VIRTUALDRIVER_BASE_TYPE_ID = base_type_id
    _VIRTUALDRIVER_BASE_TYPE_PARENT = base_type_parent
    _VIRTUALDRIVER_BASE_ACCESS_CONTEXT = base_access_context
    _VIRTUALDRIVER_BASE_ACCESS_ID = base_access_id
    _VIRTUALDRIVER_BASE_PATHS = base_paths
    property_tracer.preregister(base_type_parent, base_access_context)

classes = (
    VirtualDriver,
    InternalVirtualDriver,
    VIRTUALDRIVER_OT_add,
    VIRTUALDRIVER_OT_remove,
    OBJECT_UL_VirtualDriver,
    OBJECT_PT_VirtualDriver
)

def register():
    preregister()

    for cls in classes:
        bpy.utils.register_class(cls)

    for identifier in _VIRTUALDRIVER_BASE_PATHS:
        setattr(_VIRTUALDRIVER_BASE_TYPE_PARENT, identifier, _VIRTUALDRIVER_BASE_PATHS[identifier])

    if not virtual_driver_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(virtual_driver_depsgraph_update)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for identifier in _VIRTUALDRIVER_BASE_PATHS:
        delattr(_VIRTUALDRIVER_BASE_TYPE_PARENT, identifier)

    if virtual_driver_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(virtual_driver_depsgraph_update)
