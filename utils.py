
from dataclasses import dataclass
import re
from typing import Any, Callable, Literal, Pattern, Union
import bpy



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
class Interpretation:
    id: bpy.types.ID
    rna_path: str
    prop_path: str
    array_index: Union[int, None]
    prop: bpy.types.Property


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

def path_recognize(id: bpy.types.ID, path: str) -> Union[Interpretation, None]:
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

    rgraph = graph[::-1]
    for i, item in enumerate(rgraph):
        if item.prop is None:
            continue

        array_index = None
        idx = [g for g in rgraph[:i]]
        if idx:
            if len(idx) > 1:
                raise Exception('not supported')
            else:
                array_index = idx[0].path

        return Interpretation(
            id,
            rgraph[i+1].prna if len(rgraph) > i+1 else '',
            item.path,
            array_index,
            item.prop
        )

def animatable(id: bpy.types.ID, path: str) -> Union[Interpretation, None]:
    pr = path_recognize(id, path)
    if pr is None:
        return

    if not pr.prop.is_animatable:
        return
    if pr.prop.is_readonly:
        return
    if pr.prop.type in ('COLLECTION', 'POINT'):
        return
    if pr.prop.type in ('BOOLEAN', 'INT', 'FLOAT'):
        if pr.prop.is_array and pr.array_index is None:
            return
    return pr

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
