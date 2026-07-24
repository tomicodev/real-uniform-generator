import bpy
from bpy.types import Panel


class RUG_PT_main(Panel):
    bl_label = 'Real Uniform Generator'
    bl_idname = 'RUG_PT_main'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Uniform'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.rug_settings

        box = layout.box()
        box.label(text='シルエット', icon='MESH_DATA')
        box.prop(settings, 'pleat_count')
        box.prop(settings, 'skirt_length')
        row = box.row(align=True)
        row.prop(settings, 'waist_width')
        row.prop(settings, 'waist_depth')
        row = box.row(align=True)
        row.prop(settings, 'hem_width')
        row.prop(settings, 'hem_depth')
        box.prop(settings, 'back_drop')
        box.prop(settings, 'wrinkle_strength')

        box = layout.box()
        box.label(text='プリーツ・縫製', icon='MOD_CLOTH')
        box.prop(settings, 'pleat_depth')
        box.prop(settings, 'pleat_stitch_length')
        box.prop(settings, 'fabric_thickness')
        box.prop(settings, 'waistband_height')
        box.prop(settings, 'waistband_overlap')
        box.prop(settings, 'vertical_segments')
        box.prop(settings, 'create_stitches')
        box.prop(settings, 'create_lining')
        if settings.create_lining:
            box.prop(settings, 'lining_length_ratio')
        box.prop(settings, 'create_hardware')

        box = layout.box()
        box.label(text='生地・PBR', icon='MATERIAL')
        box.prop(settings, 'fabric')
        box.prop(settings, 'weave_scale')
        box.prop(settings, 'weave_strength')
        box.prop(settings, 'texture_resolution')
        box.label(text='生成時にBase/Roughness/Normalを作成', icon='INFO')

        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator('rug.generate_skirt', icon='OUTLINER_OB_MESH')
        row.operator('rug.delete_skirt', text='', icon='TRASH')

        box = layout.box()
        box.label(text='質感確認', icon='RENDER_STILL')
        row = box.row(align=True)
        row.operator('rug.prepare_preview', icon='LIGHT_AREA')
        row.operator('rug.clear_preview', text='', icon='X')
        box.operator('rug.render_preview', icon='IMAGE_DATA')

        box = layout.box()
        box.label(text='保存・書き出し', icon='EXPORT')
        box.operator('rug.save_blend_copy', icon='FILE_BLEND')
        box.separator()
        box.prop(settings, 'export_format')
        box.prop(settings, 'apply_modifiers')
        box.prop(settings, 'export_lining')
        box.prop(settings, 'export_hardware')
        box.operator('rug.export_skirt', icon='FILE_TICK')


CLASSES = (RUG_PT_main,)
