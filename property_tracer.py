
import enum
from typing import Any, Callable, Literal, Union
import bpy
from .utils import animatable, copy_anim_property



_PROPTRACE_BASE_TYPE: bpy.types.bpy_struct = None
_PROPTRACE_BASE_ACCESS_CONTEXT: Callable[[bpy.types.Context], bpy.types.bpy_struct] = None
_PROPTRACE_BASE_PATHS: dict[str, bpy.props._PropertyDeferred] = dict()

_PROPTRACE_ID_TYPE_STR: list[tuple[str, str, str, str, int]] = [
    ('ACTION', 'Action', '', 'ACTION', 17217),
    ('ARMATURE', 'Armature', '', 'ARMATURE_DATA', 21057),
    ('BRUSH', 'Brush', '', 'BRUSH_DATA', 21058),
    ('CAMERA', 'Camera', '', 'CAMERA_DATA', 16707),
    ('CACHEFILE', 'Cache File', '', 'FILE', 17987),
    ('CURVE', 'Curve', '', 'CURVE_DATA', 21827),
    ('FONT', 'Font', '', 'FONT_DATA', 18006),
    ('GREASEPENCIL', 'Grease Pencil', '', 'GREASEPENCIL', 17479),
    ('COLLECTION', 'Collection', '', 'OUTLINER_COLLECTION', 21063),
    ('IMAGE', 'Image', '', 'IMAGE_DATA', 19785),
    ('KEY', 'Key', '', 'SHAPEKEY_DATA', 17739),
    ('LIGHT', 'Light', '', 'LIGHT_DATA', 16716),
    ('LIBRARY', 'Library', '', 'LIBRARY_DATA_DIRECT', 18764),
    ('LINESTYLE', 'Line Style', '', 'LINE_DATA', 21324),
    ('LATTICE', 'Lattice', '', 'LATTICE_DATA', 21580),
    ('MASK', 'Mask', '', 'MOD_MASK', 21325),
    ('MATERIAL', 'Material', '', 'MATERIAL_DATA', 16717),
    ('META', 'Metaball', '', 'META_DATA', 16973),
    ('MESH', 'Mesh', '', 'MESH_DATA', 17741),
    ('MOVIECLIP', 'Movie Clip', '', 'TRACKER', 17229),
    ('NODETREE', 'Node Tree', '', 'NODETREE', 21582),
    ('OBJECT', 'Object', '', 'OBJECT_DATA', 16975),
    ('PAINTCURVE', 'Paint Curve', '', 'CURVE_BEZCURVE', 17232),
    ('PALETTE', 'Palette', '', 'COLOR', 19536),
    ('PARTICLE', 'Particle', '', 'PARTICLE_DATA', 16720),
    ('LIGHT_PROBE', 'Light Probe', '', 'LIGHTPROBE_CUBEMAP', 20556),
    ('SCENE', 'Scene', '', 'SCENE_DATA', 17235),
    ('SIMULATION', 'Simulation', '', 'PHYSICS', 18771),
    ('SOUND', 'Sound', '', 'SOUND', 20307),
    ('SPEAKER', 'Speaker', '', 'SPEAKER', 19283),
    ('TEXT', 'Text', '', 'TEXT', 22612),
    ('TEXTURE', 'Texture', '', 'TEXTURE_DATA', 17748),
    ('HAIR', 'Hair', '', 'HAIR_DATA', 16712),
    ('POINTCLOUD', 'Point Cloud', '', 'POINTCLOUD_DATA', 21584),
    ('VOLUME', 'Volume', '', 'VOLUME_DATA', 20310),
    ('WINDOWMANAGER', 'Window Manager', '', 'WINDOW', 19799),
    ('WORLD', 'World', '', 'WORLD_DATA', 20311),
    ('WORKSPACE', 'Workspace', '', 'WORKSPACE', 21335),
]

