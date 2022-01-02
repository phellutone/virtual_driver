import types
from typing import Any, Callable, Literal, Pattern, Union
from dataclasses import dataclass
import re
import bpy

# rna prpoerty recognize start ---------------------

_PROPTRACE_RE_PATH_DISASSEMBLY: Pattern = re.compile(r'''(\[(?:(?P<str>".*?(?<!\\)")|(?P<int>\d+))\])|(?(1)|(?P<path>\w+))''')

@dataclass
class DisassemblyItem:
    type: Union[Literal['path'], Literal['int'], Literal['str']]
    path: Union[str, int, None]

@dataclass
class AssemblyItem:
    prop: Union[bpy.types.Property, None]
    prna: str
    eval: Any
    path: Union[str, int, None]
    type: Union[Literal['id'], Literal['path'], Literal['int'], Literal['str']]

@dataclass
class Reassembly:
    id: bpy.types.ID
    path: str
    prop: str
    array_index: int
    graph: list[AssemblyItem]

def path_disassembly(path: str) -> list[DisassemblyItem]:
    res = _PROPTRACE_RE_PATH_DISASSEMBLY.finditer(path)
    result = []
    for r in res:
        if r.group('path'):
            result.append(DisassemblyItem('path', r.group('path')))
        elif r.group('int'):
            result.append(DisassemblyItem('int', int(r.group('int'))))
        elif r.group('str'):
            result.append(DisassemblyItem('str', r.group('str')))
    return result

def path_assembly(id: bpy.types.ID, path: list[DisassemblyItem], resolve=True) -> list[AssemblyItem]:
    res = [AssemblyItem(None, '', id, None, 'id')]
    tmp = id
    stmp = ''
    for i, p in enumerate(path):
        if p.type == 'path':
            e = ('' if i == 0 else '.')+p.path
        elif p.type in ('int', 'str'):
            e = '['+str(p.path)+']'
        prop = None
        stmp = stmp+e
        if resolve:
            try:
                prop = tmp.bl_rna.properties[p.path]
            except Exception as _:
                prop = None
            tmp = id.path_resolve(stmp)
        res.append(AssemblyItem(prop, stmp, tmp, p.path, p.type))
    return res

def path_reassembly(id: bpy.types.ID, path: str) -> Union[Reassembly, None]:
    if not isinstance(id, bpy.types.ID) or path == '':
        return

    try:
        id.path_resolve(path)
        pd = path_disassembly(path)
        graph = path_assembly(id, pd)
        if not graph:
            return
    except Exception as _:
        return

    g1 = graph[-1]
    g2 = graph[-2]
    g3 = graph[-3] if len(graph) > 2 else None

    if g2.type == 'path':
        if g1.type == 'int':
            return Reassembly(id, g3.prna if g3 else '', g2.path, g1.path, graph)
        if g1.type == 'str':
            return Reassembly(id, g3.prna if g3 else '', g2.path+'['+g1.path+']', 0, graph)
    if g1.type == 'path':
        return Reassembly(id, g2.prna, g1.path, 0, graph)
    return

def animatable(id: bpy.types.ID, path: str) -> Union[tuple[bpy.types.ID, str, int, bpy.types.Property], None]:
    pr = path_reassembly(id, path)
    if pr is None:
        return

    rpath = pr.path+('.' if pr.path else '')+pr.prop
    graph = pr.graph
    prop = graph[-1].prop

    if prop is None:
        prop = graph[-2].prop
    if isinstance(prop, bpy.types.Property):
        if not prop.is_animatable:
            return
        if prop.is_readonly:
            return
        if prop.type in ('BOOLEAN', 'INT', 'FLOAT', 'ENUM'):
            if prop.is_array:
                if graph[-1].type == 'int':
                    return (pr.id, rpath, pr.array_index, prop)
                else:
                    return
            return (pr.id, rpath, pr.array_index, prop)
    return

# rna prpoerty recognize end -----------------------

# property trace start -----------------------------

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
    name: bpy.props.StringProperty(
        update=lambda self, context: property_tracer_update(self, 'name')
    )
    index: bpy.props.IntProperty()
    is_valid: bpy.types.BoolProperty(
        update=lambda self, context: property_tracer_update(self, 'is_valid')
    )

    def id_type_update(self, context):
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

    def data_path_update(self, context):
        anim = animatable(self.id, self.data_path)
        if not anim:
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
    name: bpy.props.StringProperty()
    index: bpy.props.IntProperty()
    is_valid: bpy.props.BoolProperty()
    id_type: bpy.props.IntProperty()
    id: bpy.props.PointerProperty(type=bpy.types.ID)
    data_path: bpy.props.StringProperty()

    prop_type: bpy.props.StringProperty()
    prop: bpy.props.FloatProperty()

def copy_anim_property(property: bpy.types.Property, cb: Callable[[Any, bpy.types.Context], None]) -> Union[bpy.props._PropertyDeferred, None]:
    if not isinstance(property, bpy.types.Property):
        return

    name = property.name
    description = property.description
    options = set()
    if property.is_hidden:
        options.add('HIDDEN')
    if property.is_skip_save:
        options.add('SKIP_SAVE')
    if property.is_animatable:
        options.add('ANIMATABLE')
    if property.is_library_editable:
        options.add('LIBRARY_EDITABLE')
    override = set()
    if property.is_overridable:
        override.add('LIBRARY_OVERRIDABLE')

    if property.type == 'BOOLEAN':
        return bpy.props.BoolProperty(
            name=name,
            description=description,
            options=options,
            override=override,
            update=cb
        )

    if property.type == 'INT':
        min = property.hard_min
        max = property.hard_max
        soft_min = property.soft_min
        soft_max = property.soft_max
        step = property.step
        return bpy.props.IntProperty(
            name=name,
            description=description,
            options=options,
            override=override,
            min=min,
            max=max,
            soft_min=soft_min,
            soft_max=soft_max,
            step=step,
            update=cb
        )

    if property.type == 'FLOAT':
        min = property.hard_min
        max = property.hard_max
        soft_min = property.soft_min
        soft_max = property.soft_max
        step = property.step
        precision = property.precision
        return bpy.props.FloatProperty(
            name=name,
            description=description,
            options=options,
            override=override,
            min=min,
            max=max,
            soft_min=soft_min,
            soft_max=soft_max,
            step=step,
            precision=precision,
            update=cb
        )

    if property.type == 'ENUM':
        items = [(i.identifier, i.name, i.description, i.icon, i.value) for i in property.enum_items]
        if property.is_enum_flag:
            options.add('ENUM_FLAG')
            return bpy.props.EnumProperty(
                name=name,
                description=description,
                options=options,
                override=override,
                items=items,
                update=cb
            )
        else:
            return bpy.props.EnumProperty(
                name=name,
                description=description,
                options=options,
                override=override,
                items=items,
                update=cb
            )

def property_tracer_update(self, identifier):
    index: int = self.index
    pt: list[InternalPropTrace] = self.id_data.internal_prop_trace # TODO: register name
    if not pt or index < 0:
        return
    block = pt[index]
    setattr(block, identifier, getattr(self, identifier))

# property trace end -------------------------------
