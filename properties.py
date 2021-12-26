from typing import Any, Callable, Union
import bpy
from .utils import copy_anim_property, path_reassembly, animatable

class VirtualDriverDummy:
    name: str
    property: Any

_VIRTUALDRIVER_DUMMY_CLASSES: set[VirtualDriverDummy] = set()

class VirtualDriver(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    index: bpy.props.IntProperty()
    is_valid: bpy.props.BoolProperty()

    dummy: bpy.props.PointerProperty(type=bpy.types.PropertyGroup)

    def id_type_update(self, context):
        self.id = None
        c = eval('bpy.types.'+self.id_type)
        self.__class__.id = bpy.props.PointerProperty(type=c)
    id_type: bpy.props.EnumProperty(items=[
        ('Action',              'Action',           '', 'ACTION',               0),
        ('Armature',            'Armature',         '', 'ARMATURE_DATA',        1),
        ('Brush',               'Brush',            '', 'BRUSH_DATA',           2),
        ('Camera',              'Camera',           '', 'CAMERA_DATA',          3),
        ('CacheFile',           'Cache File',       '', 'FILE',                 4),
        ('Curve',               'Curve',            '', 'CURVE_DATA',           5),
        ('VectorFont',          'Font',             '', 'FONT_DATA',            6),
        ('GreasePencil',        'Grease Pencil',    '', 'GREASEPENCIL',         7),
        ('Collection',          'Collection',       '', 'OUTLINER_COLLECTION',  8),
        ('Image',               'Image',            '', 'IMAGE_DATA',           9),
        ('Key',                 'Key',              '', 'SHAPEKEY_DATA',        10),
        ('Light',               'Light',            '', 'LIGHT_DATA',           11),
        ('Library',             'Library',          '', 'LIBRARY_DATA_DIRECT',  12),
        ('FreestyleLineStyle',  'Line Style',       '', 'LINE_DATA',            13),
        ('Lattice',             'Lattice',          '', 'LATTICE_DATA',         14),
        ('Mask',                'Mask',             '', 'MOD_MASK',             15),
        ('Material',            'Material',         '', 'MATERIAL_DATA',        16),
        ('MetaBall',            'Metaball',         '', 'META_DATA',            17),
        ('Mesh',                'Mesh',             '', 'MESH_DATA',            18),
        ('MovieClip',           'Movie Clip',       '', 'TRACKER',              19),
        ('NodeTree',            'Node Tree',        '', 'NODETREE',             20),
        ('Object',              'Object',           '', 'OBJECT_DATA',          21),
        ('PaintCurve',          'Paint Curve',      '', 'CURVE_BEZCURVE',       22),
        ('Palette',             'Palette',          '', 'COLOR',                23),
        ('ParticleSettings',    'Particle',         '', 'PARTICLE_DATA',        24),
        ('LightProbe',          'Light Probe',      '', 'LIGHTPROBE_CUBEMAP',   25),
        ('Scene',               'Scene',            '', 'SCENE_DATA',           26),
        ('ID',                  'Simulation',       '', 'PHYSICS',              27),
        ('Sound',               'Sound',            '', 'SOUND',                28),
        ('Speaker',             'Speaker',          '', 'SPEAKER',              29),
        ('Text',                'Text',             '', 'TEXT',                 30),
        ('Texture',             'Texture',          '', 'TEXTURE',              31),
        ('ID',                  'Hair',             '', 'HAIR_DATA',            32),
        ('ID',                  'Point Cloud',      '', 'POINTCLOUD_DATA',      33),
        ('Volume',              'Volume',           '', 'VOLUME_DATA',          34),
        ('WindowManager',       'Window Manager',   '', 'WINDOW',               35),
        ('World',               'World',            '', 'WORLD_DATA',           36),
        ('WorkSpace',           'Workspace',        '', 'WORKSPACE',            37)
    ], default=21, update=id_type_update)

    id: bpy.props.PointerProperty(type=bpy.types.Object)
    
    def data_path_update(self, context):
        global _VIRTUALDRIVER_DUMMY_CLASSES
        anim = animatable(self.id, self.data_path)
        if anim is None:
            self.is_valid = False
            return
        _, _, _, property = anim

        li = [int(c.__name__.split('_')[1]) for c in _VIRTUALDRIVER_DUMMY_CLASSES]
        idx = max(max(li) if li else 0, 0)+1
        proptype = create_anim_propcopy('VirtualDriverDummy_'+str(idx), property, dummy_update)
        if proptype is None:
            self.is_valid = False
            return

        _VIRTUALDRIVER_DUMMY_CLASSES.add(proptype)
        print(_VIRTUALDRIVER_DUMMY_CLASSES)
        oldtype: Union[VirtualDriverDummy, bpy.types.PropertyGroup] = self.dummy.__class__
        bpy.utils.register_class(proptype)
        self.__class__.dummy = bpy.props.PointerProperty(type=proptype)
        if VirtualDriverDummy in oldtype.__mro__:
            bpy.utils.unregister_class(oldtype)
            _VIRTUALDRIVER_DUMMY_CLASSES.remove(oldtype)

        self.is_valid = True
    data_path: bpy.props.StringProperty(update=data_path_update)

def dummy_update(self: VirtualDriver, context):
    if not self.is_valid:
        return
    pr = path_reassembly(self.id, self.data_path)
    if pr is None:
        self.is_valid = False
        return
    if pr.graph[-1].type == 'path':
        setattr(pr.id.path_resolve(pr.path) if pr.path else pr.id, pr.prop, self.dummy)
    elif pr.graph[-1].type == 'int':
        getattr(pr.id.path_resolve(pr.path) if pr.path else pr.id, pr.prop)[pr.array_index] = self.dummy
    self.is_valid = True

def create_anim_propcopy(name: str, property: bpy.types.Property, cb: Callable[[Any, bpy.types.Context], None]) -> Union[VirtualDriverDummy, None]:
    prop = copy_anim_property(property, cb)
    if prop is None:
        return
    return type(
        name,
        (bpy.types.PropertyGroup, VirtualDriverDummy, ),
        {
            '__annotations__': {
                'name': bpy.props.StringProperty(default=name),
                # 'property': prop,
            },
        },
    )