_PROPTRACE_ID_TYPE_PYTYPE: dict[str, bpy.types.ID] = {
    'ACTION': bpy.types.Action,
    'ARMATURE': bpy.types.Armature,
    'BRUSH': bpy.types.Brush,
    'CAMERA': bpy.types.Camera,
    'CACHEFILE': bpy.types.CacheFile,
    'CURVE': bpy.types.Curve,
    'FONT': bpy.types.VectorFont,
    'GREASEPENCIL': bpy.types.GreasePencil,
    'COLLECTION': bpy.types.Collection,
    'IMAGE': bpy.types.Image,
    'KEY': bpy.types.Key,
    'LIGHT': bpy.types.Light,
    'LIBRARY': bpy.types.Library,
    'LINESTYLE': bpy.types.FreestyleLineStyle,
    'LATTICE': bpy.types.Lattice,
    'MASK': bpy.types.Mask,
    'MATERIAL': bpy.types.Material,
    'META': bpy.types.MetaBall,
    'MESH': bpy.types.Mesh,
    'MOVIECLIP': bpy.types.MovieClip,
    'NODETREE': bpy.types.NodeTree,
    'OBJECT': bpy.types.Object,
    'PAINTCURVE': bpy.types.PaintCurve,
    'PALETTE': bpy.types.Palette,
    'PARTICLE': bpy.types.ParticleSettings,
    'LIGHT_PROBE': bpy.types.LightProbe,
    'SCENE': bpy.types.Scene,
    'SIMULATION': bpy.types.ID,
    'SOUND': bpy.types.Sound,
    'SPEAKER': bpy.types.Speaker,
    'TEXT': bpy.types.Text,
    'TEXTURE': bpy.types.Texture,
    'HAIR': bpy.types.ID,
    'POINTCLOUD': bpy.types.ID,
    'VOLUME': bpy.types.Volume,
    'WINDOWMANAGER': bpy.types.WindowManager,
    'WORLD': bpy.types.World,
    'WORKSPACE': bpy.types.WorkSpace,
}


class PropertyTracer(bpy.types.PropertyGroup):
    identifier: Literal['property_tracer'] = 'property_tracer'

    def is_valid_update(self, context: bpy.types.Context) -> None:
        if not self.is_valid:
            return
        anim = animatable(self.id, self.data_path)
        if anim is None:
            self.is_valid = False
            return
        self.__class__.prop = copy_anim_property(
            anim.prop,
            lambda self, context: property_tracer_update(context, 'prop')
        )
        if anim.array_index is None:
            self.prop = getattr(anim.id.path_resolve(anim.rna_path) if anim.rna_path else anim.id, anim.prop_path)
        else:
            self.prop = getattr(anim.id.path_resolve(anim.rna_path) if anim.rna_path else anim.id, anim.prop_path)[anim.array_index]
        property_tracer_update(context, 'is_valid')

    def id_type_update(self, context: bpy.types.Context) -> None:
        def id_update(self: PropertyTracer, context: bpy.types.Context) -> None:
            anim = animatable(self.id, self.data_path)
            self.is_valid = not anim is None
            property_tracer_update(context, 'id')

        self.id = None
        self.__class__.id = bpy.props.PointerProperty(
            type=_PROPTRACE_ID_TYPE_PYTYPE[self.id_type],
            name='ID',
            description='ID-Block that the specific property used can be found drom (id_type property must be set first).',
            update=id_update
        )
        property_tracer_update(context, 'id_type')

    def data_path_update(self, context: bpy.types.Context) -> None:
        anim = animatable(self.id, self.data_path)
        self.is_valid = not anim is None
        property_tracer_update(context, 'data_path')

    name: bpy.props.StringProperty(
        update=lambda self, context: property_tracer_update(context, 'name')
    )
    index: bpy.props.IntProperty()
    is_valid: bpy.props.BoolProperty(
        update=is_valid_update
    )

    id_type: bpy.props.EnumProperty(
        items=_PROPTRACE_ID_TYPE_STR,
        name='ID Type',
        description='Type of ID-block that can be used',
        default='OBJECT',
        update=id_type_update
    )

    id: bpy.props.PointerProperty(type=bpy.types.ID)

    data_path: bpy.props.StringProperty(
        name='Data Path',
        description='RNA Path (from ID-Block) to property used.',
        update=data_path_update
    )

    prop: bpy.props._PropertyDeferred

