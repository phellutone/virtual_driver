from typing import Any, Callable, Literal, Pattern, Union
from dataclasses import dataclass
import re
import bpy

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

_PROPTRACE_RE_PATH_DISASSEMBLY: Pattern = re.compile(r'''(\[(?:(?P<str>".*?(?<!\\)")|(?P<int>\d+))\])|(?(1)|(?P<path>\w+))''')

def path_disassembly(path: str) -> list[DisassemblyItem]:
    res = _PROPTRACE_RE_PATH_DISASSEMBLY.finditer(path)
    result = []
    for r in res:
        if r.group('int'):
            result.append(DisassemblyItem('int', int(r.group('int'))))
        if r.group('str'):
            result.append(DisassemblyItem('str', r.group('str')))
        if r.group('path'):
            result.append(DisassemblyItem('path', r.group('path')))
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
        elif p.type == 'eval':
            return []
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
            return Reassembly(id, g3.prna if g3 else '', g2.path, 0, graph)
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



class _PropTrace:
    name: str
    index: int
    id: bpy.types.ID
    data_path: str
    is_valid: bool
    prop: Any

class _PropTrace_0(bpy.types.PropertyGroup, _PropTrace):
    id: bpy.props.PointerProperty(type=bpy.types.ID)
    data_path: bpy.props.StringProperty()

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

def create_proptype(identifier: str, props: dict[str, bpy.props._PropertyDeferred]) -> _PropTrace:
    return type(
        identifier,
        (bpy.types.PropertyGroup, _PropTrace,),
        {
            '__annotations__': props
        },
    )

class PropTraceItem(bpy.types.PropertyGroup):
    def __init__(self) -> None:
        self._i = 0
        self._l: list[tuple[str, _PropTrace]] = []
    
    def __iter__(self):
        return self
    
    def __next__(self) -> _PropTrace:
        try:
            v = self._l[self._i][1]
            self._i += 1
            return v
        except IndexError:
            raise StopIteration
    
    def add(self, identifier: str, id: bpy.types.ID, data_path: str):
        anim = animatable(id, data_path)
        if anim is None:
            return
        _, _, _, prop = anim
        proptype = create_proptype(identifier, {
            'name': bpy.props.StringProperty(default=identifier),
            'index': bpy.props.IntProperty(),
            'id': bpy.props.PointerProperty(),
            'data_path': bpy.props.StringProperty(),
            'is_valid': bpy.props.BoolProperty(),
            'prop': copy_anim_property(prop, None)
        })
        self._l.append((identifier, proptype))
        pointer = bpy.props.PointerProperty(type=proptype)
        bpy.utils.register_class(proptype)
        setattr(PropTraceItem, identifier, pointer)

    def remove(self, identifier: str):
        proptypes = [i[1] for i in self._l if i[0] == identifier]
        if not proptypes:
            return
        self._l = [i for i in self._l if not i[0] == identifier]
        proptype = proptypes[0]
        bpy.utils.unregister_class(proptype)
        delattr(PropTraceItem, identifier)
    
class PropertyTracer(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    index: bpy.props.IntProperty()
    id_type: bpy.props.IntProperty()
    id: bpy.props.PointerProperty(type=bpy.types.ID)
    data_path: bpy.props.StringProperty()

    prop_type: bpy.props.StringProperty()
    prop: bpy.props.FloatProperty()
