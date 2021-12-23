from typing import Any, Literal, Union
from dataclasses import dataclass
import bpy

@dataclass
class EvalDisassemblyItem:
    type: Union[Literal['path'], Literal['int'], Literal['str']]
    path: Union[str, int]

@dataclass
class DisassemblyItem:
    type: Union[Literal['path'], Literal['int'], Literal['str'], Literal['eval']]
    path: Union[str, int, EvalDisassemblyItem]

@dataclass
class AssemblyItem:
    prop: Union[bpy.types.Property, None]
    prna: str
    eval: Any
    path: Union[str, int, None]
    type: Union[Literal['id'], Literal['path'], Literal['int'], Literal['str'], Literal['eval']]

def path_disassembly(path: str) -> list[DisassemblyItem]:
    tmp = ''
    res = []
    sid = -1
    for i, s in enumerate(path):
        if sid != -1 and sid != i:
            continue
        sid = -1
        if s == '[':
            res.append({'path': tmp})
            r, tmp = path_disassembly(path[i+1:])
            sid = r+i
            if len(tmp) > 1:
                res.append({'eval': tmp})
            else:
                res.append(tmp[0])
            tmp = ''
        elif s == '.':
            if tmp:
                res.append({'path': tmp})
            tmp = ''
        elif s == '"':
            idx = path.find('"', i+1)
            res.append({'str': path[i:idx+1]})
            sid = idx+1
            tmp = ''
        elif s == ']':
            if tmp.isdigit():
                res.append({'int': int(tmp)})
            elif tmp:
                res.append({'path': tmp})
            return i+2, res
        else:
            tmp += s
    if tmp:
        res.append({'path': tmp})
    return res

def path_assembly(id: bpy.types.ID, path: list[DisassemblyItem], resolve=True) -> list[AssemblyItem]:
    res = [{
        'prop': None,
        'prna': '',
        'eval': id,
        'path': None,
        'type': 'id'
    }]
    tmp = id
    stmp = ''
    for i, p in enumerate(path):
        if p.type == 'path':
            e = p.path
            ev = ('' if i == 0 else '.')+e
        elif p.type in ('int', 'str'):
            e = p.path
            ev = '['+str(e)+']'
        else:
            e = eval(path_assembly(id, p.path, False)[-1].prna)
            ev = '['+str(e)+']'
        prop = None
        stmp = stmp+ev
        if resolve:
            try:
                prop = tmp.bl_rna.properties[e]
            except Exception as _:
                prop = None
            tmp = id.path_resolve(stmp)
        res.append({
            'prop': prop,
            'prna': stmp,
            'eval': tmp,
            'path': e,
            'type': p[0]
        })
    return res

def animatable(id: bpy.types.ID, path: str):
    if not isinstance(id, bpy.types.ID) or path == '':
        return
    
    try:
        pd = path_disassembly(path)
        graph = path_assembly(id, pd)
    except Exception as _:
        return
    
    prop = graph[-1].prop
    if prop is None:
        prop = graph[-2].prop
    if isinstance(prop, bpy.types.Property):
        if not prop.is_animatable:
            return
        if prop.is_readonly:
            return
        if prop.type in ('BOOL', 'INT', 'FLOAT'):
            if prop.is_array:
                if graph[-1].path