class InternalPropTrace(bpy.types.PropertyGroup):
    identifier: Literal['internal_prop_trace'] = 'internal_prop_trace'

    def is_valid_update(self, context: bpy.types.Context) -> None:
        if not self.is_valid:
            return
        anim = animatable(self.id, self.data_path)
        if anim is None:
            self.is_valid = False
            return
        if anim.array_index is None:
            self.prop = getattr(anim.id.path_resolve(anim.rna_path) if anim.rna_path else anim.id, anim.prop_path)
        else:
            self.prop = getattr(anim.id.path_resolve(anim.rna_path) if anim.rna_path else anim.id, anim.prop_path)[anim.array_index]
        internal_prop_trace_update(self, context, 'is_valid')

    def id_type_update(self, context: bpy.types.Context) -> None:
        self.is_valid = isinstance(self.id, _PROPTRACE_ID_TYPE_PYTYPE[self.id_type])
        internal_prop_trace_update(self, context, 'id_type')

    def id_update(self, context: bpy.types.Context) -> None:
        anim = animatable(self.id, self.data_path)
        self.is_valid = not anim is None
        internal_prop_trace_update(self, context, 'id')

    def data_path_update(self, context: bpy.types.Context) -> None:
        anim = animatable(self.id, self.data_path)
        self.is_valid = not anim is None
        internal_prop_trace_update(self, context, 'data_path')

    name: bpy.props.StringProperty(
        update=lambda self, context: internal_prop_trace_update(self, context, 'name')
    )
    index: bpy.props.IntProperty()
    is_valid: bpy.props.BoolProperty(
        update=is_valid_update
    )
    id_type: bpy.props.StringProperty(
        update=id_type_update
    )
    id: bpy.props.PointerProperty(
        type=bpy.types.ID,
        update=id_update
    )
    data_path: bpy.props.StringProperty(
        update=data_path_update
    )
    prop: bpy.props.FloatProperty(
        update=lambda self, context: internal_prop_trace_update(self, context, 'prop')
    )

class InternalPropTraceIndex:
    identifier: Literal['active_internal_prop_trace_index'] = 'active_internal_prop_trace_index'

class TraceMode(enum.Enum):
    direct: Literal['direct'] = 'direct'
    panel: Literal['panel'] = 'panel'
    none: Literal['none'] = 'none'

_PROPTRACE_TRACE_MODE: TraceMode = TraceMode.none


def trace(
    pto: Union[PropertyTracer, InternalPropTrace],
    identifier: str,
    pfrom: Union[PropertyTracer, InternalPropTrace],
    is_set_value: bool=False,
    value: Any=None
) -> None:
    setattr(pto, identifier, getattr(pfrom, identifier) if not is_set_value else value)

def property_tracer_update(context: bpy.types.Context, identifier: str) -> None:
    global _PROPTRACE_TRACE_MODE
    if _PROPTRACE_TRACE_MODE is TraceMode.direct:
        return

    props = get_context_block(context)
    if props is None:
        return
    pt, ipt, index, block = props

    _PROPTRACE_TRACE_MODE = TraceMode.panel
    trace(block, identifier, pt)
    _PROPTRACE_TRACE_MODE = TraceMode.none

def internal_prop_trace_update(self: InternalPropTrace, context: bpy.types.Context, identifier: str) -> None:
    global _PROPTRACE_TRACE_MODE
    if _PROPTRACE_TRACE_MODE is TraceMode.panel:
        return

    props = get_context_block(context)
    if props is None:
        return
    pt, ipt, index, block = props

    if not block == self:
        return

    _PROPTRACE_TRACE_MODE = TraceMode.direct
    trace(pt, identifier, block)
    _PROPTRACE_TRACE_MODE = TraceMode.none

def internal_prop_trace_index_update(self: bpy.types.bpy_struct, context: bpy.types.Context) -> None:
    global _PROPTRACE_TRACE_MODE
    if _PROPTRACE_TRACE_MODE is TraceMode.panel:
        return

    props = get_context_block(context)
    if props is None:
        return
    pt, ipt, index, block = props

    temp_id = block.id

    _PROPTRACE_TRACE_MODE = TraceMode.direct
    trace(pt, 'index', block)
    trace(pt, 'name', block)
    trace(pt, 'id_type', block)
    trace(pt, 'id', block, True, temp_id)
    trace(pt, 'data_path', block)
    trace(pt, 'prop', block)
    _PROPTRACE_TRACE_MODE = TraceMode.none


