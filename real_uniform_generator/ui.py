from __future__ import annotations

from bpy.types import Panel


class RUG_PT_main(Panel):
    bl_label = 'Real Uniform Generator'
    bl_idname = 'RUG_PT_main'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '制服'

    def draw(self, context):
        layout = self.layout
        s = context.scene.rug_settings
        box = layout.box()
        box.label(text='標準寸法')
        for prop in ('waist_circumference', 'hip_circumference', 'skirt_length', 'hip_line', 'hem_ease'):
            box.prop(s, prop)
        box = layout.box()
        box.label(text='プリーツ・縫製')
        for prop in ('pleat_count', 'pleat_depth', 'pleat_stitch_length', 'pleat_release_length', 'fabric_thickness', 'hem_turnup', 'waistband_height'):
            box.prop(s, prop)
        box.prop(s, 'create_lining')
        if s.create_lining:
            box.prop(s, 'lining_length')
        box.prop(s, 'zipper_length')
        box.prop(s, 'zipper_position')
        box = layout.box()
        box.label(text='PBR生地')
        box.prop(s, 'use_external_pbr')
        if s.use_external_pbr:
            box.prop(s, 'texture_directory')
            box.prop(s, 'normal_format')
            box.prop(s, 'pack_external_textures')
            box.operator('rug.scan_pbr')
        box.prop(s, 'texture_tile_cm')
        box.prop(s, 'weave_size_cm')
        row = box.row(align=True)
        row.prop(s, 'normal_strength')
        row.prop(s, 'height_strength')
        box.prop(s, 'ao_strength')
        layout.operator('rug.generate_skirt', icon='MOD_CLOTH')
        row = layout.row(align=True)
        row.operator('rug.prepare_preview', icon='CAMERA_DATA')
        row.operator('rug.clear_preview')
        layout.operator('rug.render_front', icon='RENDER_STILL')
        box = layout.box()
        box.label(text='出力')
        box.prop(s, 'output_directory')
        box.prop(s, 'export_format')
        box.prop(s, 'apply_modifiers')
        box.operator('rug.export_skirt', icon='EXPORT')
        box.operator('rug.save_blend_copy', icon='FILE_BLEND')
        layout.operator('rug.delete_skirt', icon='TRASH')


CLASSES = (RUG_PT_main,)
