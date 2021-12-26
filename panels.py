import bpy
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

        box = layout.box().column()
        box.template_any_ID(vd, 'id', 'id_type', text='Prop:')
        box.template_path_builder(vd, 'data_path', vd.id, text='Path')

        if vd.is_valid:
            box.prop(vd.dummy, 'prop')
