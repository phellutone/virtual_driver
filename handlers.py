import bpy
from .properties import VirtualDriver
from .utils import path_reassembly

_VIRTUALDRIVER_UPDATE_LOCK = False

def virtual_driver_update(scene, depsgraph):
    global _VIRTUALDRIVER_UPDATE_LOCK
    if _VIRTUALDRIVER_UPDATE_LOCK:
        return
    
    _VIRTUALDRIVER_UPDATE_LOCK = True
    
    vd: VirtualDriver = scene.virtual_driver
    index: int = scene.active_virtual_driver_index
    if not vd or index < 0:
        return
    
    if vd.is_valid:
        pr = path_reassembly(vd.id, vd.data_path)
        if pr is None:
            vd.is_valid = False
            return
        if pr.graph[-1].type == 'path':
            setattr(pr.id.path_resolve(pr.path) if pr.path else pr.id, pr.prop, vd.dummy.prop)
        elif pr.graph[-1].type == 'int':
            (pr.id.path_resolve(pr.path) if pr.path else pr.id).path_resolve(pr.prop)[pr.array_index] = vd.dummy.prop
    
    _VIRTUALDRIVER_UPDATE_LOCK = False
