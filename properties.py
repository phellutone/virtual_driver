
from typing import Literal
import bpy

class VirtualDriver(bpy.types.PropertyGroup):
    identifier: Literal['virtual_driver'] = 'virtual_driver'

class VirtualDriverIndex:
    identifier: Literal['active_virtual_driver_index'] = 'active_virtual_driver_index'
