import bpy
from .utils import path_reassembly, animatable, copy_anim_property

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
    '''
    Dummy Property Tracer class for UI.
    Expect properties type of the class to change in runtime.
    '''
    identifier = 'property_tracer'

    name: bpy.props.StringProperty(
        update=lambda self, context: property_tracer_update(self, 'name')
    )
    index: bpy.props.IntProperty()
    is_valid: bpy.props.BoolProperty(
        update=lambda self, context: property_tracer_update(self, 'is_valid')
    )

    def id_type_update(self, context: bpy.types.Context) -> None:
        self.id = None
        PropertyTracer.id = bpy.props.PointerProperty(type=_PROPTRACE_ID_TYPE_PYTYPE[self.id_type])
        property_tracer_update(self, 'id_type')
    id_type: bpy.props.EnumProperty(
        items=_PROPTRACE_ID_TYPE_STR,
        name='ID Type',
        description='Type of ID-block that can be used',
        default='OBJECT',
        update=id_type_update
    )

    id: bpy.props.PointerProperty(
        type=bpy.types.ID,
        name='ID',
        description='ID-Block that the specific property used can be found drom (id_type property must be set first).',
        update=lambda self, context: property_tracer_update(self, 'id')
    )

    def data_path_update(self, context: bpy.types.Context) -> None:
        anim = animatable(self.id, self.data_path)
        if anim is None:
            self.is_valid = False
            return
        self.is_valid = True
        anim_id, anim_path, anim_arridx, anim_prop = anim
        self.prop_type = anim_prop.type
        PropertyTracer.prop = copy_anim_property(anim_prop, None)
        property_tracer_update(self, 'data_path')
    data_path: bpy.props.StringProperty(
        name='Data Path',
        description='RNA Path (from ID-Block) to property used.'
    )

    prop_type: bpy.props.StringProperty(
        update=lambda self, context: property_tracer_update(self, 'prop_type')
    )
    prop: bpy.props._PropertyDeferred

class InternalPropTrace(bpy.types.PropertyGroup):
    identifier = 'internal_prop_trace'

    name: bpy.props.StringProperty()
    index: bpy.props.IntProperty()
    is_valid: bpy.props.BoolProperty()
    id_type: bpy.props.IntProperty()
    id: bpy.props.PointerProperty(type=bpy.types.ID)
    data_path: bpy.props.StringProperty()

    prop_type: bpy.props.StringProperty()
    prop: bpy.props.FloatProperty()

class InternalPropTraceIndex:
    identifier = 'active_internal_prop_trace_index'

def property_tracer_update(self: PropertyTracer, identifier: str) -> None:
    pr = path_reassembly(self.id_data, self.path_from_id(identifier))
    if not pr:
        return
    graph = pr.graph
    if len(graph) < 3:
        return
    index: int = self.index
    ipt: list[InternalPropTrace] = getattr(graph[-3].eval, InternalPropTrace.identifier)
    if not ipt or index < 0:
        return
    block = ipt[index]
    setattr(block, identifier, getattr(self, identifier))
