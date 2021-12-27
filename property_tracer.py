from typing import Any, Callable, Literal, Union
from dataclasses import dataclass
import bpy

@dataclass
class DisassemblyItem:
    type: Union[Literal['path'], Literal['int'], Literal['str'], Literal['eval']]
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
    tmp = ''
    res = []
    sid = -1
    for i, s in enumerate(path):
        if sid != -1 and sid != i:
            continue
        sid = -1
        if s == '[':
            res.append(DisassemblyItem('path', tmp))
            r, tmp = path_disassembly(path[i+1:])
            sid = r+i
            if len(tmp) > 1:
                res.append(DisassemblyItem('eval', None))
            else:
                res.append(tmp[0])
            tmp = ''
        elif s == '.':
            if tmp:
                res.append(DisassemblyItem('path', tmp))
            tmp = ''
        elif s == '"':
            idx = path.find('"', i+1)
            res.append(DisassemblyItem('str', path[i:idx+1]))
            sid = idx+1
            tmp = ''
        elif s == ']':
            if tmp.isdigit():
                res.append(DisassemblyItem('int', int(tmp)))
            elif tmp:
                res.append(DisassemblyItem('path', tmp))
            return i+2, res
        else:
            tmp += s
    if tmp:
        res.append(DisassemblyItem('path', tmp))
    return res

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
    if g1.type == 'path':
        return Reassembly(id, g2.prna, g1.path, 0, graph)
    return

def animatable(id: bpy.types.ID, path: str) -> Union[tuple[bpy.types.ID, str, int, bpy.types.Property], None]:
    pr = path_reassembly(id, path)
    if pr is None:
        return

    graph = pr.graph    
    prop = graph[-1].prop

    if prop is None:
        prop = graph[-2].prop
    if isinstance(prop, bpy.types.Property):
        if not prop.is_animatable:
            return
        if prop.is_readonly:
            return
        if prop.type in ('BOOLEAN', 'INT', 'FLOAT'):
            if prop.is_array:
                if graph[-1].type == 'int':
                    return (pr.id, pr.path+'.'+pr.prop, pr.array_index, prop)
                else:
                    return
        return (pr.id, pr.path+'.'+pr.prop, pr.array_index, prop)
    return

class _PropTrace:
    name: str
    index: int
    id: bpy.types.ID
    data_path: str
    is_valid: bool
    prop: Any

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
        default = property.default
        return bpy.props.BoolProperty(
            name=name,
            description=description,
            options=options,
            override=override,
            default=default,
            update=cb
        )

    if property.type == 'INT':
        min = property.hard_min
        max = property.hard_max
        soft_min = property.soft_min
        soft_max = property.soft_max
        step = property.step
        default = property.default
        return bpy.props.IntProperty(
            name=name,
            description=description,
            options=options,
            override=override,
            default=default,
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
        default = property.default
        return bpy.props.FloatProperty(
            name=name,
            description=description,
            options=options,
            override=override,
            default=default,
            min=min,
            max=max,
            soft_min=soft_min,
            soft_max=soft_max,
            step=step,
            precision=precision,
            update=cb
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
                default=default,
                items=items,
                update=cb
            )
        else:
            default = property.default
            return bpy.props.EnumProperty(
                name=name,
                description=description,
                options=options,
                override=override,
                default=default,
                items=items,
                update=cb
            )

def create_proptype(name: str, property: bpy.types.Property, cb: Callable[[Any, bpy.types.Context], None]) -> Union[_PropTrace, None]:
    prop = copy_anim_property(property, cb)
    if prop is None:
        return
    return type(
        name,
        (bpy.types.PropertyGroup, _PropTrace, ),
        {
            '__annotations__': {
                'name': bpy.props.StringProperty(default=name),
                'index': bpy.props.IntProperty(),
                'id': bpy.props.PointerProperty(type=bpy.types.ID),
                'data_path': bpy.props.StringProperty(),
                'is_valid': bpy.props.BoolProperty(),
                'prop': prop,
            },
        },
    )

class PropTraceItem(bpy.types.PropertyGroup): ...

class PropertyTracer(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
