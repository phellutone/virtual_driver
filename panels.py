import bpy
from . import property_tracer
from .properties import VirtualDriver

class OBJECT_PT_VirtualDriver(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_idname = 'VIEW3D_PT_virtual_driever'
    bl_label = 'Virtual Driver'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        vd: VirtualDriver = scene.virtual_driver
        pt: property_tracer.PropertyTracer = vd.property_tracer

        box = layout.box().column()
        box.template_any_ID(pt, 'id', 'id_type', text='Prop:')
        box.template_path_builder(pt, 'data_path', pt.id, text='Path')

        if pt.is_valid:
            box.prop(pt, 'prop')
