import bpy
from .properties import VirtualDriver

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
    
    
