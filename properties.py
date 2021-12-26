from typing import Union
import bpy
from .utils import path_reassembly, animatable

class FCurveWrapper(bpy.types.PropertyGroup):
    id: bpy.props.PointerProperty(type=bpy.types.ID)
    data_path: bpy.props.StringProperty()
    anim_index: bpy.props.IntProperty()

    def path_observer(self):
        if not hasattr(self.id, 'animation_data'):
            return 
        if not self.id.animation_data:
            return
        fixes = [i for i, f in enumerate(self.id.animation_data.drivers) if f.data_path == self.data_path]
        if not fixes:
            return
        if len(fixes) > 1:
            return
        return fixes[0]

    def init():
        ...

class VirtualDriver(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    index: bpy.props.IntProperty()
    is_valid: bpy.props.BoolProperty()
    fcurve: bpy.props.PointerProperty(type=FCurveWrapper)

    def dummy_update(self, context):
        pr = path_reassembly(self.id, self.data_path)
        if pr is None:
            self.is_valid = False
            return
        if pr.graph[-1].type == 'path':
            setattr(pr.id.path_resolve(pr.path) if pr.path else pr.id, pr.prop, self.dummy)
        elif pr.graph[-1].type == 'int':
            getattr(pr.id.path_resolve(pr.path) if pr.path else pr.id, pr.prop)[pr.array_index] = self.dummy
    dummy: bpy.props.FloatProperty()

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
        anim = animatable(self.id, self.data_path)
        if anim is None:
            self.dummy = None
            self.is_valid = False
            return
        id, data_path, array_index, property = anim

        property = self.copy_anim_property(property)
        if property is None:
            self.is_valid = False
            return
        self.__class__.dummy = property

        fcurve: FCurveWrapper = self.fcurve
        fcurve.id = self.id_data
        fcurve.data_path = self.path_from_id('dummy')

    data_path: bpy.props.StringProperty(update=data_path_update)

    def copy_anim_property(self, property: bpy.types.Property) -> Union[bpy.props._PropertyDeferred, None]:
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
        tags = property.tags
        subtype = property.subtype

        if property.is_argument_optional: ...
        if property.is_never_none: ...
        if property.is_output: ...
        if property.is_readonly: ...
        if property.is_registered: ...
        if property.is_registered_optional: ...
        if property.is_required: ...
        if property.is_runtime: ...
        property.unit
        property.translation_context
        
        if property.type == 'BOOLEAN':
            if property.is_array:
                default = property.default_array
                size = property.array_length
                return bpy.props.BoolProperty(
                    name=name,
                    description=description,
                    options=options,
                    override=override,
                    tags=tags,
                    subtype=subtype,
                    default=default,
                    size=size,
                    update=self.dummy_update
                )
            else:
                default = property.default
                return bpy.props.BoolProperty(
                    name=name,
                    description=description,
                    options=options,
                    override=override,
                    tags=tags,
                    subtype=subtype,
                    default=default,
                    update=self.dummy_update
                )

        if property.type == 'INT':
            min = property.hard_min
            max = property.hard_max
            soft_min = property.soft_min
            soft_max = property.soft_max
            step = property.step
            if property.is_array:
                default = property.default_array
                size = property.array_length
                return bpy.props.IntProperty(
                    name=name,
                    description=description,
                    options=options,
                    override=override,
                    tags=tags,
                    subtype=subtype,
                    default=default,
                    size=size,
                    min=min,
                    max=max,
                    soft_min=soft_min,
                    soft_max=soft_max,
                    step=step,
                    update=self.dummy_update
                )
            else:
                default = property.default
                return bpy.props.IntProperty(
                    name=name,
                    description=description,
                    options=options,
                    override=override,
                    tags=tags,
                    subtype=subtype,
                    default=default,
                    min=min,
                    max=max,
                    soft_min=soft_min,
                    soft_max=soft_max,
                    step=step,
                    update=self.dummy_update
                )
            
        if property.type == 'FLOAT':
            min = property.hard_min
            max = property.hard_max
            soft_min = property.soft_min
            soft_max = property.soft_max
            step = property.step
            precision = property.precision
            if property.is_array:
                default = property.default_array
                size = property.array_length
                return bpy.props.FloatProperty(
                    name=name,
                    description=description,
                    options=options,
                    override=override,
                    tags=tags,
                    subtype=subtype,
                    default=default,
                    size=size,
                    min=min,
                    max=max,
                    soft_min=soft_min,
                    soft_max=soft_max,
                    step=step,
                    precision=precision,
                    update=self.dummy_update
                )
            else:
                default = property.default
                return bpy.props.FloatProperty(
                    name=name,
                    description=description,
                    options=options,
                    override=override,
                    tags=tags,
                    subtype=subtype,
                    default=default,
                    min=min,
                    max=max,
                    soft_min=soft_min,
                    soft_max=soft_max,
                    step=step,
                    precision=precision,
                    update=self.dummy_update
                )
        
        if property.type == 'ENUM':
            items = property.enum_items
            if property.is_enum_flag:
                options.add('ENUM_FLAG')
                default = property.default_flag
                return bpy.props.EnumProperty(
                    name=name,
                    description=description,
                    options=options,
                    override=override,
                    tags=tags,
                    subtype=subtype,
                    default=default,
                    items=items,
                    update=self.dummy_update
                )
            else:
                default = property.default
                return bpy.props.EnumProperty(
                    name=name,
                    description=description,
                    options=options,
                    override=override,
                    tags=tags,
                    subtype=subtype,
                    default=default,
                    items=items,
                    update=self.dummy_update
                )
