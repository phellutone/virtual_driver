
from typing import Literal
import bpy
from . import property_tracer

class VirtualDriver(property_tracer.PropertyTracer):
    identifier: Literal['virtual_driver'] = 'virtual_driver'
    mute: bpy.props.BoolProperty()

class InternalVirtualDriver(property_tracer.InternalPropTrace):
    identifier: Literal['internal_virtual_driver'] = 'internal_virtual_driver'
    mute: bpy.props.BoolProperty()

class VirtualDriverIndex(property_tracer.InternalPropTraceIndex):
    identifier: Literal['active_virtual_driver_index'] = 'active_virtual_driver_index'
