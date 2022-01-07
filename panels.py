import bpy
from . import property_tracer
from .properties import InternalVirtualDriver, VirtualDriver, VirtualDriverIndex

class OBJECT_UL_VirtualDriver(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, 'name', icon='ANIM', text='', emboss=False)
            row.prop(item, 'mute', icon='CHECKBOX_HLT' if not item.mute else 'CHECKBOX_DEHLT', text='', emboss=False)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='', icon=icon)

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
        pt: VirtualDriver = scene.virtual_driver
        ipt: list[InternalVirtualDriver] = scene.internal_virtual_driver
        index: int = scene.active_virtual_driver_index

        layout.template_list(OBJECT_UL_VirtualDriver.__name__, '', scene, InternalVirtualDriver.identifier, scene, VirtualDriverIndex.identifier, rows=3)

        if not ipt or index < 0:
            return

        block = ipt[index]

        box = layout.box().column()
        box.template_any_ID(pt, 'id', 'id_type', text='Prop:')
        box.template_path_builder(pt, 'data_path', pt.id, text='Path')

        if pt.is_valid:
            box.prop(pt, 'prop')