class PROPTRACE_OT_add(bpy.types.Operator):
    bl_idname = 'prop_trace.add'
    bl_label = 'add'
    bl_description = ''
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> set[str]:
        base = prop_trace_base_access_check(_PROPTRACE_BASE_ACCESS_CONTEXT(context))
        if base is None:
            return {'CANCELLED'}
        pt: PropertyTracer = getattr(base, PropertyTracer.identifier)
        ipt: list[InternalPropTrace] = getattr(base, InternalPropTrace.identifier)
        index: int = getattr(base, InternalPropTraceIndex.identifier)

        block: InternalPropTrace = ipt.add()
        length = len(ipt)
        block.name = 'Property '+str(length)
        block.index = length-1
        block.is_valid = False
        block.id_type = 'OBJECT'

        setattr(base, InternalPropTraceIndex.identifier, length-1)
        return {'FINISHED'}

class PROPTRACE_OT_remove(bpy.types.Operator):
    bl_idname = 'prop_trace.remove'
    bl_label = 'remove'
    bl_description = ''
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> set[str]:
        base = prop_trace_base_access_check(_PROPTRACE_BASE_ACCESS_CONTEXT(context))
        if base is None:
            return {'CANCELLED'}
        pt: PropertyTracer = getattr(base, PropertyTracer.identifier)
        ipt: list[InternalPropTrace] = getattr(base, InternalPropTrace.identifier)
        index: int = getattr(base, InternalPropTraceIndex.identifier)
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


def get_context_block(context: bpy.types.Context) -> Union[tuple[PropertyTracer, list[InternalPropTrace], int, InternalPropTrace], None]:
    base = prop_trace_base_access_check(_PROPTRACE_BASE_ACCESS_CONTEXT(context))
    if base is None:
        return
    pt: PropertyTracer = getattr(base, PropertyTracer.identifier)
    ipt: list[InternalPropTrace] = getattr(base, InternalPropTrace.identifier)
    index: int = getattr(base, InternalPropTraceIndex.identifier)
    if not ipt or index < 0:
        return
    block = ipt[index]
    return (pt, ipt, index, block)

def prop_trace_base_access_check(base: bpy.types.bpy_struct) -> Union[bpy.types.bpy_struct, None]:
    if not isinstance(base, _PROPTRACE_BASE_TYPE):
        return
    if (
        not hasattr(base, PropertyTracer.identifier) or
        not hasattr(base, InternalPropTrace.identifier) or
        not hasattr(base, InternalPropTraceIndex.identifier)
    ):
        return
    pt: Union[PropertyTracer, None] = getattr(base, PropertyTracer.identifier, None)
    ipt: Union[list[InternalPropTrace], None] = getattr(base, InternalPropTrace.identifier, None)
    index: Union[int, None] = getattr(base, InternalPropTraceIndex.identifier, None)
    if pt is None or ipt is None or index is None:
        return
    return base

def prop_trace_base_access_context(context: bpy.types.Context) -> Union[bpy.types.bpy_struct, None]:
    if isinstance(context, bpy.types.Context):
        if hasattr(context, 'scene'):
            return getattr(context, 'scene')

base_type = bpy.types.Scene
base_access_context = prop_trace_base_access_context
base_paths = {
    PropertyTracer.identifier: bpy.props.PointerProperty(type=PropertyTracer),
    InternalPropTrace.identifier: bpy.props.CollectionProperty(type=InternalPropTrace),
    InternalPropTraceIndex.identifier: bpy.props.IntProperty(update=internal_prop_trace_index_update)
}

def preregister(
    base_type: bpy.types.bpy_struct = base_type,
    base_access_context: Callable[[bpy.types.Context], bpy.types.bpy_struct] = base_access_context
) -> None:
    global _PROPTRACE_BASE_TYPE, _PROPTRACE_BASE_ACCESS_CONTEXT, _PROPTRACE_BASE_PATHS
    _PROPTRACE_BASE_TYPE = base_type
    _PROPTRACE_BASE_ACCESS_CONTEXT = base_access_context
    _PROPTRACE_BASE_PATHS = base_paths

classes = (
    PropertyTracer,
    InternalPropTrace,
    PROPTRACE_OT_add,
    PROPTRACE_OT_remove
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    for identifier in _PROPTRACE_BASE_PATHS:
        setattr(_PROPTRACE_BASE_TYPE, identifier, _PROPTRACE_BASE_PATHS[identifier])

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for identifier in _PROPTRACE_BASE_PATHS:
        delattr(_PROPTRACE_BASE_TYPE, identifier)
