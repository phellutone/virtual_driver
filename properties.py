from typing import Any, Callable, Union
import bpy
from .utils import copy_anim_property, path_reassembly, animatable

class VirtualDriverDummy:
    name: str
    prop: Any
    is_valid: bool
    id: bpy.types.ID
    data_path: str

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
    id_type: bpy.props.EnumProperty(
        items=[
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
        ],
        name='ID Type',
        description='Type of ID-block that can be used',
        default='OBJECT',

        # update=id_type_update
    )

    id: bpy.props.PointerProperty(
        name='ID-Block',
        description='',
        options=set(),
        type=bpy.types.ID
    )
    
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
        oldtype: Union[VirtualDriverDummy, bpy.types.PropertyGroup] = self.dummy.__class__
        bpy.utils.register_class(proptype)
        self.__class__.dummy = bpy.props.PointerProperty(type=proptype)
        dummy: VirtualDriverDummy = self.dummy
        dummy.name = str(self.id.name)+'.'+self.data_path
        dummy.id = self.id
        dummy.data_path = self.data_path
        dummy.prop = self.id.path_resolve(self.data_path)
        dummy.is_valid = True
        if VirtualDriverDummy in oldtype.__mro__:
            bpy.utils.unregister_class(oldtype)
            _VIRTUALDRIVER_DUMMY_CLASSES.remove(oldtype)

        self.is_valid = True
    data_path: bpy.props.StringProperty(update=data_path_update)

def dummy_update(self: VirtualDriverDummy, context):
    if not self.is_valid:
        return
    pr = path_reassembly(self.id, self.data_path)
    if pr is None:
        self.is_valid = False
        return
    if pr.graph[-1].type == 'path':
        setattr(pr.id.path_resolve(pr.path) if pr.path else pr.id, pr.prop, self.prop)
    elif pr.graph[-1].type == 'int':
        (pr.id.path_resolve(pr.path) if pr.path else pr.id).path_resolve(pr.prop)[pr.array_index] = self.prop
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
                'prop': prop,
                'is_valid': bpy.props.BoolProperty(),
                'id': bpy.props.PointerProperty(type=bpy.types.ID),
                'data_path': bpy.props.StringProperty()
            },
        },
    )
