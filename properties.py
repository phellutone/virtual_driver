import bpy
from .utils import animatable

class FCurveWrapper(bpy.types.PropertyGroup):
    id: bpy.props.PointerProperty(type=bpy.types.ID)
    data_path: bpy.props.StringProperty()
    array_index: bpy.props.IntProperty()

class VirtualDriver(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    index: bpy.props.IntProperty()
    dummy: None
    fcurve: bpy.props.PointerProperty(type=FCurveWrapper)

