from typing import Any, Literal, Union, get_args
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
        if g1.type == 'str':
            return Reassembly(id, g3.prna if g3 else '', g2.path+'['+g1.path+']', 0, graph)
    if g1.type == 'path':
        return Reassembly(id, g2.prna, g1.path, 0, graph)
    return

def animatable(id: bpy.types.ID, path: str) -> Union[tuple[bpy.types.ID, str, int], None]:
    pr = path_reassembly(id, path)
    if not pr:
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
        if prop.type in ('BOOL', 'INT', 'FLOAT'):
            if prop.is_array:
                if graph[-1].type == 'int':
                    return (pr.id, pr.path+'.'+pr.prop, pr.array_index)
                else:
                    return
        return (pr.id, pr.path+'.'+pr.prop, pr.array_index)
    return

def panelprop(id: bpy.types.ID, path: str) -> Union[tuple[str, str], None]:
    pr = path_reassembly(id, path)
    if not pr:
        return

    try:
        path = pr.id.path_resolve(pr.path)
    except Exception as _:
        return
    
    return (path, pr.prop)
